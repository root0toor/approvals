from messaging_processor.consumers import ApprovalToggleConsumer, UserTypeChangeConsumer, SMDeletionConsumer, \
    UGDeletionConsumer
from utils.constant import ConsumerTopic
from utils.initialize_common_utils import common_utils_ins
import asyncio


class KafkaContainer:

    @staticmethod
    async def initialize(config=None):
        __config = config
        approval_toggle_consumer = ApprovalToggleConsumer(__config, topic=ConsumerTopic.APPROVAL_TOGGLE)
        approval_toggle_consumer.initialize()
        user_type_change_consumer = UserTypeChangeConsumer(__config, topic=ConsumerTopic.SHARED_MAILBOX_USER_REMOVED)
        user_type_change_consumer.initialize()
        sm_deletion_consumer = SMDeletionConsumer(__config, topic=ConsumerTopic.SHARED_MAILBOX_STATE)
        sm_deletion_consumer.initialize()
        ug_deletion_consumer = UGDeletionConsumer(__config, topic=ConsumerTopic.USER_GROUP_USER_STATE)
        ug_deletion_consumer.initialize()
        consumers = [approval_toggle_consumer, user_type_change_consumer, sm_deletion_consumer, ug_deletion_consumer]
        for consumer in consumers:
            asyncio.create_task(consumer.consume(callback=KafkaContainer.log_consumption_completion))

    @staticmethod
    async def log_consumption_completion(messages):
        log = common_utils_ins.logger
        log.debug("Consumed the following messages successfully: {}", format(messages))
        print("Consumed the following messages successfully: {}", format(messages))