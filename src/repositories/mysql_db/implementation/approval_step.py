from sqlalchemy.ext.asyncio import AsyncConnection

from ..models import ApprovalStepBaseColumn, ApprovalStep
from sqlalchemy import select
from typing import List, Optional
from utils.initialize_common_utils import common_utils_ins
from sqlalchemy.sql import text


class ApprovalStepRepository:

    async def fetchNextStepId(self, conn: AsyncConnection, step_id: int) -> Optional[int]:
        query = select(ApprovalStep.c.nextStepId).where(ApprovalStep.c.id == step_id)
        results = await conn.execute(query)

        if results.rowcount != 0:
            return results.one().nextStepId

    async def createApprovalStep(
        self,
        *,
        conn: AsyncConnection,
        approval_flow_id: int,
        created_by: int,
    ) -> int:
         
        query = ApprovalStep.insert().values(
            {
                ApprovalStepBaseColumn.APPROVAL_FLOW_ID.value: approval_flow_id,
                ApprovalStepBaseColumn.CREATED_BY.value: created_by,
            }
        )
        result = await conn.execute(query)
        return result.lastrowid

    async def fetchApprovalFlowSteps(self, *, approval_flow_id: int, conn: AsyncConnection) -> List:
        query = select(ApprovalStep).where(ApprovalStep.c.approvalFlowId == approval_flow_id)
        results = await conn.execute(query)
        return results.all()
            
    async def setNextStepIdOfApprovalStep(
        self, conn: AsyncConnection, approval_step_id:int, next_step_id:int
    ) -> None:
        query = (
            ApprovalStep.update()
            .where(
                ApprovalStep.c.id == approval_step_id,
            )
            .values(
                {
                    ApprovalStep.c.nextStepId: next_step_id
                }
            )
        )
        await conn.execute(query)
