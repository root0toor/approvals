import json

from comlib.kafka.base_consumer import KafkaConsumerBase
from configs.config import Config
from schemas.events import ApprovalToggleSchema
from utils.initialize_common_utils import common_utils_ins


class ApprovalToggleConsumer(KafkaConsumerBase):

    def __init__(self, config: Config, topic: str):
        super().__init__(config, topic)
        self.__log = common_utils_ins.logger

    async def parse(self, messages, headers_list):
        from services import ApprovalToggleService

        for message in messages:
            print(f"Received message: {message}")
            message = json.loads(message)
            try:
                validated_message = ApprovalToggleSchema(**message)
            except Exception:
                self.__log.exception(f"Error while parsing {message}")
                return

            try:
                await ApprovalToggleService().toggle(**validated_message.dict())
                self.__log.debug(f"Successfully toggled for {validated_message.sm_id}")
            except Exception:
                self.__log.exception(f"Exception while toggling for {validated_message.sm_id}")
