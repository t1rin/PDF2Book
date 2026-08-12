import pyfiglet

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "pdf2book.log"

FORMAT = "%(levelname)+8s - %(asctime)s - <%(name)s> %(message)s"
#FORMAT = "[%(levelname)s] - %(asctime)s - <%(name)s> %(message)s"
DATE_FORMAT = "%H:%M:%S"

MODULE_LEVELS: dict[str, int] = {
    "core":              logging.DEBUG,
    "ui":                logging.INFO,
    "utils":             logging.DEBUG,
    "__main__":          logging.DEBUG,
}


def write_start_label(label: str = "PDF2Book") -> None:
    print(pyfiglet.figlet_format(label))


def setup_log(console_level: int | None = None,
              file_level: int | None = None,
              max_bytes: int = 5 * 1024 * 1024,
              backup_count: int = 3) -> None:
    LOG_DIR.mkdir(exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(FORMAT, datefmt=DATE_FORMAT)

    if console_level is not None:
        write_start_label()
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    if file_level is not None:
        file_handler = RotatingFileHandler(LOG_FILE,
            maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    for module, level in MODULE_LEVELS.items():
        logging.getLogger(module).setLevel(level)

    logging.getLogger(__name__).debug("Логирование инициализировано → %s", LOG_FILE)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
