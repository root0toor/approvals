from sqlalchemy.ext.asyncio import AsyncConnection

from services import ApprovalRequestServices, ApprovalToggleService
from typing import List


class SMDeletionService:

    def __init__(self) -> None:
        self.__approval_request_service = ApprovalRequestServices()
        self.__approval_toggle_service = ApprovalToggleService()

    async def process_sm_deletion_event(self, connection: AsyncConnection, sm_ids: List[int]) -> None:
        # cancel pending approvals and remove collaborator access from pvt link
        await self.__approval_request_service.cancel_approvals_for_sms(connection, sm_ids)
        await self.__approval_toggle_service.disable(sm_ids=sm_ids)
