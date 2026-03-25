from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of this file's directory)
load_dotenv(Path(__file__).parent.parent / ".env")

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL: str = "claude-sonnet-4-5"
MAX_TOKENS_EXTRACT: int = 512

DATA_DIR: Path = Path(__file__).parent.parent / "data"
STORE_PATH: Path = DATA_DIR / "expenses.json"
