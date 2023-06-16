import os
import sys
from typing import Awaitable, Callable, Dict, Optional

import sentry_sdk
from fastapi import Request, Response
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from exceptions.errors import AuthenticationError, AuthorizationError


class SentryMiddleware:
    def __init__(self):
        self.initialize()

    def initialize(self) -> None:
        """
        Initialize Sentry to capture errors
        """
        
        sentry_sdk.init(
            environment=os.getenv("TIER"),
            dsn=os.getenv("SENTRY_DSN"),
            before_send=self.before_send,
            traces_sample_rate=1.0,
        )

    async def handle(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response = await call_next(request)
        except Exception as e:
            with sentry_sdk.push_scope() as scope:
                
                userid,usergroupid,collaborator_id = (None,)*3
                
                if "jwt_payload" in request.state._state:
                    collaborator_id =  request.state.jwt_payload.get("collaborator_id")
                    if not collaborator_id:
                        userid = request.state.jwt_payload.get("userid")
                        usergroupid = request.state.jwt_payload.get("usergroupid")
                    
                scope.set_context(
                    "request",
                    {
                        "path": request.url.path,
                        "usergroupid": usergroupid,
                        "user_id": userid,
                        "collaborator_id": collaborator_id,
                    },
                )
                
                scope.user = {
                    "ip_address": request.client.host,
                }
                sentry_sdk.capture_exception(e)
            raise e
        return response

    def before_send(self, event: Dict, hint: Dict) -> Optional[Dict]:
        """
        Ignore specific types of exceptions here
        Source: https://github.com/getsentry/sentry-python/issues/149#issuecomment-434448781
        """
        if "exc_info" in hint:
            exc_type, exc_value, tb = hint["exc_info"]
        else:
            exc_type, exc_value, tb = sys.exc_info()
        if exc_value and self.is_error_ignored(exc_value):
            return None

        return event

    def is_error_ignored(self, exception: Exception) -> bool:
        """
        Check if the given exception is to be ignored
        """
        return isinstance(exception, (ExpiredSignatureError,
                                      InvalidSignatureError,
                                      AuthenticationError,
                                      AuthorizationError))
