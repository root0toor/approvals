from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from services import (
    ApprovalRequestServices,
    ApproverServices,
)
from fastapi import status, Request, BackgroundTasks, Depends
from dtos.response import SuccessResponse
from dtos.request.approvals import ProcessApprovalRequest
from exceptions.errors import AuthorizationError, NoResultFoundError
from auth.active_user import ActiveApprover
from utils.constant import APPROVAL_STATES, REASON
from exceptions.errors import InputValidationError
from utils.helper import get_db_connection_dependency
from utils.initialize_common_utils import common_utils_ins

class ProcessApprovalRequestController:

    async def processApprovalRequestController(
            self,
            request: Request,
            request_data: ProcessApprovalRequest,
            connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        """
        Transition an approval request to the next step
        """
        approval_request_services = ApprovalRequestServices()
        approver_services = ApproverServices()
        log = common_utils_ins.logger

        """validating request body if status is REJECTED"""

        if request_data.status == APPROVAL_STATES.REJECTED:
            if request_data.reason not in [REASON.DUPLICATE, REASON.INACCURATE, REASON.OTHER]:
                raise InputValidationError(
                    f"Reason value must be either {REASON.DUPLICATE} or {REASON.INACCURATE} or {REASON.OTHER}")
        else:
            request_data.reason, request_data.note = (None,) * 2

        active_approver = ActiveApprover()
        await active_approver.setUserDetails(request=request)

        approver_external_id, approver_type = active_approver.getApproverDetails()

        try:
            """fetch approval request details for the approval_request_id"""
            approval_request_info = (
                await approval_request_services.fetch_approval_request_details(
                    conn=connection,
                    approval_request_id=int(request_data.approvalRequestId),
                    approver_external_id=approver_external_id,
                    approver_type=approver_type
                )
            )

            if len(approval_request_info) == 0:
                raise NoResultFoundError("Approval request not found")

            current_step_id = approval_request_info["currentStepId"]

            """fetching active sm_approver_id for the current step"""
            sm_approver_id = await approver_services.getSmApproverIdForCurrentStep(
                conn=connection,
                approver_external_id=approver_external_id,
                approver_type=approver_type,
                current_step_id=current_step_id
            )

            if request_data.status != APPROVAL_STATES.CANCELLED and not sm_approver_id:
                raise AuthorizationError("Sm Approver doesn't have access")

            has_completed = await approval_request_services.processApprovalRequest(
                connection=connection,
                approval_request_info=approval_request_info,
                sm_approver_id=sm_approver_id,
                request_data=request_data,
                approver_external_id=approver_external_id,
                approval_flow_id=approval_request_info["approvalFlowId"]
            )

            if request_data.status == APPROVAL_STATES.APPROVED:
                arguments = {
                    "conn": connection,
                    "conversation_id": approval_request_info["conversationId"],
                    "current_step_id": current_step_id,
                    "initial_step_id": -1,  # random ID to make trigger_email_notif_event() work correctly
                    "initiated_by": approval_request_info["createdBy"]
                }
                if not has_completed:
                    await approval_request_services.trigger_email_notif_event(**arguments)

            if has_completed:
                await approval_request_services.trigger_status_change_event(
                    conversation_id=approval_request_info["conversationId"],
                    sm_id=approval_request_info["smId"],
                    target_status=request_data.status
                )
        except Exception as e:
            await connection.rollback()
            raise e
        else:
            await connection.commit()

        if has_completed and request_data.status != APPROVAL_STATES.CANCELLED:
            try:
                approval_request_services.trigger_assignee_notification(approval_request_info=approval_request_info,
                                                                        status=request_data.status)
            except Exception:
                log.exception(f"Error in sending assignee notification for request id "
                              f"{request_data.approvalRequestId}")

        response = SuccessResponse(
            data={"id": request_data.approvalRequestId}
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict(by_alias=True),
        )