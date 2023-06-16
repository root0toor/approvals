import json

from comlib.kafka.base_consumer import KafkaConsumerBase
from schemas.events import SMDeletionSchema
from utils.initialize_common_utils import common_utils_ins
from configs.config import Config
from utils.constant import ConsumerEventTypes


class SMDeletionConsumer(KafkaConsumerBase):

    def __init__(self, config: Config, topic: str):
        super().__init__(config, topic)
        self.__log = common_utils_ins.logger
        self.__engine = common_utils_ins.mysql_client

    async def parse(self, messages, headers_list):
        from services import SMDeletionService

        for message, headers in zip(messages, headers_list):
            print(f"Received message: {message}")
            message = json.loads(message)
            
            if headers.get('event_type', '') != ConsumerEventTypes.SHARED_MAILBOX_REMOVAL:
                return
            
            try:
                validated_message = SMDeletionSchema(**message)
            except Exception:
                self.__log.exception(f"Error while parsing {message}")
                return

            connection = self.__engine.connect()
            try:
                await connection.__aenter__()
                async with connection.begin() as transaction:
                    try:
                        await SMDeletionService().process_sm_deletion_event(connection=connection, sm_ids=[validated_message.sm_id])
                        await transaction.commit()
                    except Exception as e:
                        self.__log.exception(f"Exception during SM deletion processing for {validated_message.sm_id} : {e}")
                        await transaction.rollback()
                        raise e
            except Exception as e:
                self.__log.exception(f"Error while processing message: {message}")
                raise e
            finally:
                await connection.close()
