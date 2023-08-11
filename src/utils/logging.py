import logging
import sys

import structlog

from src.data.config import load_config


def setup_logger() -> structlog.typing.FilteringBoundLogger:
    config = load_config()

    logging.basicConfig(
        level=config.app.logging_level,
        stream=sys.stdout
    )

    log: structlog.typing.FilteringBoundLogger = structlog.get_logger(
        structlog.stdlib.BoundLogger
    )
    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level
    ]
    processors = shared_processors + [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.dev.ConsoleRenderer(),
    ]
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(config.app.logging_level)
    )

    logging.getLogger("aiogram.dispatcher").setLevel(logging.WARN)
    logging.getLogger("aiogram.event").setLevel(logging.WARN)
    logging.getLogger("apscheduler.executors.default").setLevel(logging.WARN)
    logging.getLogger("apscheduler.scheduler").setLevel(logging.WARN)
    logging.getLogger("aiogram.utils.chat_action").setLevel(logging.WARN)
    logging.getLogger("aiogram_dialog.context.intent_middleware").setLevel(logging.WARN)
    # logging.getLogger("aiogram_dialog.manager.message_manager").setLevel(logging.WARN)

    return log
