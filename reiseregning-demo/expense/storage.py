from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from .config import DATA_DIR, STORE_PATH
from .models import Expense

_EMPTY_STORE = {"version": 1, "expenses": []}


def _init_store(path: Path = STORE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        _atomic_write(path, _EMPTY_STORE)


def _atomic_write(path: Path, data: dict) -> None:
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_all(path: Path = STORE_PATH) -> list[dict]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("expenses", [])


def save_expense(expense: Expense, path: Path = STORE_PATH) -> None:
    _init_store(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw.setdefault("expenses", [])
    raw["expenses"].append(expense.to_dict())
    _atomic_write(path, raw)


def find_duplicate(
    date_str: str,
    amount: float,
    description: str,
    window_days: int = 30,
    path: Path = STORE_PATH,
) -> Optional[dict]:
    expenses = load_all(path)
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        return None

    desc_key = description[:40].lower()
    for record in expenses:
        try:
            rec_date = date.fromisoformat(record.get("date", ""))
        except ValueError:
            continue
        if abs((target - rec_date).days) > window_days:
            continue
        if record.get("amount") != amount:
            continue
        if record.get("description", "")[:40].lower() != desc_key:
            continue
        return record
    return None
