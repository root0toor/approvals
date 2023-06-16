from typing import Tuple, Optional, List

from sqlalchemy.ext.asyncio import AsyncConnection

from ..models import ApprovalRequestBaseColumn, ApprovalRequest, ApprovalStep, StepApprover, SmApprover, Approver, ApprovalFlow, Approver
from sqlalchemy import case, select, and_
from utils.initialize_common_utils import common_utils_ins
from utils.constant import APPROVAL_STATES

class ApprovalRequestRepository:
    def __init__(self) -> None:
        self.__log = common_utils_ins.logger

    async def create_or_update_approval_request(
        self,
        conn: AsyncConnection,
        approval_flow_id: int,
        conversation_id: int,
        smid: int,
        created_by: int,
        current_step_id: int
    ) -> int:
        
        self.__log.info(f"Creating approval request for approval flow id {smid} and conversation id {conversation_id}")

        # Checking if the ApprovalRequest exists for combination of conversation, sm, status in rejected or
        # cancelled. This is required for re-initiating the ApprovalRequest without creating a new entry in
        # ApprovalRequest table
        select_query = (
            select(ApprovalRequest.c.id)
            .where(
                ApprovalRequest.c.conversationId == conversation_id,
                ApprovalRequest.c.smId == smid,
                ApprovalRequest.c.status.in_([APPROVAL_STATES.REJECTED, APPROVAL_STATES.CANCELLED])
            )
        )
        select_result = await conn.execute(select_query)
        filtered_row = select_result.fetchone()

        if filtered_row:
            # If we find row corresponding to above criteria, we update the ApprovalRequest instead of creating one
            update_query = (
                ApprovalRequest.update()
                .where(
                    ApprovalRequest.c.conversationId == conversation_id,
                    ApprovalRequest.c.smId == smid,
                    ApprovalRequest.c.status.in_([APPROVAL_STATES.REJECTED, APPROVAL_STATES.CANCELLED])
                )
                .values(
                    {
                        ApprovalRequest.c.approvalFlowId: approval_flow_id,
                        ApprovalRequest.c.status: APPROVAL_STATES.PENDING,
                        ApprovalRequest.c.createdBy: created_by,
                        ApprovalRequest.c.currentStepId: current_step_id,
                    }
                )
            )
            await conn.execute(update_query)
            return filtered_row.id
        else:
            # If not then create new ApprovalRequest
            ins_query = ApprovalRequest.insert().values(
                {
                    ApprovalRequestBaseColumn.APPROVAL_FLOW_ID.value: approval_flow_id,
                    ApprovalRequestBaseColumn.SMID.value: smid,
                    ApprovalRequestBaseColumn.CONVERSATION_ID.value: conversation_id,
                    ApprovalRequestBaseColumn.CREATED_BY.value: created_by,
                    ApprovalRequestBaseColumn.CURRENT_STEP_ID.value: current_step_id,
                }
            )

            insert_result = await conn.execute(ins_query)
            return insert_result.lastrowid

    async def fetch_approval_request_details(
        self,
        *,
        conversation_id: Optional[int] = None,
        smid: Optional[int] = None,
        approval_request_id: Optional[int] = None,
        approver_external_id: Optional[int] = None,
        approver_type: Optional[int] = None,
        conn: AsyncConnection
    ) -> Tuple:

        if approval_request_id:

            self.__log.info(f"Fetching approval request details for approval request id {approval_request_id}")

            query = (
                select(
                    ApprovalRequest.c.id,
                    ApprovalRequest.c.smId,
                    ApprovalRequest.c.approvalFlowId,
                    ApprovalRequest.c.conversationId,
                    ApprovalRequest.c.status,
                    ApprovalRequest.c.currentStepId,
                    ApprovalRequest.c.permalink,
                    ApprovalRequest.c.createdBy,
                    ApprovalRequest.c.createdAt,
                    ApprovalFlow.c.name,
                    ApprovalFlow.c.usergroupId,
                    case(
                        (
                            and_(
                                SmApprover.c.approverExternalId == approver_external_id,
                                SmApprover.c.approverType == approver_type,
                                SmApprover.c.smId == smid
                            ),
                            True
                        ),
                        else_=False
                    )
                )
                .select_from(
                    ApprovalRequest.join(
                        ApprovalFlow,
                        ApprovalRequest.c.approvalFlowId == ApprovalFlow.c.id,
                    )
                )
                .join(
                    ApprovalStep,
                    ApprovalStep.c.approvalFlowId == ApprovalFlow.c.id
                ).join(
                    StepApprover,
                    StepApprover.c.approvalStepId == ApprovalStep.c.id
                ).join(
                    SmApprover,
                    SmApprover.c.id == StepApprover.c.smApproverId
                ).join(
                    Approver,
                    Approver.c.id == SmApprover.c.approverId
                )
                .where(
                    and_(
                        ApprovalRequest.c.id == approval_request_id,
                        ApprovalStep.c.id == ApprovalRequest.c.currentStepId
                    )
                ).group_by(
                    ApprovalRequest.c.conversationId, ApprovalFlow.c.smId
                )
            )
        elif conversation_id:

            self.__log.info(f"Fetching approval request details for conversation id {conversation_id}")

            query = (
                select([
                    ApprovalRequest.c.id,
                    ApprovalRequest.c.smId,
                    ApprovalRequest.c.approvalFlowId,
                    ApprovalRequest.c.conversationId,
                    ApprovalRequest.c.status,
                    ApprovalRequest.c.currentStepId,
                    ApprovalRequest.c.permalink,
                    ApprovalRequest.c.createdBy,
                    ApprovalRequest.c.createdAt,
                    ApprovalFlow.c.name,
                    ApprovalFlow.c.usergroupId,
                ])
                .select_from(ApprovalRequest.join(ApprovalFlow, ApprovalRequest.c.approvalFlowId == ApprovalFlow.c.id))
                .where(
                    and_(
                        ApprovalRequest.c.conversationId == conversation_id,
                        ApprovalRequest.c.smId == smid
                    )
                )
                .group_by(ApprovalRequest.c.id)
            )

        results = await conn.execute(query)
        if results.rowcount == 0:
            return ()

        approval_request_details = results.one()

        if approval_request_id:
            return approval_request_details

        is_approver = case([(and_(SmApprover.c.approverExternalId == approver_external_id,
                                  SmApprover.c.approverType == approver_type,
                                  SmApprover.c.smId == smid),
                             "TRUE")], else_="FALSE").label("isApprover")

        sub_query = (
            select([is_approver])
            .select_from(ApprovalRequest)
            .join(ApprovalStep, ApprovalStep.c.id == ApprovalRequest.c.currentStepId)
            .join(StepApprover, StepApprover.c.approvalStepId == ApprovalStep.c.id)
            .join(SmApprover, SmApprover.c.id == StepApprover.c.smApproverId)
            .join(Approver, Approver.c.id == SmApprover.c.approverId)
            .where(and_(ApprovalRequest.c.conversationId == conversation_id, ApprovalRequest.c.smId == smid))
            .group_by(is_approver)
            .where(is_approver == "TRUE")
        )

        sub_query_result = await conn.execute(sub_query)

        sub_query_value = sub_query_result.one() if sub_query_result.rowcount != 0 else (False,)

        final_result = (*approval_request_details, *sub_query_value)

        return final_result

    async def update_approval_request(self, connection: AsyncConnection, approval_request_id: int, status: str,
                                      has_completed: bool, current_step_id: Optional[int],
                                      next_step_id: Optional[int] = False
                                      ) -> int:
        
        """Note: If the approval does not complete the approval flow, then the status should remain as Pending"""
        # TODO: Fix the below non-intuitive code
        status = status if has_completed else ApprovalRequest.c.status
        next_step_id = next_step_id if next_step_id else None
        
        ins = (
            ApprovalRequest.update()
            .where(
                and_(
                    ApprovalRequest.c.id == approval_request_id,
                    ApprovalRequest.c.status == APPROVAL_STATES.PENDING,
                    ApprovalRequest.c.currentStepId == current_step_id
                )
            )
            .values(
                {
                    ApprovalRequestBaseColumn.CURRENT_STEP_ID.value: next_step_id,
                    ApprovalRequestBaseColumn.STATUS.value: status,
                }
            )
        )

        results = await connection.execute(ins)
        return results.rowcount

    async def get_by_conversation_id(self, *, conn: AsyncConnection, conversation_id: int,
                                     sm_id: Optional[int] = None) -> Optional[List]:
        select_query = select(ApprovalRequest).where(ApprovalRequest.c.conversationId == conversation_id)
        if sm_id:
            select_query = select_query.where(ApprovalRequest.c.smId == sm_id)
        result = await conn.execute(select_query)
        if result.rowcount == 0:
            return None
        return result.all()

    async def fetch_approvals(self, conn: AsyncConnection, sm_ids: List[int], approval_state: str):
        select_stmt = ApprovalRequest.select().where(
            and_(
                ApprovalRequest.c.smId.in_(sm_ids),
                ApprovalRequest.c.status == approval_state
            )
        )
        results = await conn.execute(select_stmt)

        return results.fetchall()
    
    # TODO: Standardize all SELECT query functions
    async def get_by_id(self, *, approval_request_id: int, conn: AsyncConnection):
        select_query = select(ApprovalRequest).where(ApprovalRequest.c.id == approval_request_id)
        result = await conn.execute(select_query)
        return result.first()

               
