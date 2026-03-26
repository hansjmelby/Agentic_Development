# Direktiv: Norsk nyhetsoppsummering

## Mål
Hent dagens nyheter fra VG, Dagbladet og Aftenposten via RSS, og generer en kort, konsis daglig nyhetsoversikt på norsk.

## Input
- Ingen obligatorisk input. Kjøres uten argumenter for dagens nyheter.

## Verktøy / Scripts
1. `execution/scrape_norsk_nyheter.py` – Henter RSS-feeder og lagrer artiklene til `.tmp/nyheter_raw.json`
2. `execution/oppsummer_nyheter.py` – Leser `.tmp/nyheter_raw.json`, kaller Claude API og printer oppsummeringen

## Output
- Konsis nyhetsoversikt printet til terminalen
- Rådata lagres i `.tmp/nyheter_raw.json` (kan slettes og regenereres)

## RSS-feeder
| Kilde        | URL                                              |
|--------------|--------------------------------------------------|
| VG           | https://www.vg.no/rss/feed/                      |
| NRK          | https://www.nrk.no/toppsaker.rss                 |
| Aftenposten  | https://www.aftenposten.no/rss/                  |

> **Merk:** Dagbladet har fjernet RSS-støtten (returnerer 404). Erstattet med NRK.

## Kjøring
```bash
# Steg 1: Skrape nyheter
.venv/bin/python execution/scrape_norsk_nyheter.py

# Steg 2: Generer oppsummering
.venv/bin/python execution/oppsummer_nyheter.py
```

## Edge cases og læringer
- RSS-feeder kan av og til endre URL – sjekk kildenes nettsider ved feil
- Aftenposten kan kreve `/rss/v2/` – test alternativt `/rss/feed/`
- Maks 10 artikler per kilde hentes (de nyeste)
- Claude-modellen som brukes: claude-haiku-4-5-20251001 (rask og billig for oppsummering)
