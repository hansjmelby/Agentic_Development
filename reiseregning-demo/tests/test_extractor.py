from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from expense.extractor import ExtractionError, extract_expense, _parse_tool_result
from expense.models import ExtractionResult


def _make_tool_use_response(input_data: dict) -> MagicMock:
    tool_block = SimpleNamespace(type="tool_use", input=input_data)
    response = MagicMock()
    response.content = [tool_block]
    return response


def test_extract_happy_path(mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_tool_use_response({
        "date": "2026-03-23",
        "amount": 24.50,
        "currency": "USD",
        "category": "Food",
        "description": "Lunch at Joe's",
        "confidence_notes": "",
    })
    mocker.patch("expense.extractor._build_client", return_value=mock_client)

    result = extract_expense("Lunch at Joe's $24.50 yesterday", today=date(2026, 3, 24))

    assert result.date == "2026-03-23"
    assert result.amount == 24.50
    assert result.currency == "USD"
    assert result.category == "Food"
    assert result.description == "Lunch at Joe's"
    assert result.confidence_notes == ""


def test_extract_today_injected_in_system_prompt(mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_tool_use_response({
        "date": "2026-03-24",
        "amount": 10.0,
        "currency": "USD",
        "category": "Food",
        "description": "Coffee",
        "confidence_notes": "",
    })
    mocker.patch("expense.extractor._build_client", return_value=mock_client)

    extract_expense("Coffee today", today=date(2026, 3, 24))

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert "2026-03-24" in call_kwargs["system"]


def test_extract_no_tool_use_block_raises(mocker):
    text_block = SimpleNamespace(type="text", text="Sorry I cannot help.")
    response = MagicMock()
    response.content = [text_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = response
    mocker.patch("expense.extractor._build_client", return_value=mock_client)

    with pytest.raises(ExtractionError):
        extract_expense("Something", today=date(2026, 3, 24))


def test_parse_tool_result_invalid_category_becomes_none():
    result = _parse_tool_result({
        "date": "2026-03-24",
        "amount": 50.0,
        "currency": "USD",
        "category": "Meals",  # not in CATEGORIES
        "description": "Dinner",
        "confidence_notes": "",
    })
    assert result.category is None


def test_parse_tool_result_null_amount():
    result = _parse_tool_result({
        "date": "2026-03-24",
        "amount": None,
        "currency": "USD",
        "category": "Food",
        "description": "Dinner",
        "confidence_notes": "",
    })
    assert result.amount is None


def test_parse_tool_result_european_amount():
    # Claude should have already normalised 1.234,56 → 1234.56 before returning
    result = _parse_tool_result({
        "date": "2026-03-24",
        "amount": 1234.56,
        "currency": "EUR",
        "category": "Travel",
        "description": "Train ticket",
        "confidence_notes": "",
    })
    assert result.amount == 1234.56
    assert result.currency == "EUR"
