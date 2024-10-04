import logging
from logging.handlers import RotatingFileHandler
import os
from rag_app.config import settings

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "rag_app.log")

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5),
            logging.StreamHandler()
        ]
    )

    logging.getLogger("uvicorn.access").disabled = True

    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed.")
