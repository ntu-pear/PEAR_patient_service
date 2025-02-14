from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json

# This is for localtesting logs
# LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "logs"))

# Note that this is production Kubernetes logs
LOG_DIR = "/app/logs"

os.makedirs(LOG_DIR, exist_ok=True) 

today = datetime.now().strftime("%Y-%m-%d")
log_file = f"{LOG_DIR}/app_{today}.log"

log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "user": "%(user)s", "table": "%(table)s", "action": "%(action)s", "message": %(message)s}'
date_format = "%Y-%m-%dT%H:%M:%S"  

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format)) 

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler]
)

logger = logging.getLogger(__name__)
