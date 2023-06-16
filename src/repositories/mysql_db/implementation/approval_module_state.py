from typing import Dict, Optional, Any, List

from sqlalchemy import select

from repositories.mysql_db.models import ApprovalModuleState
from utils.constant import ApprovalToggleTask
from utils.initialize_common_utils import common_utils_ins


class ApprovalToggleRepository:

    @staticmethod
    async def get_by_col(*, col_name: str, col_val: Any) -> ApprovalModuleState:
        instrumented_attribute = getattr(ApprovalModuleState, col_name)
        async with common_utils_ins.get_db_session() as session:
            async with session.begin():
                stmt = select(ApprovalModuleState).where(instrumented_attribute == col_val)
                res = await session.scalars(stmt)
                return res.first()

    @staticmethod
    # TODO: Return obj itself instead of its ID
    async def enable(*, sm_id: int) -> int:
        approvals_pending_tasks = {
            ApprovalToggleTask.LABELS: True,
            ApprovalToggleTask.VIEWS: True,
            ApprovalToggleTask.AUTO_FAVOURITE: True
        }

        # TODO: Replace with upsert
        async with common_utils_ins.get_db_session() as session:
            async with session.begin():
                stmt = select(ApprovalModuleState).where(ApprovalModuleState.smId == sm_id)
                res = await session.scalars(stmt)
                obj = res.first()

                if not obj:
                    obj = ApprovalModuleState(smId=sm_id, pendingTasks=approvals_pending_tasks)
                else:
                    obj.enabled = True

                session.add(obj)
                await session.commit()

        return obj.id

    async def disable(self, *, sm_ids: List[int]) -> None:
        async with common_utils_ins.get_db_session() as session:
            async with session.begin():
                # TODO: Remove the for loop after
                # Refactoring get_by_col so that col_val accepts a list of values
                for sm_id in sm_ids:
                    obj = await self.get_by_col(col_name=ApprovalModuleState.smId.key, col_val=sm_id)
                    if obj is None:
                        continue
                    obj.enabled = False
                    session.add(obj)
                await session.commit()

    async def mark_task_as_complete(self, *, row_id: int, task: str, incoming_meta_data: Optional[Dict] = None) -> None:
        if not incoming_meta_data:
            incoming_meta_data = {}

        obj = await self.get_by_col(col_name=ApprovalModuleState.id.key, col_val=row_id)

        async with common_utils_ins.get_db_session() as session:
            async with session.begin():
                obj.pendingTasks[task] = False
                obj.metaData.update(incoming_meta_data)
                session.add(obj)
                await session.commit()
