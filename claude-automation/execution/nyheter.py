#!/usr/bin/env python3
"""Kjører scraping og oppsummering av norske nyheter i ett steg."""

import subprocess
import sys

scripts = [
    "execution/scrape_norsk_nyheter.py",
    "execution/oppsummer_nyheter.py",
]

for script in scripts:
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        sys.exit(result.returncode)
