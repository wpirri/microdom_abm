# log.py
import logging
import time
from logging.handlers import TimedRotatingFileHandler

def get_daily_logger():
    logger = logging.getLogger("microdom-abm")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = TimedRotatingFileHandler(
            "/app/logs/microdom_abm.log",
            when="midnight",
            interval=1,
            backupCount=7,
            utc=False,
            encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        formatter.converter = time.localtime
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger