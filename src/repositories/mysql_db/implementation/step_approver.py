from typing import List

from sqlalchemy import case, func, literal, select, and_, dialects, text
from sqlalchemy.ext.asyncio import AsyncConnection

from ..models import StepApprover, StepApproverBaseColumn
from utils.initialize_common_utils import common_utils_ins


class StepApproverRepository:
    def __init__(self) -> None:
        self.__log = common_utils_ins.logger

    async def createStepApprover(
            self, *, conn: AsyncConnection, approval_step_id: int, sm_approver_id: int, created_by: int
    ) -> int:

        self.__log.info(
            f"Creating approver step for approval step id {approval_step_id} and sm approver id {sm_approver_id}")
        ins = StepApprover.insert().values(
            {
                StepApproverBaseColumn.APPROVAL_STEP_ID.value: approval_step_id,
                StepApproverBaseColumn.SM_APPROVER_ID.value: sm_approver_id,
                StepApproverBaseColumn.CREATED_BY.value: created_by,
            }
        )
        result = await conn.execute(ins)
        return result.lastrowid

    async def get_approvers_for_steps(self, *, conn: AsyncConnection, step_ids: List[int]) -> List:
        select_query = select(StepApprover).where(StepApprover.c.approvalStepId.in_(step_ids))
        results = await conn.execute(select_query)
        return results.fetchall()

        