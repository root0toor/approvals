from fastapi import FastAPI
from exceptions.handlers import (
    InputValidationErrorHandler,
    UncaughtErrorHandler,
    IntegrityErrorHandler,
    NoResultFoundErrorHandler,
    BadRequestErrorHandler,
    AuthorizationErrorHandler,
    AuthenticationErrorHandler,
    InvalidArgumentErrorHandler,
    ExternalApiServiceErrorHandler,
    DatabaseErrorHandler
)
from middlewares import ErrorMiddleware,SentryMiddleware,LogContextMiddleware


class MiddlewaresContainer:
    def __init__(
        self,
        *,
        app: FastAPI,
    ):
        input_validation_error_handler = InputValidationErrorHandler()
        invalid_argument_error_handler = InvalidArgumentErrorHandler()
        authorization_error_handler = AuthorizationErrorHandler()
        authentication_error_handler = AuthenticationErrorHandler()
        integrity_error_handler = IntegrityErrorHandler()
        no_result_found_error_handler = NoResultFoundErrorHandler()
        bad_request_error_handler = BadRequestErrorHandler()
        external_api_service_error_handler = ExternalApiServiceErrorHandler()
        uncaught_error_handler = UncaughtErrorHandler()
        database_error_handler = DatabaseErrorHandler()
        
        sentry_middleware = SentryMiddleware()
        log_context_middleware=LogContextMiddleware()

        error_middleware = ErrorMiddleware(
            app=app,
            input_validation_error_handler=input_validation_error_handler,
            invalid_argument_error_handler=invalid_argument_error_handler,
            authorization_error_handler=authorization_error_handler,
            authentication_error_handler=authentication_error_handler,
            integrity_error_handler=integrity_error_handler,
            no_result_found_error_handler=no_result_found_error_handler,
            bad_request_error_handler=bad_request_error_handler,
            external_api_service_error_handler=external_api_service_error_handler,
            uncaught_error_handler=uncaught_error_handler,
            database_error_handler=database_error_handler
        )
        
        app.middleware("http")(sentry_middleware.handle)
        app.middleware("http")(log_context_middleware.handle)
        app.middleware("http")(error_middleware.handle)
