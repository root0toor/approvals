import logging
import sys

from logstash import TCPLogstashHandler

from configs.config import LogChannel, LogLevel

from .formatter import CustomJSONFormatter


class CustomAPILogger:
    def __init__(self, config=None) -> None:
        self.__config = config
        self.__logger = None
        self.__log_level = LogLevel.DEBUG.value
        # self.__db_logger = logging.getLogger('sqlalchemy')

    def __set_logger(self) -> None:
        self.__logger = logging.getLogger(self.__config.app_name)
        self.__set_handlers()
        self.__logger.setLevel(self.__log_level)
        # self.__db_logger.setLevel(self.__log_level)

    def __set_handlers(self):
        if self.__config is None:
            all_channels = [LogChannel.STDOUT.value]
        else:
            all_channels = self.__config.log_config.LOG_CHANNEL.split(",")
            self.__log_level = getattr(logging, self.__config.log_config.LOG_LEVEL)

        for channel in all_channels:
            if channel == LogChannel.STDOUT.value:
                handler = logging.StreamHandler(sys.stdout)
            elif channel == LogChannel.FILE.value:
                handler = logging.handlers.TimedRotatingFileHandler(
                    self.__config.app_name + ".log", when="D", interval=1, backupCount=3
                )
            elif channel == LogChannel.LOGSTASH.value:
                handler = TCPLogstashHandler(
                    host=self.__config.log_config.LOGSTASH_HOST,
                    port=self.__config.log_config.LOGSTASH_PORT,
                    version=1,
                )

            handler.setFormatter(CustomJSONFormatter())
            self.__logger.addHandler(handler)
            # self.__db_logger.addHandler(handler)

    def get_logger(self):
        if self.__logger is None:
            self.__set_logger()
        return self.__logger
