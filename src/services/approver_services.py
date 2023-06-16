from sqlalchemy.ext.asyncio import AsyncConnection

from external_api_clients import V2APIClient
from repositories.mysql_db.implementation import ApproverRepository
from typing import List, Union, Dict

from repositories.mysql_db.models import SmApprover
from utils.initialize_common_utils import common_utils_ins
from dtos.response.entities import (
    ApproverDetailResponse,
    GetSmApproverListResponse,
)
from typing import Optional
from utils.constant import PARAMS, USER_TYPE


class ApproverServices:
    def __init__(self):
        self.__approver_repository = ApproverRepository()
        self.__v2_api_client = V2APIClient()
        self.__log = common_utils_ins.logger

    # TODO: This function is called in a loop, optimize it later
    # TODO: Function needs to be renamed as well
    async def register_approver_as_collaborator(self, *, email_id, usergroup_id, invited_by):
        resp = self.__v2_api_client.register_collaborator(email_id, usergroup_id, invited_by)
        return resp["data"][email_id]


    def add_emails(self, approver_details):
        if not approver_details:
            return []
        returnval = []
        ids = []
        for row in approver_details:
            ids.append(str(row.approverExternalId))
        params_str = PARAMS.COLLABORATOR_PARAMS + '=' + ','.join(ids)
        return self.__v2_api_client.get_collaborators_emails(params_str)

    async def get_sm_collaborator_list(
        self,
        *,
        conn: AsyncConnection,
        smids: List,
    ) -> List:
        
        approver_details = await self.__approver_repository.get_sm_collaborator_list(
            conn=conn, smids=smids,
        )
        approver_collab_map = {}
        for row in approver_details:
            approver_collab_map[row.approverExternalId] = row.approverId
        collab_details = self.add_emails(approver_details)
        approver_detail_list = []
        for approver in collab_details:

            approver_info = GetSmApproverListResponse(
                id=approver_collab_map[approver["id"]], email=approver["emailid"]
            ).__dict__
            approver_detail_list.append(approver_info)

        return approver_detail_list
   
    async def checkSmApproversExist(
        self,
        *,
        connection: AsyncConnection,
        smid: int,
        list_of_approver_ids_details: List,
        list_of_sm_approver_ids: list,
    ) -> List:
        # Only checks for collaborators that have already been registered
        for approver_id_detail in list_of_approver_ids_details:
            approver_id = approver_id_detail["approver_id"]
            sm_approver_details = (
                await self.__approver_repository.fetchSmApproverDetails(
                    conn=connection,
                    smid=smid,
                    approver_id=approver_id,
                    approver_type=USER_TYPE.COLLABORATOR
                )
            )

            list_of_sm_approver_ids[approver_id_detail["step"]].append(sm_approver_details.id)

        return list_of_sm_approver_ids

    # TODO: Combine this function with createApproverForHiverUsers() below
    async def createApproverForEmails(
        self,
        *,
        connection: AsyncConnection,
        smid: int,
        approver_type: str,
        userid:int,
        list_of_collaborator_email_details: list,
        list_of_sm_approver_ids: list,
        usergroup_id: int
    ) -> List:

        for email_detail in list_of_collaborator_email_details:
            email = email_detail["approver_email"]

            approver_details = (
                await self.__approver_repository.fetchApproverDetails(
                    conn=connection,
                    approver_type=approver_type,
                    email=email,
                    sm_id=smid
                )
            )
            if approver_details:
                approver_id = approver_details["id"]
                sm_approver_details = (
                    await self.__approver_repository.fetchSmApproverDetails(
                        conn=connection, smid=smid, approver_id=approver_id, approver_type=USER_TYPE.COLLABORATOR
                    )
                )

                if not sm_approver_details:
                    # TODO: Explain why sm_approver_details don't exist even when approver_details exist
                    collaborator_id = await self.register_approver_as_collaborator(email_id=email,
                                                                                   usergroup_id=usergroup_id,
                                                                                   invited_by=userid)
                    sm_approver_id = (
                        await self.__approver_repository.createSmApprover(
                            conn=connection,
                            smid=smid,
                            approver_id=approver_id,
                            approver_external_id=collaborator_id,
                            approver_type=USER_TYPE.COLLABORATOR
                        )
                    )
                    list_of_sm_approver_ids[email_detail["step"]].append(
                        sm_approver_id
                    )
                    
                else:
                    list_of_sm_approver_ids[email_detail["step"]].append(
                        sm_approver_details.id
                    )

            else:
                collaborator_id = await self.register_approver_as_collaborator(email_id=email,
                                                                               usergroup_id=usergroup_id,
                                                                               invited_by=userid)

                approver_id = await self.__approver_repository.createApprover(conn=connection)

                sm_approver_id = await self.__approver_repository.createSmApprover(
                    conn=connection,
                    smid=smid,
                    approver_id=approver_id,
                    approver_external_id=collaborator_id,
                    approver_type=USER_TYPE.COLLABORATOR
                )

                list_of_sm_approver_ids[email_detail["step"]].append(sm_approver_id)

        return list_of_sm_approver_ids
        
    async def createApproverForHiverUsers(
        self,
        *,
        connection: AsyncConnection,
        smid: int,
        approver_type: str,
        list_of_hiver_approver_external_ids_details: list,
        list_of_sm_approver_ids: list,
    ) -> List:
        for (
            approver_external_id_detail
        ) in list_of_hiver_approver_external_ids_details:

            approver_details = (
                await self.__approver_repository.fetchApproverDetails(
                    conn=connection,
                    approver_external_id=approver_external_id_detail["approver_id"],
                    approver_type=approver_type,
                    sm_id=smid
                )
            )
            if approver_details:
                
                approver_id = approver_details["id"]
                sm_approver_details = (
                    await self.__approver_repository.fetchSmApproverDetails(
                        conn=connection, smid=smid, approver_id=approver_id, approver_type=USER_TYPE.SM_USER
                    )
                )
                if not sm_approver_details:
                    self.__log.info(f"Creating SM Approver for smid {smid} and approver id {approver_id}")
                        
                    """create entry in SmApprover Table"""
                    sm_approver_id = (
                        await self.__approver_repository.createSmApprover(
                            conn=connection,
                            smid=smid,
                            approver_id=approver_id,
                            approver_type=USER_TYPE.SM_USER,
                            approver_external_id=approver_external_id_detail["approver_id"]
                        )
                    )
                    list_of_sm_approver_ids[
                        approver_external_id_detail["step"]
                    ].append(sm_approver_id)

                else:
                    list_of_sm_approver_ids[
                        approver_external_id_detail["step"]
                    ].append(sm_approver_details[0])

                    self.__log.info(f"SM Approver found for smid {smid} and approver id {approver_id}")
                    pass
            else:

                approver_id = await self.__approver_repository.createApprover(conn=connection)

                sm_approver_id = await self.__approver_repository.createSmApprover(
                    conn=connection,
                    smid=smid,
                    approver_id=approver_id,
                    approver_type=approver_type,
                    approver_external_id=approver_external_id_detail["approver_id"]
                )
                list_of_sm_approver_ids[approver_external_id_detail["step"]].append(
                    sm_approver_id
                )

        return list_of_sm_approver_ids

    async def fetchApproverDetails(self, *, conn: AsyncConnection, sm_approver_ids: list,
                                   approver_external_id: Union[int, None] = None,
                                   approver_type: str = None, sm_id: int = None) -> List:

        # Note: There is a hard dependency on approver_type being COLLABORATOR here.
        # Right now, approver_type is always passed as COLLABORATOR from the caller, but if you're changing it,
        # you'll need to make changes to the order of the if-else clauses inside fetchApproverDetails()
        approver_details = await self.__approver_repository.fetchApproverDetails(
            conn=conn,
            sm_approver_ids=sm_approver_ids,
            approver_external_id=approver_external_id,
            approver_type=approver_type,
            sm_id=sm_id
        )
        approvers_info = []
        if approver_details:
            for approver in approver_details:
                approver = ApproverDetailResponse(
                    **{
                        key: approver[i]
                        for i, key in enumerate(
                            ApproverDetailResponse.__fields__.keys()
                        )
                    }
                ).__dict__
                approvers_info.append(approver)

        return approvers_info

    async def getSmApproverIdForCurrentStep(self, *, conn: AsyncConnection, approver_external_id: int,
                                            approver_type: str, current_step_id: int) -> int:

        return await self.__approver_repository.getSmApproverIdForCurrentStep(
            conn=conn,
            approver_external_id=approver_external_id,
            approver_type=approver_type,
            current_step_id=current_step_id
        )

    async def fetch_sm_approver_details(self, *, conn: AsyncConnection, sm_id: int, approver_type: str,
                                        approver_external_id: Optional[int] = None) -> SmApprover:
        return await self.__approver_repository.fetchSmApproverDetails(conn=conn,
                                                                       smid=sm_id,
                                                                       approver_external_id=approver_external_id,
                                                                       approver_type=approver_type)

    async def update_approver_sm_details(self, *, conn: AsyncConnection, sm_approver_id: int, approver_type: str,
                                         approver_external_id: int) -> None:
        return await self.__approver_repository.update_approver_sm_details(conn=conn,
                                                                           sm_approver_id=sm_approver_id,
                                                                           approver_type=approver_type,
                                                                           approver_external_id=approver_external_id)
