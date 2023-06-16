from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from services import (
    ApproverRequestHistoryServices,
    ApprovalRequestServices,
)
from fastapi import Request, status, Depends
from utils import helper
from fastapi.encoders import jsonable_encoder
from dtos.response import SuccessResponse
from dtos.response.entities import ApproverResponse, ApproversListResponse
from auth.active_user import ActiveHiverUser, ActiveApprover
from exceptions.errors import AuthorizationError
from services.approvals_access import ApprovalsAccessService
from services.approver_services import ApproverServices
from services.step_approver import StepApproverServices
from utils.constant import USER_TYPE
from utils.helper import get_db_connection_dependency, get_valid_approval_step_ids
from exceptions.errors import NoResultFoundError


class ApprovalRequestDetailsController:

    def __init__(self):
        self.approval_access_service = ApprovalsAccessService()
        self.approval_request_services = ApprovalRequestServices()
        self.approver_request_history_services = ApproverRequestHistoryServices()
        self.approver_services = ApproverServices()
        self.step_approver_services = StepApproverServices()

    async def approvalRequestDetailController(
        self,
        request: Request,
        connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        """
        This function is made to fetch the approval request details
        along with the approver history for the conversation attached
        to it.
        """        
        active_hiver_user = ActiveHiverUser()
        await active_hiver_user.setUserDetails(request=request)

        params = request.query_params
        conversation_id = int(params["conversation_id"])
        smid = int(params["sm_id"])
        from_collab_space = bool(request.query_params.get("source", "").lower() == "collab_space")

        is_sm_member = active_hiver_user.isSmMember(smid=smid)

        if not is_sm_member:
            raise AuthorizationError

        active_approver = ActiveApprover()
        await active_approver.setUserDetails(request=request)
        approver_external_id, approver_type = active_approver.getApproverDetails()

        # Check if the user is a valid approver in the current approval request
        # This check is only for collaborators, since SM members should be able to see the approval requests
        # in every case
        # While on collab space, only collaborators who are valid approvers should see the approval request details
        # TODO: Move this check into the middleware
        has_access = True
        if approver_type == USER_TYPE.COLLABORATOR:
            if not await self.approval_access_service.has_access(conn=connection,
                                                            conversation_id=conversation_id,
                                                            approver_external_id=approver_external_id,
                                                            sm_id=smid):
                has_access = False

        if has_access:
            """fetch approval request details for the coversation"""
            approval_request_info = (
                await self.approval_request_services.fetch_approval_request_details(
                    conn=connection,
                    conversation_id=conversation_id,
                    smid=smid,
                    approver_external_id=approver_external_id,
                    approver_type=approver_type
                )
            )
        else:
            approval_request_info = {}

        print(f"Testing123: ari --> {approval_request_info}")
        if len(approval_request_info) != 0:
            approval_request_info["statusDetails"] = ""
            """fetching details of approver history for the approval request"""
            approver_history = (
                await self.approver_request_history_services.fetch_approver_history_details(
                    conn=connection,
                    approval_request_info=approval_request_info,
                    user_group_id=approval_request_info["usergroupId"],
                    approver_external_id=approver_external_id,
                    should_remove_flow_name=from_collab_space,
                    approver_type=approver_type
                )
            )
            approval_request_info["approvalRequestDetails"] = approver_history

        response = SuccessResponse(
            data=jsonable_encoder(approval_request_info if len(approval_request_info) != 0 else None)
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict(by_alias=True),
        )


    async def fetch_approvers(
        self,
        request: Request,
        connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        
        params = request.query_params
        conversation_id = int(params["conversation_id"])
        
        try:
            approval_requests = await self.approval_request_services.get_by_conversation_id(conn=connection, conversation_id=conversation_id)
            if approval_requests is None:
                raise NoResultFoundError(f"No approval requests found for conversation: {conversation_id}")
            
            approval_request_ids = []
            current_step_ids = []
            for approval_request in approval_requests:
                approval_request_ids.append(approval_request.id)
                current_step_ids.append(approval_request.currentStepId)

            completed_histories = await self.approver_request_history_services.\
                fetch_history_records(conn=connection, approval_request_ids=approval_request_ids)
            
            valid_approval_step_ids = await get_valid_approval_step_ids(completed_histories=completed_histories)
            valid_approval_step_ids.extend(current_step_ids)

            step_approvers = await self.step_approver_services.get_approvers_for_steps(
                conn=connection, step_ids = valid_approval_step_ids
            )

            sm_approver_ids = [step_approver.smApproverId for step_approver in step_approvers]
            sm_approvers = await self.approver_services.fetchApproverDetails(conn=connection, sm_approver_ids=sm_approver_ids)
            if sm_approvers is None:
                raise NoResultFoundError(f"No approvers found for conversation: {conversation_id}")
            
            approvers = []
            for sm_approver in sm_approvers:
                approver = ApproverResponse(
                    approverExternalId = sm_approver["approverExternalId"],
                    approverType = sm_approver["approverType"]
                )
                if approver not in approvers:
                    approvers.append(approver)

            response = SuccessResponse(data=ApproversListResponse(approvers=approvers))
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response.dict(by_alias=True),
            )
        except NoResultFoundError as e:
            response = SuccessResponse(data=ApproversListResponse(approvers=ApproverResponse()))
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response.dict(by_alias=True),
        )
