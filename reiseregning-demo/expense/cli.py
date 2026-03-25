from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import anthropic
import click

from .extractor import ConfigError, ExtractionError, extract_expense
from .models import CATEGORIES, ExtractionResult
from .storage import find_duplicate, load_all, save_expense
from .validator import validate_and_complete


@click.group()
@click.version_option(version="0.1.0", prog_name="expense")
def cli() -> None:
    """Expense tracking CLI powered by Claude."""


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("text", nargs=-1, required=True)
@click.option("--no-interactive", "no_interactive", is_flag=True, default=False,
              help="Fail instead of prompting for missing fields.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Print the extracted expense as JSON without saving.")
@click.option("--date", "override_date", default=None, metavar="YYYY-MM-DD",
              help="Override the extracted date.")
def add(
    text: tuple[str, ...],
    no_interactive: bool,
    dry_run: bool,
    override_date: Optional[str],
) -> None:
    """Add a new expense from natural language TEXT."""
    raw_text = " ".join(text)

    # Extract via Claude
    result: ExtractionResult
    try:
        result = extract_expense(raw_text)
    except ConfigError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except anthropic.AuthenticationError:
        click.secho("Error: Invalid ANTHROPIC_API_KEY. Check your .env file.", fg="red", err=True)
        sys.exit(1)
    except anthropic.RateLimitError:
        click.secho("Error: Rate limit reached. Try again in a moment.", fg="yellow", err=True)
        sys.exit(1)
    except (anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
        click.secho(f"Warning: API unavailable ({e}). Manual entry required.", fg="yellow", err=True)
        result = ExtractionResult(date=None, amount=None, category=None, description=None)
    except ExtractionError as e:
        click.secho(f"Warning: Extraction failed ({e}). Manual entry required.", fg="yellow", err=True)
        result = ExtractionResult(date=None, amount=None, category=None, description=None)

    # Apply date override
    if override_date:
        result.date = override_date

    # Duplicate check (skip in dry-run)
    if not dry_run and result.date and result.amount is not None and result.description:
        dup = find_duplicate(result.date, result.amount, result.description or "")
        if dup:
            click.secho(
                f"  Similar expense found: {dup['category']} / ${dup['amount']} / "
                f"{dup['description']} / {dup['date']}",
                fg="yellow",
            )
            if not click.confirm("Save anyway?", default=True):
                click.echo("Aborted.")
                return

    # Validate and complete
    try:
        expense = validate_and_complete(result, raw_text, skip_confirm=no_interactive)
    except click.UsageError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)

    if dry_run:
        click.echo(json.dumps(expense.to_dict(), indent=2))
        return

    save_expense(expense)
    click.secho(
        f"Saved: {expense.category} / ${expense.amount:.2f} {expense.currency} / "
        f"{expense.description} / {expense.date} [{expense.id[:8]}]",
        fg="green",
    )


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@cli.command("list")
@click.option("--limit", default=20, show_default=True, help="Number of recent records.")
@click.option("--category", type=click.Choice(CATEGORIES, case_sensitive=False), default=None)
@click.option("--since", default=None, metavar="YYYY-MM-DD", help="Show records from this date.")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table",
              show_default=True)
def list_expenses(limit: int, category: Optional[str], since: Optional[str], fmt: str) -> None:
    """List stored expenses."""
    expenses = load_all()

    if since:
        expenses = [e for e in expenses if e.get("date", "") >= since]
    if category:
        expenses = [e for e in expenses if e.get("category", "").lower() == category.lower()]

    expenses = expenses[-limit:]

    if not expenses:
        click.echo("No expenses found.")
        return

    if fmt == "json":
        click.echo(json.dumps(expenses, indent=2))
        return

    # Table output
    header = f"{'DATE':<12} {'CATEGORY':<15} {'AMOUNT':>10}  {'DESCRIPTION'}"
    click.echo(header)
    click.echo("-" * len(header))
    for e in expenses:
        click.echo(
            f"{e.get('date', ''):<12} {e.get('category', ''):<15} "
            f"${e.get('amount', 0):>9.2f}  {e.get('description', '')}"
        )


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--month", default=None, metavar="YYYY-MM", help="Filter to month (e.g. 2026-03).")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text",
              show_default=True)
def report(month: Optional[str], fmt: str) -> None:
    """Show expense totals grouped by category."""
    expenses = load_all()

    if month:
        expenses = [e for e in expenses if e.get("date", "").startswith(month)]

    totals: dict[str, tuple[float, int]] = {}
    for e in expenses:
        cat = e.get("category", "Other")
        amt = float(e.get("amount", 0))
        prev_amt, prev_count = totals.get(cat, (0.0, 0))
        totals[cat] = (prev_amt + amt, prev_count + 1)

    grand_total = sum(v[0] for v in totals.values())
    grand_count = sum(v[1] for v in totals.values())

    if fmt == "json":
        output = {
            "month": month or "all",
            "categories": [
                {"category": cat, "total": amt, "count": cnt}
                for cat, (amt, cnt) in sorted(totals.items())
            ],
            "grand_total": grand_total,
            "grand_count": grand_count,
        }
        click.echo(json.dumps(output, indent=2))
        return

    title = f"Expense Report — {month or 'All time'}"
    click.echo(title)
    click.echo("-" * len(title))
    for cat, (amt, cnt) in sorted(totals.items()):
        click.echo(f"  {cat:<18} ${amt:>9.2f}  ({cnt} item{'s' if cnt != 1 else ''})")
    click.echo("-" * len(title))
    click.echo(f"  {'Total':<18} ${grand_total:>9.2f}  ({grand_count} item{'s' if grand_count != 1 else ''})")


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--output", "-o", type=click.Path(), default=None,
              help="File path to write. Defaults to stdout.")
@click.option("--since", default=None, metavar="YYYY-MM-DD", help="Export from this date.")
def export(output: Optional[str], since: Optional[str]) -> None:
    """Export all expenses as JSON."""
    expenses = load_all()

    if since:
        expenses = [e for e in expenses if e.get("date", "") >= since]

    payload = json.dumps({"version": 1, "expenses": expenses}, indent=2)

    if output:
        Path(output).write_text(payload, encoding="utf-8")
        click.echo(f"Exported {len(expenses)} expense(s) to {output}")
    else:
        click.echo(payload)
