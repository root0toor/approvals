from .common_utils import CommonUtils
import os, sys
from configs import ConfigError, getConfig
from utils.constant import TIER


def initializeCommonUtils():
    tier = os.getenv("TIER", default=TIER.LOCAL).lower()
    try:
        config = getConfig(tier)
        common_utils_ins = CommonUtils(config=config)
        return common_utils_ins
    except ConfigError as e:
        print("**ERROR***", e)
        sys.exit(1)


common_utils_ins = initializeCommonUtils()
