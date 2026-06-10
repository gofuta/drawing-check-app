import json
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path(__file__).parent.parent / "output" / "history"


def save_history(project_name: str, result: dict):
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{project_name}.json"
        data = {
            "timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "result": result,
        }
        (HISTORY_DIR / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_history() -> list[dict]:
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)
        records = []
        for f in files:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["_filename"] = f.name
                records.append(data)
            except Exception:
                pass
        return records
    except Exception:
        return []
