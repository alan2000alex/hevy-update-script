import json
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("data/backups")


def save_backup(workouts: list[dict]) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = BACKUP_DIR / f"backup_{timestamp}.json"
    path.write_text(json.dumps(workouts, indent=2, default=str))
    return path
