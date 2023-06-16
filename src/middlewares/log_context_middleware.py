from socket import gethostbyname, gethostname
from typing import Awaitable, Callable
from uuid import uuid4
from fastapi import Request, Response
from comlib.logs import LogContext


class LogContextMiddleware:
    async def handle(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        LogContext.taskid = str(uuid4())
        LogContext.host = gethostname()
        LogContext.ip = gethostbyname(LogContext.host)
        LogContext.route = request.url.path
        LogContext.method = request.method

        response = await call_next(request)
        return response
