import json
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("history", [])


def save_result(
    members: list[str],
    groups: list[list[str]],
    group_size: int | None,
    num_groups: int | None,
) -> dict:
    _ensure_data_dir()
    history = load_history()
    record = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().isoformat(timespec="seconds"),
        "members": members,
        "groups": groups,
        "group_size": group_size,
        "num_groups": num_groups,
    }
    history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"history": history}, f, ensure_ascii=False, indent=2)
    return record


def clear_history() -> None:
    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"history": []}, f, ensure_ascii=False, indent=2)


def delete_record(record_id: str) -> bool:
    history = load_history()
    new_history = [r for r in history if r["id"] != record_id]
    if len(new_history) == len(history):
        return False
    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"history": new_history}, f, ensure_ascii=False, indent=2)
    return True
