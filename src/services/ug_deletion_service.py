from sqlalchemy.ext.asyncio import AsyncConnection

from services import SMDeletionService
from typing import List


class UGDeletionService:

    def __init__(self) -> None:
        self.__sm_deletion_service = SMDeletionService()

    async def process_ug_deletion_event(self, connection: AsyncConnection, sm_ids: List[int]) -> None:
        # cancel pending approvals and remove collaborator access from pvt link
        await self.__sm_deletion_service.process_sm_deletion_event(connection, sm_ids)
