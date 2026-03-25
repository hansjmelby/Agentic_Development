from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from expense.cli import cli
from expense.models import Expense, ExtractionResult


def _full_result(**kwargs) -> ExtractionResult:
    defaults = dict(
        date="2026-03-24",
        amount=24.50,
        currency="USD",
        category="Food",
        description="Lunch at Joe's",
        confidence_notes="",
    )
    defaults.update(kwargs)
    return ExtractionResult(**defaults)


def _sample_expense(**kwargs) -> Expense:
    defaults = dict(
        id="abc123def456",
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


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

def test_add_dry_run_prints_json_no_save(mocker, runner, tmp_path):
    mocker.patch("expense.cli.extract_expense", return_value=_full_result())
    mocker.patch("expense.cli.find_duplicate", return_value=None)
    mocker.patch("expense.cli.validate_and_complete", return_value=_sample_expense())
    mock_save = mocker.patch("expense.cli.save_expense")

    result = runner.invoke(cli, ["add", "--dry-run", "Lunch at Joe's $24.50 yesterday"])

    assert result.exit_code == 0
    mock_save.assert_not_called()
    data = json.loads(result.output)
    assert data["amount"] == 24.50


def test_add_saves_expense(mocker, runner, tmp_path):
    mocker.patch("expense.cli.extract_expense", return_value=_full_result())
    mocker.patch("expense.cli.find_duplicate", return_value=None)
    mocker.patch("expense.cli.validate_and_complete", return_value=_sample_expense())
    mock_save = mocker.patch("expense.cli.save_expense")

    result = runner.invoke(cli, ["add", "Lunch at Joe's $24.50 yesterday"])

    assert result.exit_code == 0
    mock_save.assert_called_once()
    assert "Saved" in result.output


def test_add_api_failure_falls_back_to_manual(mocker, runner):
    import anthropic as _anthropic
    import httpx
    mocker.patch("expense.cli.extract_expense", side_effect=_anthropic.APIConnectionError(request=httpx.Request("GET", "https://api.anthropic.com")))
    mocker.patch("expense.cli.find_duplicate", return_value=None)
    mocker.patch("expense.cli.validate_and_complete", return_value=_sample_expense())
    mocker.patch("expense.cli.save_expense")

    result = runner.invoke(cli, ["add", "Lunch $24.50"])

    assert result.exit_code == 0
    assert "Warning" in result.stderr or "Warning" in result.output


def test_add_no_interactive_missing_fields_exits(mocker, runner):
    mocker.patch("expense.cli.extract_expense", return_value=_full_result(date=None))
    mocker.patch("expense.cli.find_duplicate", return_value=None)

    result = runner.invoke(cli, ["add", "--no-interactive", "some expense"])

    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def test_list_empty_store(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[])

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "No expenses found" in result.output


def test_list_table_output(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[
        _sample_expense(category="Food", amount=10.0, description="Coffee").to_dict(),
        _sample_expense(category="Travel", amount=50.0, description="Taxi").to_dict(),
    ])

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "Coffee" in result.output
    assert "Taxi" in result.output


def test_list_category_filter(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[
        _sample_expense(category="Food", description="Coffee").to_dict(),
        _sample_expense(category="Travel", description="Taxi").to_dict(),
    ])

    result = runner.invoke(cli, ["list", "--category", "Food"])

    assert result.exit_code == 0
    assert "Coffee" in result.output
    assert "Taxi" not in result.output


def test_list_json_format(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[
        _sample_expense().to_dict(),
    ])

    result = runner.invoke(cli, ["list", "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["description"] == "Lunch at Joe's"


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def test_report_month_filter(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[
        _sample_expense(date="2026-03-10", category="Food", amount=20.0).to_dict(),
        _sample_expense(date="2026-03-15", category="Travel", amount=80.0).to_dict(),
        _sample_expense(date="2026-02-01", category="Food", amount=999.99).to_dict(),  # excluded
    ])

    result = runner.invoke(cli, ["report", "--month", "2026-03"])

    assert result.exit_code == 0
    assert "20.00" in result.output or "80.00" in result.output
    # Feb expense should not appear
    assert "999.99" not in result.output


def test_report_json_format(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[
        _sample_expense(category="Food", amount=24.50).to_dict(),
    ])

    result = runner.invoke(cli, ["report", "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["grand_total"] == 24.50


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

def test_export_stdout(mocker, runner):
    mocker.patch("expense.cli.load_all", return_value=[_sample_expense().to_dict()])

    result = runner.invoke(cli, ["export"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data["expenses"]) == 1


def test_export_to_file(mocker, runner, tmp_path):
    mocker.patch("expense.cli.load_all", return_value=[_sample_expense().to_dict()])
    out_file = tmp_path / "out.json"

    result = runner.invoke(cli, ["export", "-o", str(out_file)])

    assert result.exit_code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert len(data["expenses"]) == 1
