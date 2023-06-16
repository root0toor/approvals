from sqlalchemy.ext.asyncio import AsyncConnection

from dtos.response import SuccessResponse,FailureResponse
from dtos.request.approvals import CreateApprovalRequest
from fastapi import status, Request, Depends
from fastapi.responses import JSONResponse
from services import ApprovalFlowServices, ApprovalRequestServices
from auth.active_user import ActiveHiverUser
from exceptions.errors import AuthorizationError
from utils.constant import APPROVAL_STATES
from utils.helper import get_db_connection_dependency


class CreateApprovalRequestController:

    async def createApprovalRequestController(
        self,
        request: Request,
        request_data: CreateApprovalRequest,
        connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        """
        Create an approval request for a conversation
        """
        approval_request_services = ApprovalRequestServices()
        approval_flow_services = ApprovalFlowServices()
            
        active_hiver_user = ActiveHiverUser()
        await active_hiver_user.setUserDetails(request=request)

        smid = int(request_data.smId)
        is_sm_member = active_hiver_user.isSmMember(smid=smid)
        if not is_sm_member:
            raise AuthorizationError

        user_details = active_hiver_user.getUserDetails()
        created_by = user_details["userid"]

        try:
            approval_flow_info = await approval_flow_services.fetch_active_approval_flow_details(
                conn=connection, approval_flow_id=request_data.approvalFlowId
            )
            first_step_id = approval_flow_info["initialStepId"]

            """creating approval request for the conversation"""

            approval_request_data = await approval_request_services.createApprovalRequest(
                connection=connection,
                request_data=request_data,
                created_by=created_by,
                current_step_id=first_step_id,
            )

            await approval_request_services.trigger_email_notif_event(conn=connection,
                                                                      conversation_id=request_data.conversationId,
                                                                      current_step_id=first_step_id,
                                                                      initial_step_id=first_step_id,
                                                                      initiated_by=created_by)
            await approval_request_services.trigger_status_change_event(conversation_id=request_data.conversationId,
                                                                        sm_id=smid,
                                                                        target_status=APPROVAL_STATES.PENDING)
        except Exception as e:
            await connection.rollback()
            raise e
        else:
            await connection.commit()

        response = SuccessResponse(data=approval_request_data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.dict(by_alias=True),
        )
