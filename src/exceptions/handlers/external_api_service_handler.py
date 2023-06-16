import http

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from exceptions.errors import ExternalApiServiceError
from utils.initialize_common_utils import common_utils_ins
from utils.helper import errorTracking


class ExternalApiServiceErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class ExternalApiServiceErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: ExternalApiServiceError) -> JSONResponse:
        
        response = ExternalApiServiceErrorResponse(error="EXTERNAL API SERVICE ERROR",
                                                   message=e.message,
                                                   status=http.HTTPStatus.FAILED_DEPENDENCY)

        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")
         
        return JSONResponse(
            status_code=e.status_code,
            content=response.dict(by_alias=True),
        )
