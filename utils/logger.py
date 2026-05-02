import logging
from pathlib import Path

LOG_DIR = Path("data/logs")


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "hevy_update.log"

    fmt = "%(asctime)s %(levelname)-8s %(name)s – %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
