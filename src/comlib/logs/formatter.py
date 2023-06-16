import json
import logging

from .log_context import LogContext


class CustomJSONFormatter(logging.Formatter):
    def __init__(self, **kwargs):
        datefmt = kwargs.pop("datefmt", None)
        if not datefmt:
            datefmt = "%Y-%m-%dT%H:%M:%SZ"
        super(CustomJSONFormatter, self).__init__(datefmt=datefmt)

        self.format_dict = {
            "@timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "location": "(%(filename)s)<%(funcName)s:%(lineno)d>",
            "app_name": "%(name)s",
        }
        self.format_dict.update(kwargs)

    def format(self, record):
        record_dict = record.__dict__
        record_dict["asctime"] = self.formatTime(record, self.datefmt)
        log_dict = {k: v % record_dict for k, v in self.format_dict.items() if v}
        log_dict["message"] = record.getMessage()
        log_dict.update(LogContext._as_dict())
        LogContext._reset()
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            log_dict["exceptions"] = record.exc_text

        return json.dumps(log_dict)
