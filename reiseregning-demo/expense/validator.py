from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import click

from .models import CATEGORIES, Expense, ExtractionResult


def _prompt_date(default: Optional[str]) -> str:
    while True:
        value = click.prompt("Date of expense", default=default or "", show_default=bool(default))
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            click.secho("  Invalid date. Use YYYY-MM-DD format.", fg="red")


def _prompt_amount(default: Optional[float]) -> float:
    while True:
        raw = click.prompt(
            "Amount",
            default=str(default) if default is not None else "",
            show_default=default is not None,
        )
        try:
            val = float(str(raw).replace(",", "."))
            if val <= 0:
                raise ValueError
            return val
        except ValueError:
            click.secho("  Invalid amount. Enter a positive number.", fg="red")


def _prompt_category(default: Optional[str]) -> str:
    valid_default = default if default in CATEGORIES else None
    return click.prompt(
        "Category",
        type=click.Choice(CATEGORIES, case_sensitive=False),
        default=valid_default,
        show_default=bool(valid_default),
    )


def _prompt_description(default: Optional[str]) -> str:
    while True:
        value = click.prompt(
            "Description",
            default=default or "",
            show_default=bool(default),
        )
        if value.strip():
            return value.strip()
        click.secho("  Description cannot be empty.", fg="red")


def _prompt_all(result: ExtractionResult) -> tuple[str, float, str, str]:
    date_val = _prompt_date(result.date)
    amount_val = _prompt_amount(result.amount)
    category_val = _prompt_category(result.category)
    desc_val = _prompt_description(result.description)
    return date_val, amount_val, category_val, desc_val


def validate_and_complete(
    result: ExtractionResult,
    raw_input: str,
    skip_confirm: bool = False,
) -> Expense:
    """Interactively fill missing/ambiguous fields and return a complete Expense.

    Args:
        result: Partial extraction from Claude.
        raw_input: Original user string, stored verbatim.
        skip_confirm: If True, suppresses the ambiguity confirmation prompt.

    Returns:
        A fully-populated Expense ready for storage.

    Raises:
        click.UsageError: If skip_confirm is True and a required field is missing.
        click.Abort: If the user presses Ctrl-C.
    """
    if skip_confirm:
        missing = []
        if not result.date:
            missing.append("date")
        if result.amount is None:
            missing.append("amount")
        if not result.category:
            missing.append("category")
        if not result.description:
            missing.append("description")
        if missing:
            raise click.UsageError(
                f"Missing field(s): {', '.join(missing)}. "
                "Remove --no-interactive to be prompted."
            )

    date_val = result.date
    amount_val = result.amount
    category_val = result.category
    desc_val = result.description

    # Prompt for each missing field individually
    if not date_val:
        date_val = _prompt_date(None)

    if amount_val is None:
        amount_val = _prompt_amount(None)

    if not category_val or category_val not in CATEGORIES:
        category_val = _prompt_category(category_val)

    if not desc_val:
        desc_val = _prompt_description(None)

    # If Claude flagged ambiguity, surface it and offer a full re-prompt
    if result.confidence_notes and not skip_confirm:
        click.secho(f"  Note: {result.confidence_notes}", fg="yellow")
        if not click.confirm("Does this look correct?", default=True):
            date_val, amount_val, category_val, desc_val = _prompt_all(result)

    return Expense(
        id=uuid.uuid4().hex,
        date=date_val,
        amount=float(amount_val),
        currency=result.currency,
        category=category_val,
        description=desc_val,
        raw_input=raw_input,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
