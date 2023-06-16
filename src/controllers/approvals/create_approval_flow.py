from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from services import (
    ApprovalFlowServices,
    ApproverServices,
)
from fastapi import Request, status, Depends
from dtos.response import SuccessResponse, FailureResponse
from dtos.request.approvals import CreateApprovalFlowRequest
from auth.active_user import ActiveHiverUser
from utils import helper
from exceptions.errors import InputValidationError
from exceptions.errors import AuthorizationError
from utils.constant import USER_TYPE
from utils.helper import get_db_connection_dependency


class CreateApprovalFlowController:

    def validate_request_body(self, request_data: CreateApprovalFlowRequest):
        sm_user_ids = []
        collaborator_ids = []
        collaborator_emails = []

        for idx, steps in enumerate(request_data.steps):
            for approver in steps:
                approver_value = approver.value
                approver_type = approver.type

                if approver_type == USER_TYPE.COLLABORATOR:
                    if approver_value.isdigit():
                        collaborator_ids.append(
                            {
                                "step": idx,
                                "approver_id": approver_value,
                                "approver_type": approver_type,
                            }
                        )
                    else:
                        approver_email = approver_value
                        is_valid_email = helper.validate_email(approver_email)
                        if not is_valid_email:
                            raise InputValidationError("Please provide the valid email")
                        collaborator_emails.append(
                            {"step": idx, "approver_email": approver_email}
                        )
                else:     
                    sm_user_ids.append(
                        {
                            "step": idx,
                            "approver_id": approver_value,
                            "approver_type": approver_type,
                        }
                    )
    

        """validating approval flow steps ends"""

        return [
            collaborator_ids,
            collaborator_emails,
            sm_user_ids,
        ]

       

    async def createApprovalFlowController(
            self,
            request: Request,
            request_data: CreateApprovalFlowRequest,
            connection: AsyncConnection = Depends(get_db_connection_dependency)

    ) -> JSONResponse:

        """This function is made for creating an Approval flow along with Approval Step
        and Step Approver.The Approval flow can only be created by hiver admin if he has
        an access of the particular SM for which he is going to create an Approval flow.
        """

        approval_flow_services = ApprovalFlowServices()
        approver_services = ApproverServices()

        active_hiver_user = ActiveHiverUser()
        
        await active_hiver_user.setUserDetails(request=request)

        combination_of_approver_list = self.validate_request_body(
            request_data=request_data
        )
        
        is_admin = active_hiver_user.hasAccessToSMConfiguration(smid=request_data.smId)

        if not is_admin:
            raise AuthorizationError

        user_details = active_hiver_user.getUserDetails()
        userid = user_details["userid"]
        usergroup_id = user_details["usergroupid"]

        try:
            does_approval_flow_exist = await approval_flow_services.checkApprovalFlowExistWithName(
                conn=connection, smid=request_data.smId, name=request_data.name
            )

            if does_approval_flow_exist:
                raise InputValidationError(
                    f"Approval Flow with the name '{request_data.name}' already exist for the Sm")

            """vaildating sm_collaborator_ids for the Approval flow if it exist or not"""

            list_of_sm_approver_ids = [[] for _ in range(len(request_data.steps))]

            list_of_sm_approver_ids = await approver_services.checkSmApproversExist(
                connection=connection,
                smid=request_data.smId,
                list_of_approver_ids_details=combination_of_approver_list[0],
                list_of_sm_approver_ids=list_of_sm_approver_ids,
            )

            """saving collaborator emails for the Approval Flow"""

            list_of_sm_approver_ids = await approver_services.createApproverForEmails(
                connection=connection,
                smid=request_data.smId,
                approver_type=USER_TYPE.COLLABORATOR,
                userid=userid,
                list_of_collaborator_email_details=combination_of_approver_list[1],
                list_of_sm_approver_ids=list_of_sm_approver_ids,
                usergroup_id=usergroup_id
            )

            """saving hiver user for the Approval flow"""

            list_of_sm_approver_ids = await approver_services.createApproverForHiverUsers(
                connection=connection,
                smid=request_data.smId,
                approver_type=USER_TYPE.SM_USER,
                list_of_hiver_approver_external_ids_details=combination_of_approver_list[2],
                list_of_sm_approver_ids=list_of_sm_approver_ids,
            )

            """creating approval flow"""
            approval_flow_id = await approval_flow_services.createApprovalFlow(
                conn=connection,
                request_data=request_data,
                usergroup_id=usergroup_id,
                created_by=userid,
                list_of_sm_approver_ids=list_of_sm_approver_ids,
            )

            """Fetch newly created approval flow details"""
            approval_flow_details = (
                await approval_flow_services.fetch_active_approval_flow_details(
                    conn=connection, approval_flow_id=approval_flow_id
                )
            )
        except Exception as e:
            await connection.rollback()
            raise e
        else:
            await connection.commit()

        response = SuccessResponse(
            data=approval_flow_details,
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.dict(by_alias=True),
        )