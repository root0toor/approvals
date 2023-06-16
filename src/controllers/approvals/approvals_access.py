from fastapi.responses import JSONResponse
from fastapi import status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from services.approvals_access import ApprovalsAccessService
from utils.helper import get_db_connection_dependency


class ApprovalsAccessController:
    """
    This is an access checker for only collaborator-approvers, since they're not a part of an SM, and thus
    have limited access privileges.
    """

    def __init__(self):
        self.__approvals_access_service = ApprovalsAccessService()

    async def has_access(
            self,
            request: Request,
            collaborator_id: int,
            conversation_id: int,
            connection: AsyncConnection = Depends(get_db_connection_dependency)
    ) -> JSONResponse:
        has_access = await self.__approvals_access_service.has_access(conn=connection,
                                                                      conversation_id=conversation_id,
                                                                      approver_external_id=collaborator_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": has_access},
        )
