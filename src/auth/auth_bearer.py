from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer as BaseHTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from exceptions.errors import AuthenticationError
from .auth_handler import AuthHandler

from comlib.logs import LogContext


class HTTPBearer(BaseHTTPBearer):
    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            raise AuthenticationError(message=e.detail)


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        auth_handler: AuthHandler,
        auto_error: bool = True,
    ):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.__auth_handler = auth_handler

    async def handle(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
       
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthenticationError(message="Invalid authentication scheme.")
            if not self.verifyJwt(credentials.credentials,request):
                raise AuthenticationError(message="Invalid token or expired token")
            return credentials.credentials
        else:
            raise AuthenticationError(message="Invalid authorization code.")

    def verifyJwt(self, jwtoken: str,request:Request) -> bool:
        print("********INSIDE VERFIY JWT*********")
        print(f"********JWT: {jwtoken}*********")

        is_token_valid = False
        try:
            print(f"********BEFORE CALLING DECODE JWT*********")
            payload = self.__auth_handler.decodeJwt(jwtoken)
            print(f"********Payload: {payload}*********")
            is_token_valid = True
            
            """setting up value for logging"""
            
            if payload.get("userid"):
                LogContext.userid = payload["userid"]
                LogContext.usergroupid = payload.get("usergroupid")
            elif payload.get("collaborator_id"):
                LogContext.collaborator_id = payload["collaborator_id"]
            else:
                pass
            
            """for tracking exceptions using sentry"""
            
            request.state.jwt_payload = payload
        except Exception:
            print(f"**EXCEPTION: {Exception.__traceback__}")
       
        return is_token_valid
