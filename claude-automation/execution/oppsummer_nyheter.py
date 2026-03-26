#!/usr/bin/env python3
"""
Leser .tmp/nyheter_raw.json og bruker Claude til å generere en konsis daglig nyhetsoversikt.
"""

import json
import os
import sys
from dotenv import load_dotenv
import anthropic

load_dotenv()

INPUT_PATH = ".tmp/nyheter_raw.json"


def build_article_text(artikler):
    lines = []
    for i, a in enumerate(artikler):
        lines.append(f"[ID:{i}] [{a['kilde']}] {a['tittel']}")
        if a.get("sammendrag"):
            summary = a["sammendrag"][:300]
            lines.append(f"  {summary}")
        lines.append("")
    return "\n".join(lines)


def inject_links(text, artikler):
    """Erstatter [ID:N] i Claude-output med markdown-lenker til artikkelen."""
    import re
    def replace(m):
        idx = int(m.group(1))
        if idx < len(artikler):
            url = artikler[idx].get("url", "")
            tittel = artikler[idx].get("tittel", f"ID:{idx}")
            if url:
                return f"[{tittel}]({url})"
        return m.group(0)
    return re.sub(r'\[ID:(\d+)\]', replace, text)


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"Finner ikke {INPUT_PATH}. Kjør scrape_norsk_nyheter.py først.")
        sys.exit(1)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    artikler = data["artikler"]
    hentet_tidspunkt = data["hentet_tidspunkt"]
    artikkel_tekst = build_article_text(artikler)

    print(f"Oppsummerer {len(artikler)} artikler hentet {hentet_tidspunkt[:16].replace('T', ' kl.')}...\n")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    melding = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Du er en norsk nyhetsredaktør. Nedenfor er dagens artikler fra VG, Dagbladet og Aftenposten.

Lag en kort og konsis nyhetsoversikt på norsk. Strukturen skal være:

**Dagens viktigste saker – {hentet_tidspunkt[:10]}**

Grupper sakene i kategorier som passer (f.eks. Politikk, Økonomi, Sport, Utenriks, Annet). Ta med de 8–12 viktigste sakene totalt. Skriv 1–2 setninger per sak. Unngå klikk-bait og tabloid-språk – vær saklig og nøktern.

Viktig: Hver sak du omtaler MÅ starte med [ID:N] der N er ID-nummeret til den aktuelle artikkelen. Eksempel: "[ID:3] **Tittelen** – beskrivelse av saken."

---
ARTIKLER:
{artikkel_tekst}
---""",
            }
        ],
    )

    output = inject_links(melding.content[0].text, artikler)
    print(output)


if __name__ == "__main__":
    main()
