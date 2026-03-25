from __future__ import annotations

from datetime import date
from typing import Any, Optional

import anthropic

from .config import ANTHROPIC_API_KEY, MAX_TOKENS_EXTRACT, MODEL
from .models import CATEGORIES, ExtractionResult

_SYSTEM_TEMPLATE = (
    "You are an expense extraction assistant. Today's date is {today}. "
    "Always call the record_expense tool — never respond with plain text."
)

_EXTRACT_TOOL: dict[str, Any] = {
    "name": "record_expense",
    "description": (
        "Extract a structured expense record from the user's natural language input. "
        "Always resolve relative dates (today, yesterday, last Friday) to absolute "
        "ISO 8601 dates based on the provided current date. "
        "For amounts, use the numeric value only, stripping currency symbols. "
        "Normalise European decimal formats (1.234,56 → 1234.56). "
        "If a field cannot be determined with reasonable confidence, set it to null. "
        "Do NOT guess an amount if multiple unrelated numbers appear."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "date": {
                "type": ["string", "null"],
                "description": "Absolute date as YYYY-MM-DD. Resolve relative dates using today's date.",
            },
            "amount": {
                "type": ["number", "null"],
                "description": "Expense amount as a positive float in the original currency.",
            },
            "currency": {
                "type": "string",
                "description": "ISO 4217 currency code inferred from symbols or context. Default USD.",
            },
            "category": {
                "type": ["string", "null"],
                "enum": [*CATEGORIES, None],
                "description": "Best-fit category from the fixed list, or null if unclear.",
            },
            "description": {
                "type": ["string", "null"],
                "description": "Short merchant name or purpose (e.g. 'Lunch at Joe\\'s').",
            },
            "confidence_notes": {
                "type": "string",
                "description": "Brief note on any ambiguity or assumption made during extraction.",
            },
        },
        "required": ["date", "amount", "currency", "category", "description", "confidence_notes"],
    },
}


class ExtractionError(Exception):
    """Raised when Claude does not return the expected tool_use block."""


class ConfigError(Exception):
    """Raised when ANTHROPIC_API_KEY is not configured."""


def _build_client() -> anthropic.Anthropic:
    if not ANTHROPIC_API_KEY:
        raise ConfigError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _parse_tool_result(tool_input: dict[str, Any]) -> ExtractionResult:
    raw_category = tool_input.get("category")
    category: Optional[str] = raw_category if raw_category in CATEGORIES else None

    raw_amount = tool_input.get("amount")
    amount: Optional[float]
    try:
        amount = float(raw_amount) if raw_amount is not None else None
    except (TypeError, ValueError):
        amount = None

    return ExtractionResult(
        date=tool_input.get("date") or None,
        amount=amount,
        currency=tool_input.get("currency") or "USD",
        category=category,
        description=tool_input.get("description") or None,
        confidence_notes=tool_input.get("confidence_notes") or "",
    )


def extract_expense(raw_text: str, today: Optional[date] = None) -> ExtractionResult:
    """Call Claude to extract expense fields from raw_text.

    Args:
        raw_text: The user's free-form input.
        today: Override for current date (used in tests). Defaults to date.today().

    Returns:
        ExtractionResult with fields set to None where Claude was uncertain.

    Raises:
        ConfigError: If ANTHROPIC_API_KEY is not set.
        ExtractionError: If Claude's response is malformed.
        anthropic.APIError: On API-level failures.
    """
    _today = today or date.today()
    client = _build_client()

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_EXTRACT,
        system=_SYSTEM_TEMPLATE.format(today=_today.isoformat()),
        tools=[_EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "record_expense"},
        messages=[{"role": "user", "content": raw_text}],
    )

    tool_block = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_block is None:
        raise ExtractionError("Claude did not return a tool_use block.")

    return _parse_tool_result(tool_block.input)
