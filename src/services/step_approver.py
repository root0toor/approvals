from typing import List

from sqlalchemy.ext.asyncio import AsyncConnection

from repositories.mysql_db.implementation import StepApproverRepository


class StepApproverServices:
    def __init__(self):
        self.__step_approver_repository = StepApproverRepository()

    async def get_approvers_for_steps(self, *, conn: AsyncConnection, step_ids: List[int]) -> List:
        return await self.__step_approver_repository.get_approvers_for_steps(conn=conn, step_ids=step_ids)
