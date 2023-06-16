import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", [])
V2_BASE_URL = os.getenv("V2_INTERNAL_URL", "")
V2_X_API_KEY = os.getenv("V2_X_API_KEY", "")
LABEL_MANAGER_BASE_URL = os.getenv("LABEL_MANAGER_BASE_URL", "")
APP_ENV = os.getenv("APP_ENV", "")
