from sqlalchemy.ext.asyncio import AsyncConnection

from repositories.mysql_db.implementation import (
    ApprovalFlowRepository,
    ApprovalStepRepository,
    StepApproverRepository
)
from dtos.request.approvals import CreateApprovalFlowRequest
from dtos.response.entities import (
    ApprovalFlowDetailResponse,
    ListApprovalFlowDetailResponse,
)
from repositories.mysql_db.models import ApprovalFlow
from typing import List, Dict
from utils import helper


class ApprovalFlowServices:
    def __init__(self):
        self.__approval_flow_repository = ApprovalFlowRepository()
        self.__approval_step_repository = ApprovalStepRepository()
        self.__step_approver_repository = StepApproverRepository()

    async def createApprovalFlow(
            self,
            *,
            conn: AsyncConnection,
            request_data: CreateApprovalFlowRequest,
            usergroup_id: int,
            created_by: int,
            list_of_sm_approver_ids: list
    ) -> int:

        approval_flow_id = await self.__approval_flow_repository.createApprovalFlow(
            conn=conn,
            smId=request_data.smId,
            name=request_data.name,
            usergroup_id=usergroup_id,
            created_by=created_by,
        )

        list_of_approval_step_id = []
        for count, _ in enumerate(request_data.steps):
            approval_step_id = await self.__approval_step_repository.createApprovalStep(conn=conn,
                                                                                        approval_flow_id=approval_flow_id,
                                                                                        created_by=created_by)
            list_of_approval_step_id.append(approval_step_id)
            for sm_approver_id in list_of_sm_approver_ids[count]:
                _ = await self.__step_approver_repository.createStepApprover(conn=conn,
                                                                             approval_step_id=approval_step_id,
                                                                             sm_approver_id=sm_approver_id,
                                                                             created_by=created_by)

        initial_step_id = list_of_approval_step_id[0]
        await self.__approval_flow_repository.setInitialStepIdOfApprovalFlow(conn=conn,
                                                                             initial_step_id=initial_step_id,
                                                                             approval_flow_id=approval_flow_id)

        for approval_step_id in list_of_approval_step_id[:-1]:
            next_step_id = approval_step_id + 1

            await self.__approval_step_repository.setNextStepIdOfApprovalStep(conn=conn,
                                                                              approval_step_id=approval_step_id,
                                                                              next_step_id=next_step_id)

        return approval_flow_id

    async def checkApprovalFlowExistWithName(self, *, conn: AsyncConnection, smid: int, name: str) -> bool:
        
        return await self.__approval_flow_repository.checkApprovalFlowExistWithName(
            conn=conn, name=name, smid=smid
        )

    async def listApprovalFlowBySmId(self, conn, smid) -> List:
        approval_flow_info = []
        approval_flow = await self.__approval_flow_repository.listApprovalFlow(conn=conn, smid=smid)

        for item in approval_flow:
            approval_flow_details = ListApprovalFlowDetailResponse(
                **{
                    key: getattr(item, key, None)
                    for i, key in enumerate(
                        ListApprovalFlowDetailResponse.__fields__.keys()
                    )
                }
            ).__dict__

            """fetching the list of steps for the approval flow"""
            approval_flow_steps = (
                await self.__approval_step_repository.fetchApprovalFlowSteps(
                    conn=conn, approval_flow_id=approval_flow_details["id"]
                )
            )

            """fetching the list of approvers for the approval flow steps"""
            approval_flow_details["steps"] = []
            for step in approval_flow_steps:
                approval_step_info = dict()
                step_approvers_details = (
                    await self.__approval_flow_repository.get_approvers_for_current_step(
                        conn=conn, step_id=step.id
                    )
                )

                approval_step_info["stepId"] = step.id
                approval_step_info["stepApprovers"] = helper.create_step_approver_object(step_approvers_details)
                approval_flow_details["steps"].append(approval_step_info)

            approval_flow_info.append(approval_flow_details)
        
        return approval_flow_info

    async def fetch_active_approval_flow_details(self, conn: AsyncConnection, approval_flow_id: int) -> ApprovalFlow:
        data = await self.__approval_flow_repository.fetch_active_approval_flow_details(
            conn=conn, approval_flow_id=approval_flow_id
        )

        approval_flow_details = ApprovalFlowDetailResponse(
            **{
                key: getattr(data, key, None)
                for i, key in enumerate(
                    ApprovalFlowDetailResponse.__fields__.keys()
                )
            }
        ).__dict__

        """fetching the list of steps for the approval flow"""
        approval_flow_steps = (
            await self.__approval_step_repository.fetchApprovalFlowSteps(
                conn=conn, approval_flow_id=approval_flow_id
            )
        )

        """fetching the list of approvers for the approval flow steps"""
        approval_flow_details["steps"] = []
        for step in approval_flow_steps:
            approval_step_info = dict()
            step_approvers_details = (
                await self.__approval_flow_repository.get_approvers_for_current_step(
                    conn=conn, step_id=step.id
                )
            )

            approval_step_info["stepId"] = step.id
            approval_step_info["stepApprovers"] = helper.create_step_approver_object(step_approvers_details)
            approval_flow_details["steps"].append(approval_step_info)

        return approval_flow_details
    
    async def update_approval_flow(
            self,
            *,
            conn: AsyncConnection,
            approval_flow_id: int,
            kwargs: Dict
        ):
        return await self.__approval_flow_repository.update_approval_flow(
            conn=conn, approval_flow_id=approval_flow_id, kwargs=kwargs
        )