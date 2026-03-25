# Expense CLI

A command-line tool for tracking expenses. Enter receipts in plain language — Claude extracts the date, amount, and category automatically.

---

## Prerequisites

- Python 3.11 or later
- An [Anthropic API key](https://console.anthropic.com/)

---

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd reiseregning-demo

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install the package and dev dependencies
pip install -e ".[dev]"

# 4. Configure your API key
cp .env.example .env
# Edit .env and replace "your-api-key-here" with your actual key:
#   ANTHROPIC_API_KEY=sk-ant-...
```

---

## Commands

### `expense add` — Add a new expense

```bash
# Basic usage (no quoting required)
expense add Lunch at Joe's $24.50 yesterday

# With quotes
expense add "Team dinner, €89, last Friday"

# Preview without saving
expense add "Taxi to airport $45" --dry-run

# Override the extracted date
expense add "Coffee $4.50" --date 2026-03-20

# Fail instead of prompting for missing fields (for scripts)
expense add "Some expense" --no-interactive
```

Output on success:
```
Saved: Food / $24.50 USD / Lunch at Joe's / 2026-03-23 [a1b2c3d4]
```

### `expense list` — View stored expenses

```bash
# Show last 20 expenses (default)
expense list

# Filter by category
expense list --category Food

# Show since a specific date
expense list --since 2026-03-01

# Limit results
expense list --limit 5

# JSON output
expense list --format json
```

### `expense report` — Summary by category

```bash
# All-time report
expense report

# Filter to a specific month
expense report --month 2026-03

# JSON output
expense report --month 2026-03 --format json
```

Example output:
```
Expense Report — 2026-03
------------------------
  Food               $   124.50  (5 items)
  Travel             $    89.00  (2 items)
  Entertainment      $    35.00  (1 item)
------------------------
  Total              $   248.50  (8 items)
```

### `expense export` — Export raw JSON

```bash
# Print to stdout
expense export

# Save to a file
expense export -o report.json

# Export from a specific date
expense export --since 2026-01-01 -o q1.json
```

---

## Flags Reference

| Flag | Command | Description |
|------|---------|-------------|
| `--dry-run` | `add` | Print extracted expense as JSON without saving |
| `--no-interactive` | `add` | Fail instead of prompting for missing fields |
| `--date YYYY-MM-DD` | `add` | Override the extracted date |
| `--category` | `list` | Filter by category |
| `--since YYYY-MM-DD` | `list`, `export` | Show records from this date onward |
| `--limit N` | `list` | Maximum number of records to show (default: 20) |
| `--month YYYY-MM` | `report` | Filter report to a specific month |
| `--format` | `list`, `report` | Output format: `table`/`json` (list) or `text`/`json` (report) |
| `-o / --output` | `export` | Write output to a file instead of stdout |

---

## Categories

Fixed set: `Food`, `Travel`, `Lodging`, `Office`, `Entertainment`, `Other`

If Claude cannot determine the category, you will be prompted to choose one interactively.

---

## Data Storage

Expenses are stored in `data/expenses.json` in the project directory. This file is excluded from git (`.gitignore`). Back it up manually if needed.

---

## Troubleshooting

**`Error: ANTHROPIC_API_KEY is not set`**
Copy `.env.example` to `.env` and add your key from [console.anthropic.com](https://console.anthropic.com/).

**`Error: Invalid ANTHROPIC_API_KEY`**
Your key may be incorrect or revoked. Check the Anthropic console for a valid key.

**`Error: Rate limit reached`**
You have hit the Anthropic API rate limit. Wait a moment and try again.

**`Warning: API unavailable`**
Network error contacting the API. The tool will prompt you to enter all fields manually.

**Running tests**

```bash
pytest
```

All tests mock the Anthropic API — no real API calls are made during testing.
