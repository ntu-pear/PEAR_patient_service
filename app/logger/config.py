from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure logs directory exists

# Add suffix to log file name 
today = datetime.now().strftime("%Y-%m-%d")
log_file = f"{LOG_DIR}/app_{today}.log"

# TimedRotatingFileHandler rotates logs daily and appends the date to the filename
# Stores max 30 days worth of logs before deleting.
file_handler = TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30
)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        file_handler,  # File handler for daily rotation
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)