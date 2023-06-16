from typing import Union

from sqlalchemy.ext.asyncio import AsyncConnection

from services import ApproverServices
from utils.constant import USER_TYPE


class UserTypeChange:
    REMOVED_USER_FUNCTION = "change_for_removed_user"
    ADDED_USER_FUNCTION = "change_for_added_user"

    def __init__(self) -> None:
        self.__approver_service = ApproverServices()

    async def change_for_removed_user(self, usergroup_id: int, sm_id: int, user_id: int, email_id: str,
                                      conn: AsyncConnection) -> bool:
        sm_approver = await self.__approver_service.fetch_sm_approver_details(sm_id=sm_id,
                                                                              approver_external_id=user_id,
                                                                              approver_type=USER_TYPE.SM_USER,
                                                                              conn=conn)

        if not sm_approver:
            return False

        collaborator_id = await self.__approver_service.register_approver_as_collaborator(email_id=email_id,
                                                                                          usergroup_id=usergroup_id,
                                                                                          invited_by=-1)

        await self.__approver_service.update_approver_sm_details(sm_approver_id=sm_approver.id,
                                                                 approver_type=USER_TYPE.COLLABORATOR,
                                                                 approver_external_id=collaborator_id,
                                                                 conn=conn)

        return True

    async def change_for_added_user(self, sm_id: int, user_id: int, collaborator_id: Union[int, None],
                                    conn: AsyncConnection) -> bool:
        sm_approver = await self.__approver_service.fetch_sm_approver_details(sm_id=sm_id,
                                                                              approver_external_id=collaborator_id,
                                                                              approver_type=USER_TYPE.COLLABORATOR,
                                                                              conn=conn)

        if not sm_approver:
            return False

        await self.__approver_service.update_approver_sm_details(sm_approver_id=sm_approver.id,
                                                                 approver_type=USER_TYPE.SM_USER,
                                                                 approver_external_id=user_id,
                                                                 conn=conn)

        return True
