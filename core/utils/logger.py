import logging
import logging.handlers

from rich.logging import RichHandler


RICH_FORMAT = "[%(asctime)s] >> %(message)s"


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO | logging.WARNING | logging.ERROR | logging.CRITICAL | logging.WARN,
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=False)],
    )
    logger = logging.getLogger("rich")
    return logger


logger = get_logger()
