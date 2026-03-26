#!/usr/bin/env python3
"""
Henter nyheter fra VG, Dagbladet og Aftenposten via RSS og lagrer til .tmp/nyheter_raw.json
"""

import json
import os
from datetime import datetime
import feedparser

FEEDS = {
    "VG": "https://www.vg.no/rss/feed/",
    "NRK": "https://www.nrk.no/toppsaker.rss",
    "Aftenposten": "https://www.aftenposten.no/rss/",
}

MAX_ARTICLES_PER_SOURCE = 10


def fetch_feed(source, url):
    print(f"  Henter {source}...", end=" ", flush=True)
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        print(f"FEIL: {feed.bozo_exception}")
        return []

    articles = []
    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        articles.append({
            "kilde": source,
            "tittel": entry.get("title", "").strip(),
            "sammendrag": entry.get("summary", "").strip(),
            "publisert": entry.get("published", ""),
            "url": entry.get("link", ""),
        })

    print(f"{len(articles)} artikler hentet")
    return articles


def main():
    os.makedirs(".tmp", exist_ok=True)
    output_path = ".tmp/nyheter_raw.json"

    alle_artikler = []
    print("Henter nyheter fra norske medier...")

    for source, url in FEEDS.items():
        articles = fetch_feed(source, url)
        alle_artikler.extend(articles)

    result = {
        "hentet_tidspunkt": datetime.now().isoformat(),
        "antall_artikler": len(alle_artikler),
        "artikler": alle_artikler,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nTotalt {len(alle_artikler)} artikler lagret til {output_path}")


if __name__ == "__main__":
    main()
