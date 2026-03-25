from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from expense.models import Expense
from expense.storage import find_duplicate, load_all, save_expense


def _make_expense(**kwargs) -> Expense:
    defaults = dict(
        id="abc123",
        date="2026-03-24",
        amount=24.50,
        currency="USD",
        category="Food",
        description="Lunch at Joe's",
        raw_input="Lunch at Joe's $24.50 yesterday",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    defaults.update(kwargs)
    return Expense(**defaults)


def test_store_created_on_first_save(tmp_path):
    store = tmp_path / "expenses.json"
    save_expense(_make_expense(), path=store)

    assert store.exists()
    data = json.loads(store.read_text())
    assert data["version"] == 1
    assert len(data["expenses"]) == 1


def test_save_and_load_round_trip(tmp_path):
    store = tmp_path / "expenses.json"
    e = _make_expense(id="deadbeef" * 4, amount=42.0, description="Coffee")
    save_expense(e, path=store)

    loaded = load_all(path=store)
    assert len(loaded) == 1
    assert loaded[0]["amount"] == 42.0
    assert loaded[0]["description"] == "Coffee"


def test_multiple_saves_append(tmp_path):
    store = tmp_path / "expenses.json"
    save_expense(_make_expense(id="aaa", description="A"), path=store)
    save_expense(_make_expense(id="bbb", description="B"), path=store)

    loaded = load_all(path=store)
    assert len(loaded) == 2
    assert {e["description"] for e in loaded} == {"A", "B"}


def test_load_all_returns_empty_list_when_no_file(tmp_path):
    result = load_all(path=tmp_path / "nonexistent.json")
    assert result == []


def test_atomic_write_uses_tmp_file(tmp_path, mocker):
    store = tmp_path / "expenses.json"
    original_replace = __import__("os").replace

    replaced = []

    def track_replace(src, dst):
        replaced.append((str(src), str(dst)))
        return original_replace(src, dst)

    mocker.patch("expense.storage.os.replace", side_effect=track_replace)
    save_expense(_make_expense(), path=store)

    # save_expense calls _atomic_write twice: once for _init_store, once to append
    assert len(replaced) >= 1
    assert all(src.endswith(".tmp") for src, dst in replaced)
    assert all(dst == str(store) for src, dst in replaced)


def test_find_duplicate_returns_match(tmp_path):
    store = tmp_path / "expenses.json"
    save_expense(_make_expense(date="2026-03-24", amount=24.50, description="Lunch at Joe's"), path=store)

    result = find_duplicate("2026-03-24", 24.50, "Lunch at Joe's", path=store)
    assert result is not None
    assert result["amount"] == 24.50


def test_find_duplicate_different_amount_returns_none(tmp_path):
    store = tmp_path / "expenses.json"
    save_expense(_make_expense(amount=24.50, description="Lunch"), path=store)

    result = find_duplicate("2026-03-24", 99.99, "Lunch", path=store)
    assert result is None


def test_find_duplicate_outside_window_returns_none(tmp_path):
    store = tmp_path / "expenses.json"
    save_expense(_make_expense(date="2026-01-01", amount=24.50, description="Lunch"), path=store)

    result = find_duplicate("2026-03-24", 24.50, "Lunch", window_days=30, path=store)
    assert result is None
