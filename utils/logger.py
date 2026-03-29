import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(fileName=None):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    if fileName is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(current_dir, "..", "logs", "server.log")
    file_handler = RotatingFileHandler(filename, maxBytes=100000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


app_logger = setup_logger()
