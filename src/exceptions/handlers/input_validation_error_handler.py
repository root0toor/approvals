from typing import Any, Dict, List, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils.initialize_common_utils import common_utils_ins
from exceptions.errors import InputValidationError
from utils.helper import errorTracking


class ValidationErrorResponse(BaseModel):
    status: int = 0
    error: str
    message: str


class InputValidationErrorHandler:
    def __init__(self):
        self.__log = common_utils_ins.logger

    async def handle(self, request: Request, e: InputValidationError) -> JSONResponse:
        response = ValidationErrorResponse(error="INPUT_VALIDATION_ERROR", message=e.message)

        self.__log.error(f"{response.error} : {response.message} : {errorTracking()}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.dict(by_alias=True),
        )
