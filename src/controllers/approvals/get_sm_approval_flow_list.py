from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from services import ApprovalFlowServices
from fastapi import status, Request, Depends
from dtos.response import SuccessResponse,FailureResponse
from auth.active_user import ActiveHiverUser
from exceptions.errors import AuthorizationError
from utils.helper import get_db_connection_dependency
from utils.initialize_common_utils import common_utils_ins


class GetApprovalFlowListForSMController:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def getApprovalFlowListForSM(
        self,
            request: Request,
            smid: int,
            connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        approval_flow_services = ApprovalFlowServices()
        
        active_hiver_user = ActiveHiverUser()
        await active_hiver_user.setUserDetails(request=request)

        is_sm_member = active_hiver_user.isSmMember(smid=smid)

        if not is_sm_member:
            raise AuthorizationError

        list_of_approval_flow = await approval_flow_services.listApprovalFlowBySmId(
            conn=connection, smid=smid
        )

        response = SuccessResponse(
            data=list_of_approval_flow,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict(by_alias=True),
        )
