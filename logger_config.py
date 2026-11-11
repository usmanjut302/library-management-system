
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Get the project directory
BASE_DIR = Path(__file__).resolve().parent

# Create logs directory
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file location
LOG_FILE = LOG_DIR / "library.log"


# Create logger
logger = logging.getLogger("library")
logger.setLevel(logging.INFO)

# Prevent duplicate log messages
logger.propagate = False


# Configure log format
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


# Configure rotating file handler
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,
    backupCount=5,
    encoding="utf-8"
)

file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)


# Add handler only once
if not logger.handlers:
    logger.addHandler(file_handler)
