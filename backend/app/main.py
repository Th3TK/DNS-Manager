import logging
from fastapi import FastAPI

from app.config import ENV_CONFIG

logging.basicConfig(level=getattr(logging, ENV_CONFIG.LOG_LEVEL))

logger = logging.getLogger(__name__)

app = FastAPI(root_path="/api")