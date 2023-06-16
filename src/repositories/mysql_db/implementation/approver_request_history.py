from typing import List

from sqlalchemy.ext.asyncio import AsyncConnection

from utils.constant import APPROVAL_STATES
from ..models import ApproverRequestHistoryBaseColumn, ApproverRequestHistory, Approver, SmApprover, ApprovalRequest, ApprovalStep, ApprovalFlow, StepApprover
from sqlalchemy import and_, literal, select
from sqlalchemy.engine import Connection
from typing import Optional
from utils.initialize_common_utils import common_utils_ins


class ApproverRequestHistoryRepository:

    async def create_approver_request_history(
        self,
        *,
        approval_request_id: int,
        status: Optional[str] = APPROVAL_STATES.INITIATED,
        reason: Optional[str] = None,
        note: Optional[str] = None,
        step_id: int,
        conversation_id: int,
        sm_approver_id: Optional[int] = None,
        approver_external_id: int,
        approval_flow_id: int,
        connection: AsyncConnection
    ) -> int:
        ins = ApproverRequestHistory.insert().values(
            {
                ApproverRequestHistoryBaseColumn.APPROVAL_REQUEST_ID.value: approval_request_id,
                ApproverRequestHistoryBaseColumn.STEP_ID.value: step_id,
                ApproverRequestHistoryBaseColumn.CONVERSATION_ID.value: conversation_id,
                ApproverRequestHistoryBaseColumn.APPROVAL_FLOW_ID.value: approval_flow_id,
                ApproverRequestHistoryBaseColumn.STATUS.value: status,
                ApproverRequestHistoryBaseColumn.SM_APPROVER_ID.value: sm_approver_id,
                ApproverRequestHistoryBaseColumn.REASON.value: reason,
                ApproverRequestHistoryBaseColumn.NOTE.value: note,
                ApproverRequestHistoryBaseColumn.CREATED_BY.value: approver_external_id,
            }
        )
        results = await connection.execute(ins)
        return results.lastrowid

    async def fetch_approver_timeline(self, conn: AsyncConnection, approval_request_id: int) -> List:
        query = select(
            [
                ApprovalRequest.c.id,
                ApprovalStep.c.id.label("stepId"),
                literal(APPROVAL_STATES.IDLE).label("status"),
                ApproverRequestHistory.c.reason,
                ApproverRequestHistory.c.note,
                ApproverRequestHistory.c.createdAt,
                ApproverRequestHistory.c.createdBy,
                SmApprover.c.approverType,
                SmApprover.c.approverExternalId
            ]) \
            .select_from(ApprovalRequest
                        .join(ApprovalFlow, ApprovalFlow.c.id == ApprovalRequest.c.approvalFlowId)
                        .join(ApprovalStep, ApprovalStep.c.approvalFlowId == ApprovalFlow.c.id)
                        .outerjoin(ApproverRequestHistory, ApproverRequestHistory.c.approvalRequestId == ApprovalRequest.c.id)
                        .join(StepApprover, StepApprover.c.approvalStepId == ApprovalStep.c.id)
                        .join(SmApprover, SmApprover.c.id == StepApprover.c.smApproverId)
                        .join(Approver, Approver.c.id == SmApprover.c.approverId)
                        ) \
            .where(
                and_(
                    ApprovalRequest.c.id == approval_request_id,
                    ApprovalRequest.c.currentStepId <= ApprovalStep.c.id
                )
            )
        results = await conn.execute(query)

        return results.fetchall()

    async def fetch_approver_history(self, conn: AsyncConnection, approval_request_ids: List[int]) -> List:
        # If the Approval Request is rejected/cancelled then no smApprover details is tracked
        # SmApprover doesn't cancel or reject the request and their data will be null, but still we need to show the
        # Approver Request History for cancelled and rejected states. Hence, the outer Join.
        query = select(
            [
                ApproverRequestHistory.c.approvalRequestId,
                ApproverRequestHistory.c.id,
                ApproverRequestHistory.c.stepId,
                ApproverRequestHistory.c.status,
                ApproverRequestHistory.c.reason,
                ApproverRequestHistory.c.note,
                ApproverRequestHistory.c.createdAt,
                ApproverRequestHistory.c.createdBy,
                SmApprover.c.approverType,
                SmApprover.c.approverExternalId
            ]) \
            .select_from(
                ApproverRequestHistory.outerjoin(
                    SmApprover,
                    SmApprover.c.id == ApproverRequestHistory.c.smApproverId
                ).outerjoin(
                    Approver,
                    Approver.c.id == SmApprover.c.approverId
                )
            ) \
            .where(
                ApproverRequestHistory.c.approvalRequestId.in_(approval_request_ids),
            )
        results = await conn.execute(query)

        return results.fetchall()

        