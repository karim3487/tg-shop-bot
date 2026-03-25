import logging
import os
from logging.handlers import RotatingFileHandler

from app.config.models import AppConfig


def setup_logging(config: AppConfig) -> None:
    """
    Configures logging with console and rotating file handlers.
    """
    log_dir = "logs"
    log_file = os.path.join(log_dir, "bot.log")

    # Ensure log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define log format
    log_format = "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(config.logs.level_name.upper())

    # Clear existing handlers if any (to avoid duplicates if called multiple times)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 1. Console Handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)

    # 2. Rotating File Handler
    # maxBytes=5MB, backupCount=5 as per requirements
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)

    logging.info(f"Logging initialized. Level: {config.logs.level_name}, File: {log_file}")
