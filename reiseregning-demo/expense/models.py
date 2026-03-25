from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

CATEGORIES: tuple[str, ...] = (
    "Food",
    "Travel",
    "Lodging",
    "Office",
    "Entertainment",
    "Other",
)

Category = Literal["Food", "Travel", "Lodging", "Office", "Entertainment", "Other"]


@dataclass
class ExtractionResult:
    """Raw output from Claude — all fields optional because extraction may be partial."""

    date: Optional[str]         # ISO 8601 "YYYY-MM-DD" or None
    amount: Optional[float]     # Normalised positive float or None
    category: Optional[str]     # One of CATEGORIES or None
    description: Optional[str]  # Merchant name / purpose or None
    currency: str = "USD"       # ISO 4217 code
    confidence_notes: str = ""  # Claude's uncertainty notes


@dataclass
class Expense:
    """A validated, complete expense record ready for storage."""

    id: str           # uuid4().hex
    date: str         # "YYYY-MM-DD"
    amount: float     # Always positive
    currency: str     # ISO 4217 code
    category: str     # Always in CATEGORIES
    description: str
    raw_input: str    # Original user text, verbatim
    created_at: str   # UTC ISO 8601 timestamp

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "description": self.description,
            "raw_input": self.raw_input,
            "created_at": self.created_at,
        }
