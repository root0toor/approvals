from fastapi.responses import JSONResponse
from fastapi import Depends, Request, status

from auth.active_user import ActiveHiverUser
from dtos.request.approvals import UpdateApprovalFlowRequest
from dtos.response import SuccessResponse
from exceptions.errors import AuthorizationError
from services import ApprovalFlowServices
from sqlalchemy.ext.asyncio import AsyncConnection
from utils.initialize_common_utils import common_utils_ins
from utils.helper import get_db_connection_dependency

class UpdateApprovalFlowController:

    def __init__(self):
        self._log = common_utils_ins.logger
        self._approval_flow_services = ApprovalFlowServices()
        self._active_hiver_user = ActiveHiverUser()


    async def update_approval_flow(
        self,
        approvalflowid: int,
        request: Request,
        request_data: UpdateApprovalFlowRequest,
        connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        await self._active_hiver_user.setUserDetails(request=request)
        is_admin = self._active_hiver_user.hasAccessToSMConfiguration(smid=request_data.smId)

        if not is_admin:
            raise AuthorizationError
        
        kwargs = request_data.dict(exclude={"smId"})
        
        try:
            await self._approval_flow_services.update_approval_flow(
                conn=connection,
                approval_flow_id=approvalflowid,
                kwargs=kwargs
            )
        except Exception as e:
            await connection.rollback()
            raise e
        else:
            await connection.commit()

        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="")

