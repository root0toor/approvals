import re
import sys
import traceback
import typing

from auth.auth_bearer import JWTBearer
from auth.auth_handler import AuthHandler
from utils.constant import USER_TYPE
from utils.initialize_common_utils import common_utils_ins
from typing import List

def validate_email(email):
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if not re.match(email_regex, email):
        return False
    return True


async def getUserToken(request):
    auth_handler = AuthHandler(
        JWT_SECRET_KEY=common_utils_ins.config.hiver_config.JWT_SECRET_KEY,
        JWT_ALGORITHM=common_utils_ins.config.hiver_config.JWT_ALGORITHM,
    )
    jwt_bearer = JWTBearer(
        auth_handler=auth_handler,
    )
    token = await jwt_bearer.handle(request=request)
    return token


def decodeUserToken(token):
    auth_handler = AuthHandler(
        JWT_SECRET_KEY=common_utils_ins.config.hiver_config.JWT_SECRET_KEY,
        JWT_ALGORITHM=common_utils_ins.config.hiver_config.JWT_ALGORITHM,
    )
    user_details = auth_handler.decodeJwt(token)
    return user_details


def errorTracking():
    exc_type, exc_value, exc_tb = sys.exc_info()
    err_stacktrace = "".join(
        traceback.format_exception(exc_type, exc_value, exc_tb)
    )
    return err_stacktrace


def create_step_approver_object(step_approvers_details):
    step_approvers = []
    for instance in step_approvers_details:
        each_step_approver = {
            "type": instance.approverType,
            "id": instance.approverExternalId if instance.approverType == USER_TYPE.SM_USER else instance.id
        }
        step_approvers.append(each_step_approver)
    return step_approvers


async def get_db_connection_dependency() -> typing.AsyncIterator:
    """
    Begin a transaction and return a connection from the DB connection pool
    Once the dependent entity finishes processing, the connection is closed
    """
    engine = common_utils_ins.mysql_client
    connection = engine.connect()
    connection = await connection.start()
    try:
        yield connection
    finally:
        await connection.close()
            
async def get_valid_approval_step_ids(completed_histories: List) -> List:
    valid_approval_step_ids = []
    for completed_history in completed_histories:
        # -1 is the stepId for the INITIATED history record, which doesn't have any approvers attached
        if completed_history.stepId != -1:
            valid_approval_step_ids.append(completed_history.stepId)
    return valid_approval_step_ids
