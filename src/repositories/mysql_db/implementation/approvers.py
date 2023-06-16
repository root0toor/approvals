from sqlalchemy.ext.asyncio import AsyncConnection

from ..models import ApproverBaseColumn, Approver, SmApproverBaseColumn, SmApprover
from sqlalchemy import select, and_, desc
from typing import Dict, Tuple, List, Union
from utils.initialize_common_utils import common_utils_ins
from utils.constant import USER_TYPE
from typing import Optional
from sqlalchemy.sql import text
from exceptions.errors import InvalidArgumentError

class ApproverRepository:
    def __init__(self) -> None:
        self.__log = common_utils_ins.logger

    # Create a dummy Approver entry with NULL email
    # The Approver table will be deprecated later
    async def createApprover(self, conn: AsyncConnection) -> int:
        query = Approver.insert().values(
            {
                ApproverBaseColumn.EMAIL.value: None
            }
        )
        result = await conn.execute(query)
        return result.lastrowid

    async def createSmApprover(
        self,
        conn: AsyncConnection,
        smid: int,
        approver_id: Union[int, None],
        approver_type: str,
        approver_external_id: Union[int, None],
    ) -> int:

        query = SmApprover.insert().values(
            {
                SmApproverBaseColumn.APPROVER_ID.value: approver_id,
                SmApproverBaseColumn.SMID.value: smid,
                SmApproverBaseColumn.APPROVER_EXTERNAL_ID.value: approver_external_id,
                SmApproverBaseColumn.APPROVER_TYPE.value: approver_type
            }
        )

        result = await conn.execute(query)
        return result.lastrowid

    async def fetchApproverDetails(
        self,
        conn: AsyncConnection,
        approver_type: Optional[str] = None,
        sm_approver_ids: Optional[list] = None,
        email: Optional[str] = None,
        approver_external_id: Optional[int] = None,
        sm_id: Optional[int] = None
    ) -> Tuple:

        if approver_type == USER_TYPE.SM_USER and approver_external_id:
            self.__log.info(f"Fetching approver details for approver type '{USER_TYPE.SM_USER}' and approver external id {approver_external_id}")
            ins = select(
                Approver.c.id,
                Approver.c.email,
                SmApprover.c.approverExternalId,
                SmApprover.c.approverType,
            ).\
                select_from(Approver.join(SmApprover, SmApprover.c.approverId == Approver.c.id)).\
                where(
                and_(
                    SmApprover.c.approverExternalId == approver_external_id,
                    SmApprover.c.approverType == approver_type,
                    SmApprover.c.smId == sm_id
                )
            )
        elif approver_type == USER_TYPE.COLLABORATOR and email:
            self.__log.info(f"Fetching approver details for approver type '{USER_TYPE.COLLABORATOR}' and approver external id {email}")
            ins = select(
                Approver.c.id,
                Approver.c.email,
                SmApprover.c.approverExternalId,
                SmApprover.c.approverType,
            ).\
                select_from(Approver.join(SmApprover, SmApprover.c.approverId == Approver.c.id)).\
                where(
                and_(
                    Approver.c.email == email,
                    SmApprover.c.approverType == approver_type,
                    SmApprover.c.smId == sm_id
                )
            )
        elif sm_approver_ids:
            self.__log.info(f"Fetching approver details for sm approver ids {sm_approver_ids}")
            ins = (
                select(
                    Approver.c.id,
                    Approver.c.email,
                    SmApprover.c.approverExternalId,
                    SmApprover.c.approverType,
                    SmApprover.c.id,
                )
                .select_from(
                    Approver.join(
                        SmApprover, SmApprover.c.approverId == Approver.c.id
                    )
                )
                .where(SmApprover.c.id.in_(sm_approver_ids))
            )
            if approver_external_id:
                ins = ins.where(
                    and_(
                        SmApprover.c.approverExternalId == approver_external_id,
                        SmApprover.c.approverType == approver_type,
                        SmApprover.c.smId == sm_id
                    )
                )
        else:

            raise InvalidArgumentError("There is an issue with input data")

        result = await conn.execute(ins)

        if result.rowcount != 0:

            if sm_approver_ids:

                return result.all()

            return result.one()

    async def fetchSmApproverDetails(
        self,
        smid: int,
        conn: AsyncConnection,
        approver_external_id: Optional[int] = None,
        approver_id: Optional[int] = None,
        approver_type: Optional[str] = None
    ) -> Union[Tuple, None]:
            
        if smid and approver_external_id:
            self.__log.info(f"Fetching SM approver details for smid {smid} and sm collaborator id {approver_external_id}")
            ins = select(
                SmApprover.c.id,
                SmApprover.c.approverId,
                SmApprover.c.smId,
                SmApprover.c.approverExternalId,
            ).where(
                and_(
                    SmApprover.c.approverExternalId == approver_external_id,
                    SmApprover.c.smId == smid,
                    SmApprover.c.active == True,
                    SmApprover.c.approverType == approver_type
                )
            )
        elif smid and approver_id:
            self.__log.info(f"Fetching SM approver details for smid {smid} and approver id {approver_id}")
            ins = select(
                SmApprover.c.id,
                SmApprover.c.approverId,
                SmApprover.c.smId,
                SmApprover.c.approverExternalId,
            ).where(
                and_(
                    SmApprover.c.approverId == approver_id,
                    SmApprover.c.smId == smid,
                    SmApprover.c.active == True,
                    SmApprover.c.approverType == approver_type
                )
            )
        else:
            return

        result = await conn.execute(ins)
            
        return result.first()

    async def get_sm_collaborator_list(
        self,
        conn: AsyncConnection,
        smids: List,
    ) -> List:

        query = (
            select(SmApprover)
            .select_from(
                Approver.join(
                    SmApprover, SmApprover.c.approverId == Approver.c.id
                )
            )
            .where(
                and_(
                    SmApprover.c.smId.in_(smids),
                    SmApprover.c.active.is_(True),
                    SmApprover.c.approverExternalId.is_not(None),
                    SmApprover.c.approverType == USER_TYPE.COLLABORATOR
                )
            )
        )

        result = await conn.execute(query)

        return result.all()
            
    async def getSmApproverIdForCurrentStep(
        self,
        conn: AsyncConnection,
        approver_external_id: int,
        approver_type:str,
        current_step_id:int
    ) -> int:

        self.__log.info(f"Fetching sm approver id for the step {current_step_id}")

        # TODO: Rewrite this using SQLAlchemy ORM
        query = f'select SmApprover.id from Approver ' \
                f'INNER JOIN SmApprover ON Approver.id = SmApprover.approverId ' \
                f'INNER JOIN StepApprover ON StepApprover.smApproverId = SmApprover.id ' \
                f'where SmApprover.approverExternalId = {approver_external_id} ' \
                f'and SmApprover.approverType = "{approver_type}" ' \
                f'and StepApprover.approvalStepId = {current_step_id}'
        print('query is ', query)
        result = await conn.execute(text(query))
        if result.rowcount != 0:
            return result.one()[0]
        return None

    async def update_approver_sm_details(self, *, conn: AsyncConnection, sm_approver_id: int, approver_type: str,
                                         approver_external_id: int):
        query = (
            SmApprover.update()
            .where(
                SmApprover.c.id == sm_approver_id,
            )
            .values(
                {
                    SmApproverBaseColumn.APPROVER_TYPE.value: approver_type,
                    SmApproverBaseColumn.APPROVER_EXTERNAL_ID.value: approver_external_id
                }
            )
        )

        await conn.execute(query)
