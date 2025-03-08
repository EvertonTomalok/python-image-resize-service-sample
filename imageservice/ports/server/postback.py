import logging
from typing import Dict

from fastapi import FastAPI

LOGGER = logging.getLogger("POSTBACK-SERVER")

app = FastAPI()


@app.post("/postback")
async def create_item(item: Dict):
    LOGGER.info(f"Message received -> {item}")
    return item
