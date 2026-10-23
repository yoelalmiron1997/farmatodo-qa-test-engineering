"""Localizadores de wordcounter.net — verificados en el DOM real el 2026-10-23.

Fuente: inspección con Chromium 152 (docs/exploration/wordcounter-spike.md). Si el sitio
cambia, se actualiza solo este módulo y la fecha de verificación.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By

VERIFIED_ON = "2026-10-23"

EDITOR = (By.ID, "box")  # <textarea id="box" placeholder="Start typing, or copy and paste...">
HEADLINE = (By.CSS_SELECTOR, "#top_counter .counted")  # "11 words 72 characters"
WORD_COUNT = (By.ID, "word_count")  # badge del panel Details
CHARACTER_COUNT = (By.ID, "character_count")  # badge del panel Details
KEYWORD_PANEL = (By.ID, "kwd-density")
KEYWORD_ROWS = (By.CSS_SELECTOR, "#kwd-accordion-data a.list-group-item")
KEYWORD_WORD = (By.CSS_SELECTOR, "span.word")
KEYWORD_BADGE = (By.CSS_SELECTOR, "span.badge")  # " 5 (45%)"
