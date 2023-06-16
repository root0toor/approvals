from fastapi import Request
from utils.constant import USER_TYPE
from utils import helper
from utils.constant import SM_ADMIN_PERMISSION
from exceptions.errors import AuthorizationError
from utils.initialize_common_utils import common_utils_ins


class ActiveUser:
    def __init__(self) -> None:
        self.__user_details = None

    def getUserDetails(self):
        return self.__user_details

    async def setUserDetails(self, request: Request):
        token = await helper.getUserToken(request=request)
        self.__user_details = helper.decodeUserToken(token=token)
        if not self._isValidUser():
            raise AuthorizationError

    """To get user type"""

    def getUserType(self):
        user_type = None
        if {"smids", "is_admin", "usergroupid", "userid"}.issubset(self.__user_details.keys()):
            user_type = USER_TYPE.SM_USER
        elif self.__user_details.get("collaboratorid"):
            user_type = USER_TYPE.COLLABORATOR
        return user_type

    """To check valid user"""

    def _isValidUser(self):
        if self.getUserType():
            return True
        return False


class ActiveHiverUser(ActiveUser):
    def __init__(self) -> None:
        super().__init__()
        self.__log = common_utils_ins.logger

    def _hasAccessToSM(self, smid: int):
        user_details = self.getUserDetails()
        if int(smid) in user_details.get("smids"):
            self.__log.info("User has access to sm")
            return True
        self.__log.info("User has not access to sm")
        return False

    def hasAccessToSMConfiguration(self, smid: int):
        user_details = self.getUserDetails()
        is_admin = False

        user_type = self.getUserType()
        if user_type != USER_TYPE.SM_USER:
            self.__log.info("User is not a hiver user")
            return is_admin

        is_admin = user_details.get("is_admin")
        if is_admin:
            self.__log.info("User is of type admin")
            return is_admin

        """checking permission for sm admin"""
        if SM_ADMIN_PERMISSION.SM_FULL in user_details.get("permissions"):
            self.__log.info(f"User has '{SM_ADMIN_PERMISSION.SM_FULL}' permission")
            is_admin = True

        elif SM_ADMIN_PERMISSION.SM_PARTIAL in user_details.get("permissions"):
            self.__log.info(f"User has '{SM_ADMIN_PERMISSION.SM_PARTIAL}' permission")
            has_access_to_sm = self._hasAccessToSM(smid=smid)
            if has_access_to_sm:
                is_admin = True
                self.__log.info("User has access to SM configuration")
            else:
                self.__log.info("User does not have access to SM configuration")
        else:
            self.__log.info(f"User has not necessary permissions")

        return is_admin

    def isSmMember(self, smid: int):
        is_sm_member = False
        user_type = self.getUserType()

        # TODO: Fix this later
        if user_type == USER_TYPE.COLLABORATOR:
            return True

        if user_type != USER_TYPE.SM_USER:
            self.__log.info("User is not a hiver user")
            return is_sm_member
        has_access_to_sm = self._hasAccessToSM(smid=smid)
        if has_access_to_sm:
            is_sm_member = True
            self.__log.info("User is a SM member")
        else:
            self.__log.info("User is not a SM member")
        return is_sm_member


class ActiveApprover(ActiveUser):

    def getApproverDetails(self):
        user_details = self.getUserDetails()
        if user_details.get("collaboratorid"):
            approver_external_id = user_details.get("collaboratorid")
        else:
            approver_external_id = user_details.get("userid")

        approver_type = self.getUserType()
        return approver_external_id, approver_type
