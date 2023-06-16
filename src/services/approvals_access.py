from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from repositories.mysql_db.models import ApprovalRequest
from services import ApproverServices, ApprovalRequestServices, StepApproverServices, \
    ApprovalToggleService, ApproverRequestHistoryServices
from utils.constant import USER_TYPE
from utils.helper import get_valid_approval_step_ids
from utils.initialize_common_utils import common_utils_ins


class ApprovalsAccessService:
    def __init__(self):
        self.__approver_service = ApproverServices()
        self.__approval_request_service = ApprovalRequestServices()
        self.__step_approvers_service = StepApproverServices()
        self.__approval_toggle_service = ApprovalToggleService()
        self.__approver_request_history_services = ApproverRequestHistoryServices()
        self.__log = common_utils_ins.logger

    async def _has_access_for_single_request(self, *, conn: AsyncConnection, approval_request: ApprovalRequest,
                                             approver_external_id: int, approver_type: str) -> bool:
        module_state = await self.__approval_toggle_service.get_module_state(sm_id=approval_request.smId)

        if not module_state.enabled:
            self.__log.info(f"Approvals module is disabled for SMID {approval_request.smId}")
            return False

        completed_histories = await self.__approver_request_history_services.\
            fetch_history_records(conn=conn, approval_request_ids=[approval_request.id])
        
        valid_approval_step_ids = await get_valid_approval_step_ids(completed_histories=completed_histories)
        valid_approval_step_ids.append(approval_request.currentStepId)

        # Get all the approvers for the valid steps
        step_approvers = await self.__step_approvers_service.get_approvers_for_steps(
            conn=conn, step_ids=valid_approval_step_ids
        )
        sm_approver_ids = [approver.smApproverId for approver in step_approvers]

        # Check if any of them have the same approver external id as in the input
        approvers = await self.__approver_service.fetchApproverDetails(conn=conn,
                                                                       sm_approver_ids=sm_approver_ids,
                                                                       approver_external_id=approver_external_id,
                                                                       approver_type=approver_type,
                                                                       sm_id=approval_request.smId)
        return len(approvers) != 0

    async def has_access(self, *, conn: AsyncConnection, conversation_id: int, approver_external_id: int,
                         sm_id: Optional[int] = None, approver_type: Optional[str] = USER_TYPE.COLLABORATOR) -> bool:
        try:
            # Get all the approval requests for the gmail unit id, and an optional SM ID

            # sm_id will be a valid value when we want to check access for a single SM
            # else, a None value denotes we want to check for every SM the conversation is a part of
            approval_requests = await self.__approval_request_service.get_by_conversation_id(
                conn=conn,
                conversation_id=conversation_id,
                sm_id=sm_id
            )

            for approval_request in approval_requests:
                if await self._has_access_for_single_request(conn=conn,
                                                             approval_request=approval_request,
                                                             approver_external_id=approver_external_id,
                                                             approver_type=approver_type):
                    return True

            return False

        except Exception as e:
            self.__log.exception(f"Error while checking access for conversation id {conversation_id} : {e}")
            return False
