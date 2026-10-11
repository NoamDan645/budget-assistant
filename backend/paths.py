from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
DB_PATH = PROJECT_ROOT / "data" / "expenses.db"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
