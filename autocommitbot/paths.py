import os
from pathlib import Path

# --- User Data Directory ---
# Move all state files to the user's home directory to avoid loss on package updates 
# and permission issues in site-packages.
USER_DATA_DIR = Path.home() / ".autocommitbot"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- State Files ---
CONFIG_FILE = USER_DATA_DIR / "config.json"
HISTORY_FILE = USER_DATA_DIR / "history.json"
LOG_FILE = USER_DATA_DIR / "bot.log"
BACKUP_DIR = USER_DATA_DIR / "backups"

# Create backup directory if it doesn't exist
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# --- Project Base (for bundled assets like banner.txt, etc.) ---
BASE_DIR = Path(__file__).parent.resolve()
CHANGELOG_PATH = BASE_DIR / "CHANGELOG.md"

def get_config_path():
    return str(CONFIG_FILE)

def get_history_path():
    return str(HISTORY_FILE)

def get_log_path():
    return str(LOG_FILE)

def get_backup_dir():
    return str(BACKUP_DIR)
