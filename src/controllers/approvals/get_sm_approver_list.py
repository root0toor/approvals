from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncConnection

from services import ApproverServices
from fastapi import status, Request, Depends
from dtos.response import SuccessResponse
from auth.active_user import ActiveHiverUser
from exceptions.errors import AuthorizationError
from utils.helper import get_db_connection_dependency


class GetSmApproverListController:

    async def get_sm_collaborator_list(self,
                                       request: Request,
                                       connection: AsyncConnection = Depends(get_db_connection_dependency)
                                       ) -> JSONResponse:
        body = await request.json()
        smids = body["smIds"]

        approver_services = ApproverServices()

        active_hiver_user = ActiveHiverUser()
        await active_hiver_user.setUserDetails(request=request)

        for smid in smids:
            is_admin = active_hiver_user.hasAccessToSMConfiguration(smid=smid)
            if not is_admin:
                raise AuthorizationError

        sm_approver_list = await approver_services.get_sm_collaborator_list(conn=connection, smids=smids)
        response = SuccessResponse(
            data=sm_approver_list,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.dict(by_alias=True),
        )
