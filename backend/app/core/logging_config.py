"""input: 依赖 logging、项目根目录和文件系统。
output: 向外提供命名 logger 和日志文件配置。
pos: 位于基础设施层，负责统一日志出口。
声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# backend/app/core/logging_config.py -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class LogConfig:
    DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    APP_LOG = LOGS_DIR / "app.log"
    API_LOG = LOGS_DIR / "api.log"
    WORKER_LOG = LOGS_DIR / "worker.log"
    AI_LOG = LOGS_DIR / "ai.log"
    ERROR_LOG = LOGS_DIR / "error.log"

    MAX_BYTES = 10 * 1024 * 1024
    BACKUP_COUNT = 5


def setup_logger(
    name: str,
    log_file: Path,
    level: int = logging.INFO,
    format_string: str = LogConfig.DETAILED_FORMAT,
    max_bytes: int = LogConfig.MAX_BYTES,
    backup_count: int = LogConfig.BACKUP_COUNT
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    logger.handlers.clear()

    formatter = logging.Formatter(format_string)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


app_logger = setup_logger("app", LogConfig.APP_LOG)
api_logger = setup_logger("api", LogConfig.API_LOG)
worker_logger = setup_logger("worker", LogConfig.WORKER_LOG)
ai_logger = setup_logger("ai", LogConfig.AI_LOG)
error_logger = setup_logger("error", LogConfig.ERROR_LOG, level=logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    loggers = {
        "app": app_logger,
        "api": api_logger,
        "worker": worker_logger,
        "ai": ai_logger,
        "error": error_logger
    }

    return loggers.get(name, app_logger)
