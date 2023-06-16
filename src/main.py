import sys
from ddtrace import patch
from fastapi import FastAPI
from containers import Container
from fastapi.middleware.cors import CORSMiddleware
from utils.initialize_common_utils import common_utils_ins
from comlib.logs import CustomAPILogger
import os
import asyncio

from configs.env import APP_ENV
from utils.constant import TIER

if APP_ENV == TIER.PRODUCTION:
    patch(fastapi=True)

app = FastAPI()

CORS_ALLOWED_ORIGINS = ["v2{}.hiver.space".format(APP_ENV),
                        "https://v2.hiverhq.com",
                        "https://mail.google.com",
                        "https://collab.hiverhq.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(startup())

async def startup() -> None:
    
    try:
        print("................APP STARTED................")
        container = Container(app=app)
        await container.initialize(common_utils_ins.config)
    except Exception as err:
        logger = CustomAPILogger(common_utils_ins.config).get_logger()
        logger.exception("APP_INITIATION_FAILED: Unable to startup the app")
        sys.exit(1)
