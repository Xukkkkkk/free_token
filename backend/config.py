import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "free_ai_pool.db"

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "28899"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Master API token for administering or default client usage
DEFAULT_MASTER_KEY = os.getenv("MASTER_KEY", "sk-free-ai-pool-master")

# Default request timeout in seconds
REQUEST_TIMEOUT = 60.0
