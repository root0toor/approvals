from .config import Config
from .config_error import ConfigError
from .local import getLocalConfig
from .production import getProductionConfig
from utils.constant import TIER


def getConfig(tier: str) -> Config:
    try:
        if tier == TIER.LOCAL:
            config = getLocalConfig()
        elif tier == TIER.PRODUCTION:
            config = getProductionConfig()
        else:
            raise ConfigError("No Proper TIER found")
    except Exception as e:
        raise ConfigError(e.args)
    print(config)
    return config
