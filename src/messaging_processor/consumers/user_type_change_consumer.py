import json

import sentry_sdk

from comlib.kafka.base_consumer import KafkaConsumerBase
from schemas.events import UserRemovedSchema, UserAddedSchema
from utils.constant import EventType
from utils.initialize_common_utils import common_utils_ins
from configs.config import Config


class UserTypeChangeConsumer(KafkaConsumerBase):

    def __init__(self, config: Config, topic: str):
        super().__init__(config, topic)
        self.__engine = common_utils_ins.mysql_client
        self.__log = common_utils_ins.logger

    async def parse(self, messages, headers_list):
        from services.user_type_change import UserTypeChange

        for message, headers in zip(messages, headers_list):
            message = json.loads(message)

            event_type = headers.get("event_type", "")

            # Get the event schema and appropriate function for the event type
            if event_type == EventType.USER_REMOVED_FROM_SHAREDMAILBOX:
                event_schema = UserRemovedSchema
                function_name = UserTypeChange.REMOVED_USER_FUNCTION
            elif event_type == EventType.USER_ADDED_INTO_SHAREDMAILBOX:
                event_schema = UserAddedSchema
                function_name = UserTypeChange.ADDED_USER_FUNCTION
            else:
                self.__log.warning(f"Unsupported event type {event_type} received for user type change")
                return

            try:
                validated_message = event_schema(**message)
            except Exception:
                self.__log.exception(f"Error while parsing {message}")
                return

            try:
                func = getattr(UserTypeChange, function_name)
                async with self.__engine.connect() as connection:
                    args = validated_message.dict()
                    args["conn"] = connection
                    ret = await func(UserTypeChange(), **args)
                    await connection.commit()
                if ret:
                    self.__log.info(
                        f"Successfully changed user type for {event_type} : sm_id {validated_message.sm_id} :"
                        f"user_id : {validated_message.user_id}")
                else:
                    self.__log.info(
                        f"No approver found for {event_type} : : sm_id {validated_message.sm_id} : "
                        f"user_id : {validated_message.user_id}")
            except Exception as e:
                sentry_sdk.capture_exception(e)
                self.__log.exception(
                    f"Exception while changing user type for {event_type} : sm_id {validated_message.sm_id} :"
                    f"user_id : {validated_message.user_id}")
