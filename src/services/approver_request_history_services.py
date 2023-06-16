from typing import Union, List, Any, Optional, OrderedDict

from sqlalchemy.ext.asyncio import AsyncConnection

from repositories.mysql_db.models.approval_step import ApprovalStep
from repositories.mysql_db.models.approver_request_history import ApproverRequestHistory
from external_api_clients import V2APIClient
from repositories.mysql_db.implementation import ApproverRequestHistoryRepository
from utils.constant import PARAMS, USER_TYPE, APPROVAL_STATES, SEPERATORS


class ApproverRequestHistoryServices:

    def __init__(self):
        self.__approver_request_history_repository = ApproverRequestHistoryRepository()
        self.__v2_api_client = V2APIClient()

    def create_approver_username_id_map(self, user_type, ids, ug_id, external_id_user_name_map):
        if user_type == USER_TYPE.SM_USER:
            params_str = ""
            for index, value in enumerate(ids):
                params_str += 'user_ids[{}]={}&'.format(index, value)
            params_str += PARAMS.USER_GROUP_PARAM + "=" + str(ug_id)
            user_data = self.__v2_api_client.get_sm_users_data(params_str)

            for user in user_data["userDetails"]:
                key = user_type + SEPERATORS.DOUBLE_COLON + str(user["id"])
                if key not in external_id_user_name_map:
                    external_id_user_name_map[key] = user["name"] if user["name"] else user["email"]

        else:
            ids = [str(id_) for id_ in ids]
            params_str = PARAMS.COLLABORATOR_PARAMS + '=' + ','.join(ids)
            collaborators_data = self.__v2_api_client.get_collaborators_emails(params_str)
            for collaborator in collaborators_data:
                key = user_type + SEPERATORS.DOUBLE_COLON + str(collaborator["id"])
                if key not in external_id_user_name_map:
                    external_id_user_name_map[key] = collaborator["emailid"]

    @staticmethod
    def create_id_username_map(approvers_details, external_id_and_type_map):
        if approvers_details:
            approver_details = approvers_details.split(",")
            for instance in approver_details:
                [key, value] = instance.split(SEPERATORS.DOUBLE_COLON)
                value = int(value)
                if key not in external_id_and_type_map:
                    external_id_and_type_map[key] = {value}
                else:
                    external_id_and_type_map[key].add(value)

    @staticmethod
    def construct_user_identifier_string(user_type, id):
        return user_type + SEPERATORS.DOUBLE_COLON + str(id)

    @staticmethod
    def update_approver_action_info(table, id, action_details, approver_action_info):
        unique_step_id = table + "_id_" + str(id)
        if unique_step_id not in approver_action_info:
            approver_action_info[unique_step_id] = []
        else:
            action_details["userDetails"] = approver_action_info[unique_step_id]["userDetails"] + SEPERATORS.COMMA + action_details["userDetails"]
        approver_action_info[unique_step_id] = action_details

    @staticmethod
    def create_approval_action_object(row_data, table, approver_action_info, external_id_and_type_map,
                                      last_cancellation_record_id):
        for record in row_data:
            approval_action = {}
            for key in record.keys():
                approval_action[key] = record[key]

            approval_action["isCancelled"] = last_cancellation_record_id >= record.id

            if approval_action["status"] in [APPROVAL_STATES.CANCELLED, APPROVAL_STATES.INITIATED]:
                user_details = ApproverRequestHistoryServices.construct_user_identifier_string(USER_TYPE.SM_USER, approval_action["createdBy"])
            else:
                user_details = ApproverRequestHistoryServices.construct_user_identifier_string(approval_action["approverType"], approval_action["approverExternalId"])
            approval_action["userDetails"] = user_details
            id = record["id"] if table == ApproverRequestHistory.name else record["stepId"]
            ApproverRequestHistoryServices.update_approver_action_info(table, id, approval_action, approver_action_info)
            ApproverRequestHistoryServices.create_id_username_map(approval_action["userDetails"], external_id_and_type_map)

    @staticmethod
    def get_last_cancellation_record_id(approval_history: List) -> int:
        # An approval request can go through multiple approval flows when it gets cancelled and reinitiated
        # For ex:
        # 1. initiated with flow1 with 3 steps
        # 2. approved by step1
        # 3. approved by step2
        # 4. cancelled before step3 approval
        # 5. re-initiated with flow2 with 2 steps
        # 6. cancelled before step1 approval
        # 7. re-initiated with flow3 with 1 step
        # 8. approved by step1
        # In such a scenario, we'll get the status of steps 1, 2, 3 and 5 as initiated/approved. However, the request
        # itself was later cancelled, rendering the "approved"/"initiated" status meaningless. Their "true" status is
        # now cancelled.
        # In order to show the same on the UI, we need to mark every history record BEFORE the last
        # cancellation as "cancelled". Thus, we're reversing the history to find the latest cancellation record, which
        # will later be used to modify the history records in-memory (not in the DB).

        reversed_approval_history = approval_history[::-1]
        for record in reversed_approval_history:
            if record.status == APPROVAL_STATES.CANCELLED:
                return record.id
        # When the approval request was never cancelled
        return -1

    async def fetch_approver_history_details(self,
                                             conn: AsyncConnection,
                                             approval_request_info: dict,
                                             user_group_id: int,
                                             approver_external_id: int,
                                             approver_type: int,
                                             should_remove_flow_name: Optional[bool] = None) -> List[Union[dict, Any]]:
        approver_history = (
            await self.__approver_request_history_repository.fetch_approver_history(
                conn=conn, approval_request_ids=[approval_request_info["approvalRequestId"]]
            )
        )

        approver_action_info = {}
        external_id_and_type_map = {}

        # Default assumption that the requestor is the same as the current user, thus the "you" substitution
        external_id_user_name_map = {
            approver_type + SEPERATORS.DOUBLE_COLON + str(approver_external_id): "You"
        }

        last_cancellation_record_id = self.get_last_cancellation_record_id(approval_history=approver_history)
        ApproverRequestHistoryServices.create_approval_action_object(approver_history, ApproverRequestHistory.name,
                                                                     approver_action_info, external_id_and_type_map,
                                                                     last_cancellation_record_id)

        approver_timeline_list = (
            await self.__approver_request_history_repository.fetch_approver_timeline(
                conn=conn, approval_request_id=approval_request_info["approvalRequestId"]
            )
        )

        ApproverRequestHistoryServices.create_approval_action_object(approver_timeline_list, ApprovalStep.name,
                                                                     approver_action_info, external_id_and_type_map, -1)

        for key, value in external_id_and_type_map.items():
            self.create_approver_username_id_map(key, value, user_group_id, external_id_user_name_map)

        # convert the above dict to list so that it can be sent to front end as per API contract
        approver_action_info = [v for k, v in approver_action_info.items()]

        for index, value in enumerate(approver_action_info):
            approver = approver_action_info[index]["userDetails"].split(",")
            status = []
            for id_type in approver:
                if id_type in external_id_user_name_map:
                    if len(external_id_user_name_map[id_type]) > 20:
                        status.append(external_id_user_name_map[id_type][:20 - 3] + "...")
                    else:
                        status.append(external_id_user_name_map[id_type])
                else:
                    status.append(id_type)
            status = list(set(status))
            str_status = ""
            current_status = approver_action_info[index]["status"]
            if current_status == APPROVAL_STATES.IDLE:
                str_status += " or ".join(status) + " to Approve"
            elif current_status in [APPROVAL_STATES.APPROVED, APPROVAL_STATES.CANCELLED]:
                str_status += current_status.title() + " by " + " or ".join(status) + \
                              '<br/>' + approver_action_info[index]["createdAt"].strftime("%B %d, %Y")
            elif current_status == APPROVAL_STATES.CANCELLED:
                str_status += "Cancelled by " + " or ".join(status) + "<br/>" + approver_action_info[index][
                    "createdAt"].strftime("%B %d, %Y")
            elif current_status == APPROVAL_STATES.REJECTED:
                rejection_reason = str(approver_action_info[index]["note"] or "")
                str_status += "Rejected by " + " or ".join(status) + '<br/>' + approver_action_info[index][
                    "createdAt"].strftime("%B %d, %Y") + '<br/>Reason : ' + approver_action_info[index][
                                  "reason"]
                if rejection_reason:
                    str_status += '<br/>Notes : ' + str(approver_action_info[index]["note"] or "")
            elif current_status == APPROVAL_STATES.INITIATED:
                str_status = " or ".join(status) + " requested "
                if not should_remove_flow_name:
                    str_status += approval_request_info["name"]
                str_status += " Approval" + '<br/>' + approver_action_info[index]["createdAt"].strftime("%B %d, %Y")
            approver_action_info[index]["statusDetails"] = str_status

            del approver_action_info[index]["userDetails"]

        return approver_action_info

    async def fetch_history_records(self, *, conn: AsyncConnection, approval_request_ids: List[int]) -> List:
        return await self.__approver_request_history_repository.\
            fetch_approver_history(conn=conn, approval_request_ids=approval_request_ids)
