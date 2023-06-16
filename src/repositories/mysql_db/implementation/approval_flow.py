from typing import Dict, List, Optional

from sqlalchemy import desc, select, and_, update
from sqlalchemy.ext.asyncio import AsyncConnection

from exceptions.errors import NoResultFoundError
from utils.initialize_common_utils import common_utils_ins
from ..models import (
    ApprovalFlowBaseColumn,
    ApprovalFlow,
    StepApprover,
    SmApprover,
    Approver,
)


class ApprovalFlowRepository:
    def __init__(self) -> None:
        self.__log = common_utils_ins.logger

    async def createApprovalFlow(
        self,
        *,
        conn: AsyncConnection,
        smId: int,
        name: str,
        usergroup_id: int,
        created_by: int,
    ) -> int:
        
        query = ApprovalFlow.insert().values(
            {
                ApprovalFlowBaseColumn.NAME.value: name,
                ApprovalFlowBaseColumn.SMID.value: smId,
                ApprovalFlowBaseColumn.USERGROUPID.value: usergroup_id,
                ApprovalFlowBaseColumn.CREATED_BY.value: created_by,
            }
        )
        result = await conn.execute(query)
        return result.lastrowid
            
    async def checkApprovalFlowExistWithName(self, *, conn: AsyncConnection, smid: int, name: str) -> bool:
        query = select(ApprovalFlow).where(
            and_(
                ApprovalFlow.c.name == name,
                ApprovalFlow.c.smId == smid,
            )
        )
        results = await conn.execute(query)

        return results.rowcount != 0
        
    async def setInitialStepIdOfApprovalFlow(
        self, conn: AsyncConnection, initial_step_id:int ,approval_flow_id: int
    ) -> None:

        self.__log.info(f"Set initial step id of approval flow id {approval_flow_id}")
        
        query = (
            ApprovalFlow.update()
            .where(
                ApprovalFlow.c.id == approval_flow_id,
                ApprovalFlow.c.initialStepId == None
            )
            .values(
                {
                    ApprovalFlow.c.initialStepId: initial_step_id,
                }
            )
        )
        await conn.execute(query)

    async def listApprovalFlow(self, conn: AsyncConnection, smid: int) -> List:
        query = select(
            ApprovalFlow.c.id,
            ApprovalFlow.c.name,
            ApprovalFlow.c.createdBy,
            ApprovalFlow.c.usergroupId,
            ApprovalFlow.c.isActive,
        ).where(
            and_(ApprovalFlow.c.smId == smid)
        )
        query = query.order_by(desc(ApprovalFlow.c.id))
        results = await conn.execute(query)
        return results.all()

    async def get_approvers_for_current_step(self, step_id: int, conn: AsyncConnection) -> List:
        query = (
            select(
                Approver.c.id,
                SmApprover.c.approverExternalId,
                SmApprover.c.approverType
            ).select_from(
                StepApprover.join(
                    SmApprover,
                    SmApprover.c.id == StepApprover.c.smApproverId
                )
            ).join(
                Approver,
                Approver.c.id == SmApprover.c.approverId
            ).where(
                StepApprover.c.approvalStepId == step_id
            ).group_by(
                Approver.c.id
            )
        )

        results = await conn.execute(query)

        return results.all()

    async def fetch_active_approval_flow_details(self, conn: AsyncConnection, approval_flow_id: int) -> ApprovalFlow:
        self.__log.info(f"Fetching approval flow details for approval flow id {approval_flow_id}")
        query = select(ApprovalFlow).where(
            and_(
                ApprovalFlow.c.isActive.is_(True),
                ApprovalFlow.c.id == approval_flow_id,
            )
        )
        results = await conn.execute(query)

        if results.rowcount == 0:
            raise NoResultFoundError("Approval flow doesn't exist")
        return results.one()

    async def update_approval_flow(
        self,
        *,
        conn: AsyncConnection,
        approval_flow_id : int,
        kwargs: Dict
    ):
        self.__log.info(f"Updating approval flow details for approval flow id {approval_flow_id}")
        query = update(ApprovalFlow).where(ApprovalFlow.c.id == approval_flow_id).values(kwargs)
        results = await conn.execute(query)
        return results.rowcount