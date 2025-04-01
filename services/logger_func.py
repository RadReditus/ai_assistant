import logging
import os
from colorama import init, Fore, Style
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
load_dotenv(dotenv_path)
DEBUG = os.getenv("DEBUG")
LOG_FILE_NAME: str = 'general.log'

if DEBUG == 'True':
    LOG_FILE_NAME = 'test_general.log'

logger = logging.getLogger("MyBot")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_formatter)

log_dir = os.path.join(os.path.dirname(__file__), "../data/logs")
os.makedirs(log_dir, exist_ok=True)
    
log_file = os.path.join(log_dir, LOG_FILE_NAME)
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

