from typing import Awaitable, Callable
from fastapi import FastAPI, Request, Response
from exceptions.errors import (
    NoResultFoundError,
    BadRequestError,
    AuthenticationError,
    AuthorizationError,
    InputValidationError,
    InvalidArgumentError,
    ExternalApiServiceError
)
from sqlalchemy.exc import IntegrityError, DBAPIError
from exceptions.handlers import (
    InputValidationErrorHandler,
    UncaughtErrorHandler,
    IntegrityErrorHandler,
    NoResultFoundErrorHandler,
    BadRequestErrorHandler,
    AuthenticationErrorHandler,
    AuthorizationErrorHandler,
    InvalidArgumentErrorHandler,
    ExternalApiServiceErrorHandler,
    DatabaseErrorHandler
)

class ErrorMiddleware:
    def __init__(
        self,
        app: FastAPI,
        input_validation_error_handler: InputValidationErrorHandler,
        invalid_argument_error_handler: InvalidArgumentErrorHandler,
        authorization_error_handler: AuthorizationErrorHandler,
        authentication_error_handler: AuthenticationErrorHandler,
        integrity_error_handler: IntegrityErrorHandler,
        no_result_found_error_handler: NoResultFoundErrorHandler,
        uncaught_error_handler: UncaughtErrorHandler,
        bad_request_error_handler: BadRequestErrorHandler,
        external_api_service_error_handler: ExternalApiServiceErrorHandler,
        database_error_handler: DatabaseErrorHandler
    ):

        app.exception_handler(InputValidationError)(
            input_validation_error_handler.handle
        )
        app.exception_handler(InvalidArgumentError)(
            invalid_argument_error_handler.handle
        )
        app.exception_handler(AuthorizationError)(authorization_error_handler.handle)
        app.exception_handler(AuthenticationError)(authentication_error_handler.handle)
        app.exception_handler(IntegrityError)(integrity_error_handler.handle)
        app.exception_handler(NoResultFoundError)(no_result_found_error_handler.handle)
        app.exception_handler(BadRequestError)(bad_request_error_handler.handle)
        app.exception_handler(ExternalApiServiceError)(external_api_service_error_handler.handle)
        app.exception_handler(DBAPIError)(database_error_handler.handle)
        self.__uncaught_error_handler = uncaught_error_handler

    async def handle(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        origin = request.headers.get("origin")
        try:
            response = await call_next(request)
            print("**AFTER MIDDLE**")
        except Exception as e:
            print("**INSIDE MIDDLE EXCEPTION**")
            response = await self.__uncaught_error_handler.handle(request=request, e=e)
            if origin:
                response.headers["access-control-allow-credentials"] = "true"
                response.headers["access-control-allow-origin"] = origin

        return response
