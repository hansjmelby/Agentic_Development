from __future__ import annotations

import pytest
import click

from expense.models import ExtractionResult
from expense.validator import validate_and_complete


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


def test_validate_complete_result_no_prompts(mocker):
    mock_prompt = mocker.patch("expense.validator.click.prompt")
    mock_confirm = mocker.patch("expense.validator.click.confirm")

    expense = validate_and_complete(_full_result(), raw_input="test")

    mock_prompt.assert_not_called()
    mock_confirm.assert_not_called()
    assert expense.date == "2026-03-24"
    assert expense.amount == 24.50
    assert expense.category == "Food"
    assert expense.description == "Lunch at Joe's"


def test_validate_missing_date_prompts(mocker):
    mocker.patch("expense.validator.click.prompt", return_value="2026-03-24")
    mocker.patch("expense.validator.click.confirm", return_value=True)

    expense = validate_and_complete(_full_result(date=None), raw_input="test")

    assert expense.date == "2026-03-24"


def test_validate_missing_amount_prompts(mocker):
    mocker.patch("expense.validator.click.prompt", return_value="99.99")

    expense = validate_and_complete(_full_result(amount=None), raw_input="test")

    assert expense.amount == 99.99


def test_validate_invalid_category_prompts(mocker):
    mocker.patch("expense.validator.click.prompt", return_value="Travel")

    expense = validate_and_complete(_full_result(category="Meals"), raw_input="test")

    assert expense.category == "Travel"


def test_validate_confidence_notes_shows_confirm_yes(mocker):
    mocker.patch("expense.validator.click.prompt")
    mocker.patch("expense.validator.click.confirm", return_value=True)

    expense = validate_and_complete(
        _full_result(confidence_notes="Ambiguous date"), raw_input="test"
    )

    click.confirm.assert_called_once()
    assert expense.amount == 24.50


def test_validate_confidence_notes_confirm_no_reprompts_all(mocker):
    prompts = ["2026-03-25", "50.00", "Travel", "New description"]
    prompt_iter = iter(prompts)
    mocker.patch("expense.validator.click.prompt", side_effect=lambda *a, **kw: next(prompt_iter))
    mocker.patch("expense.validator.click.confirm", return_value=False)

    expense = validate_and_complete(
        _full_result(confidence_notes="Maybe wrong date"), raw_input="test"
    )

    assert expense.date == "2026-03-25"
    assert expense.description == "New description"


def test_validate_no_interactive_missing_fields_raises():
    with pytest.raises(click.UsageError, match="Missing field"):
        validate_and_complete(
            _full_result(date=None, amount=None), raw_input="test", skip_confirm=True
        )


def test_validate_preserves_raw_input():
    expense = validate_and_complete(_full_result(), raw_input="original text here")
    assert expense.raw_input == "original text here"


def test_validate_id_is_hex_string():
    expense = validate_and_complete(_full_result(), raw_input="test")
    assert len(expense.id) == 32
    int(expense.id, 16)  # raises if not valid hex
