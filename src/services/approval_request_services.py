import json
from typing import Dict, Optional, Union, List

from sqlalchemy.ext.asyncio import AsyncConnection

from dtos.request.approvals import CreateApprovalRequest, ProcessApprovalRequest
from dtos.response.entities import ApprovalRequestDetailResponse
from exceptions.errors import InvalidArgumentError
from messaging_processor.producer import event_producer
from repositories.mysql_db.implementation import (
    ApprovalRequestRepository,
    ApprovalStepRepository,
    ApproverRequestHistoryRepository,
    ApprovalFlowRepository
)
from utils.constant import APPROVAL_STATES, ProducerTopic, NotificationActionType
from utils.constants import SERVICE
from external_api_clients import V2APIClient
from utils.initialize_common_utils import common_utils_ins


class ApprovalRequestServices:
    def __init__(self):
        # TODO: Fix this circular import
        from services import ApprovalToggleService

        self.__approval_request_repository = ApprovalRequestRepository()
        self.__approval_step_repository = ApprovalStepRepository()
        self.__approver_request_history_repository = ApproverRequestHistoryRepository()
        self.__approver_flow_repository = ApprovalFlowRepository()
        self.__approval_toggle_service = ApprovalToggleService()
        self.__v2_api_client = V2APIClient()
        self.__log = common_utils_ins.logger

    async def createApprovalRequest(
        self,
        *,
        connection: AsyncConnection,
        request_data: CreateApprovalRequest,
        created_by: int,
        current_step_id: int,
    ) -> int:
        approval_request_id = await self.__approval_request_repository.create_or_update_approval_request(
                conn=connection,
                approval_flow_id=request_data.approvalFlowId,
                conversation_id=request_data.conversationId,
                smid=int(request_data.smId),
                created_by=created_by,
                current_step_id=current_step_id,
            )

        await self.__approver_request_history_repository.create_approver_request_history(
            connection=connection,
            approval_request_id=approval_request_id,
            step_id=-1,
            conversation_id=request_data.conversationId,
            approver_external_id=created_by,
            approval_flow_id=request_data.approvalFlowId
        )

        return { "id": approval_request_id }
        
    async def fetch_approval_request_details(
        self,
        *,
        conversation_id: Optional[int] = None,
        smid:Optional[int] = None,
        approval_request_id: Optional[int] = None,
        approver_external_id: Optional[int] = None,
        approver_type: Optional[int] = None,
        conn: AsyncConnection
    ) -> Dict:

        if not smid:
            approval_request = await self.__approval_request_repository.get_by_id(
                conn=conn, approval_request_id=approval_request_id
            )
            smid = approval_request.smId

        approval_request_info = (
            await self.__approval_request_repository.fetch_approval_request_details(
                conn=conn,
                conversation_id=conversation_id,
                smid=smid,
                approval_request_id=approval_request_id,
                approver_external_id=approver_external_id,
                approver_type=approver_type
            )
        )
        if len(approval_request_info) == 0:
            return {}
        approval_request_info = ApprovalRequestDetailResponse(
            **{
                key: approval_request_info[i]
                for i, key in enumerate(
                    ApprovalRequestDetailResponse.__fields__.keys()
                ) if i < len(approval_request_info) and approval_request_info[i] is not None
            }
        ).__dict__

        return approval_request_info

    async def processApprovalRequest(
        self,
        *,
        connection: AsyncConnection,
        approval_request_info: dict,
        sm_approver_id: int,
        request_data: ProcessApprovalRequest,
        approver_external_id: int,
        approval_flow_id: int
    ) -> bool:
    
        current_step_id = approval_request_info["currentStepId"]

        if request_data.status == APPROVAL_STATES.APPROVED:

            next_step_id = await self.__approval_step_repository.fetchNextStepId(conn=connection,
                                                                                 step_id=current_step_id)
            has_completed = not bool(next_step_id)  # if there's no next step, then it's completed

            await self.__approval_request_repository.update_approval_request(
                connection=connection,
                approval_request_id=int(request_data.approvalRequestId),
                status=request_data.status,
                has_completed=has_completed,
                current_step_id=current_step_id,
                next_step_id=next_step_id,
            )

            await self.__approver_request_history_repository.create_approver_request_history(
                connection=connection,
                approval_request_id=int(request_data.approvalRequestId),
                status=request_data.status,
                step_id=current_step_id,
                conversation_id=approval_request_info["conversationId"],
                sm_approver_id=sm_approver_id,
                approver_external_id=approver_external_id,
                approval_flow_id=approval_flow_id
            )

        elif request_data.status in [APPROVAL_STATES.REJECTED, APPROVAL_STATES.CANCELLED]:
            has_completed = True
            await self.stop_approval_request(
                connection=connection,
                approval_request_id=int(request_data.approvalRequestId),
                current_step_id=current_step_id,
                reason=request_data.reason,
                note=request_data.note,
                conversation_id=approval_request_info["conversationId"],
                sm_approver_id=sm_approver_id,
                approver_external_id=approver_external_id,
                approval_state=request_data.status,
                approval_flow_id=approval_flow_id
            )
            
        else:
            raise InvalidArgumentError("Invalid status")

        return has_completed
            
    async def get_by_conversation_id(self, *, conn: AsyncConnection, conversation_id: int,
                                     sm_id: Optional[int] = None) -> List:
        return await self.__approval_request_repository.get_by_conversation_id(conn=conn,
                                                                               conversation_id=conversation_id,
                                                                               sm_id=sm_id)

    async def trigger_email_notif_event(self, *, conn: AsyncConnection, conversation_id: int,  current_step_id: int,
                                        initial_step_id: int, initiated_by: int) -> None:

        if current_step_id == initial_step_id:
            next_step_id = current_step_id
        else:
            next_step_id = await self.__approval_step_repository.fetchNextStepId(conn=conn, step_id=current_step_id)
            if not next_step_id:
                return

        approvers = await self.__approver_flow_repository.get_approvers_for_current_step(conn=conn,
                                                                                         step_id=next_step_id)

        for approver in approvers:
            payload = {
                "gmailunit_id": conversation_id,
                "approver_external_type": approver.approverType.lower(),
                "approver_external_id": approver.approverExternalId,
                "initiated_by": initiated_by
            }
            event_producer.send_message(ProducerTopic.EMAIL_TRIGGER, json.dumps(payload))

    async def trigger_status_change_event(self, *, conversation_id: int, sm_id: int,
                                          target_status: str) -> None:

        module_state = await self.__approval_toggle_service.get_module_state(sm_id=sm_id)
        target_label = module_state.metaData["label_ids"][target_status.lower()]
        payload = {
            "gmailunit_id": conversation_id,
            "sm_id": sm_id,
            "service_name": SERVICE,
            "labels": [target_label]
        }
        event_producer.send_message(ProducerTopic.STATUS_CHANGE, json.dumps(payload))

    async def cancel_approvals_for_sms(self, connection: AsyncConnection, sm_ids: List[int]):
        approval_requests = await self.__approval_request_repository.fetch_approvals(connection, sm_ids,
                                                                                     APPROVAL_STATES.PENDING)

        for ar in approval_requests:
            await self.stop_approval_request(connection=connection, approval_request_id=ar.id,
                                             current_step_id=ar.currentStepId,
                                             conversation_id=ar.conversationId, approver_external_id=ar.createdBy,
                                             approval_state=APPROVAL_STATES.CANCELLED,
                                             approval_flow_id=ar.approvalFlowId)

    async def stop_approval_request(self, connection: AsyncConnection, approval_request_id: int, current_step_id: int,
                                    conversation_id: int, approver_external_id: int, approval_flow_id: int,
                                    approval_state: str,
                                    sm_approver_id: Optional[int] = None, reason: str = None, note: str = None):
        approval_state = approval_state if approval_state == APPROVAL_STATES.CANCELLED else APPROVAL_STATES.REJECTED

        await self.__approval_request_repository.update_approval_request(
                approval_request_id=approval_request_id,
                status = approval_state,
                has_completed=True,
                current_step_id=current_step_id,
                connection=connection
            )
        
        await self.__approver_request_history_repository.create_approver_request_history(
            approval_request_id=approval_request_id,
            status=approval_state,
            step_id=current_step_id,
            reason=reason,
            note=note,
            conversation_id=conversation_id,
            sm_approver_id=sm_approver_id,
            approver_external_id=approver_external_id,
            approval_flow_id=approval_flow_id,
            connection=connection,
        )

    def trigger_assignee_notification(self, *, approval_request_info: Dict, status: str) -> None:
        assignee_id = self._get_assignee(approval_request_info["smId"], approval_request_info["conversationId"])
        if assignee_id:
            thread_id = self._get_thread_id(approval_request_info["conversationId"], assignee_id)
            notif_payload = {
                'userids': assignee_id,
                'usergroupid': approval_request_info["usergroupId"],
                'notif_data': json.dumps({"xgmid": thread_id}),
                "subject": approval_request_info["name"],
                "content": "",
                'creator_id': approval_request_info["createdBy"],
                'notif_type': SERVICE + "_" + status.lower(),
                'action_type': NotificationActionType.NEW,
            }
            self.__v2_api_client.create_notification(notif_payload)

    def _get_assignee(self, sm_id, conversation_id) -> Union[int, None]:
        conversation_response = self.__v2_api_client.get_conversation_data(conversation_id)
        if len(conversation_response.get("conversationDetails", [])) > 0:
            for instance in conversation_response["conversationDetails"]:
                if instance["assignee_id"] and instance["smid"] == sm_id:
                    return instance["assignee_id"]

    def _get_thread_id(self, conversation_id, user_id):
        return self.__v2_api_client.get_thread_data(conversation_id, user_id)["g_threadid"]

