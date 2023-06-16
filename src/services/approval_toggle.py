import uuid
from typing import Dict, List

from external_api_clients import V2APIClient
from external_api_clients.label_manager_api_client import LabelManagerAPIClient
from repositories.mysql_db.implementation import ApprovalToggleRepository
from utils.constant import ApprovalToggleTask, APPROVAL_STATES, ApprovalStateValue
from repositories.mysql_db.models import ApprovalModuleState
from utils.constants import SERVICE


class ApprovalToggleService:
    # NOTE: The order of the tasks matters. DO NOT CHANGE IT!!
    TASKS_IN_ORDER = [ApprovalToggleTask.LABELS, ApprovalToggleTask.VIEWS, ApprovalToggleTask.AUTO_FAVOURITE]

    def __init__(self) -> None:
        self.__approval_toggle_repository = ApprovalToggleRepository()
        self.__v2_api_client = V2APIClient()
        self.__label_manager_api_client = LabelManagerAPIClient()

    def _create_labels(self, *, sm_id: int) -> Dict:
        labels_to_create = [
            APPROVAL_STATES.PENDING.lower(),
            APPROVAL_STATES.REJECTED.lower(),
            APPROVAL_STATES.CANCELLED.lower(),
            APPROVAL_STATES.APPROVED.lower(),
        ]
        payload = {
            "unique_id": uuid.uuid4().hex,
            "sm_id": sm_id,
            "service_name": SERVICE,
            "label_names": labels_to_create,
        }
        resp = self.__label_manager_api_client.create_labels(sm_id=sm_id, payload=payload)
        return resp["label_ids"]

    def _create_view(self, *, user_id: int, sm_id: int, sm_name: str, ug_id: int) -> int:
        APPROVAL_STATE_VALUE = ApprovalStateValue(APPROVED=1, CANCELLED=2, REJECTED=3, PENDING=4)
        json_query = {
            "status": {
                "op": "ANY",
                "values": [
                    "open",
                    "pending"
                ]
            },  # TODO: Get these from V2 instead of hard coding
            "approvals": {
                "op": "ANY",
                "values": [
                    APPROVAL_STATES.PENDING.lower(),
                    APPROVAL_STATES.REJECTED.lower(),
                    APPROVAL_STATES.APPROVED.lower()
                ],
                "ids": [
                    APPROVAL_STATE_VALUE.PENDING,
                    APPROVAL_STATE_VALUE.REJECTED,
                    APPROVAL_STATE_VALUE.APPROVED
                ]
            }
        }
        conversation_label_query = f"label:{sm_name} AND (label:{sm_name}/open OR label:{sm_name}/pending)"
        approval_label_query = f"(label:{sm_name}/{SERVICE}/{APPROVAL_STATES.PENDING.lower()} " \
                               f"OR " \
                               f"label:{sm_name}/{SERVICE}/{APPROVAL_STATES.REJECTED.lower()} " \
                               f"OR " \
                               f"label:{sm_name}/{SERVICE}/{APPROVAL_STATES.APPROVED.lower()})"
        full_gmail_query = conversation_label_query + " AND " + approval_label_query
        payload = {
            "shared": 1,
            "name": "Approvals",
            "jsonQuery": json_query,
            "gmailQuery": full_gmail_query,
            "ugId": ug_id,
            "overrideLimits": {
                "favLimit": True,
                "viewsLimit": True
            }
        }
        resp = self.__v2_api_client.create_view(user_id=user_id, sm_id=sm_id, payload=payload)
        return resp["id"]

    def _favourite_view(self, *, sm_id: int, view_id: int) -> None:
        self.__v2_api_client.favourite_view(sm_id=sm_id, view_id=view_id)

    async def _enable(self, *, sm_id: int, sm_name: str, user_id: int, ug_id: int) -> None:
        # 1. Upsert record in ApprovalsModule table
        row_id = await self.__approval_toggle_repository.enable(sm_id=sm_id)

        # 2. Get pending tasks
        module_state = await self.__approval_toggle_repository.get_by_col(col_name=ApprovalModuleState.id.key,
                                                                          col_val=row_id)
        view_id = module_state.metaData.get("view_id")

        # 3. Process pending tasks and record the updated state in the DB
        pending_tasks = []
        for task in self.TASKS_IN_ORDER:
            if module_state.pendingTasks[task]:
                pending_tasks.append(task)

        for task in pending_tasks:
            meta_data = {}

            if task == ApprovalToggleTask.LABELS:
                labels = self._create_labels(sm_id=sm_id)
                meta_data["label_ids"] = labels
            elif task == ApprovalToggleTask.VIEWS:
                view_id = self._create_view(user_id=user_id, sm_id=sm_id, sm_name=sm_name, ug_id=ug_id)
                meta_data["view_id"] = view_id
            elif task == ApprovalToggleTask.AUTO_FAVOURITE:
                self._favourite_view(sm_id=sm_id, view_id=view_id)

            await self.__approval_toggle_repository.mark_task_as_complete(row_id=row_id, task=task,
                                                                          incoming_meta_data=meta_data)

    async def disable(self, *, sm_ids: List[int]) -> None:
        await self.__approval_toggle_repository.disable(sm_ids=sm_ids)

    async def toggle(self, *, sm_id: int, sm_name: str, user_id: int, ug_id: int, enabled: bool) -> None:
        if not enabled:
            await self.disable(sm_ids=[sm_id])
        else:
            await self._enable(sm_id=sm_id, sm_name=sm_name, user_id=user_id, ug_id=ug_id)


    async def get_module_state(self, *, sm_id: int) -> ApprovalModuleState:
        return await self.__approval_toggle_repository.get_by_col(col_name=ApprovalModuleState.smId.key, col_val=sm_id)
