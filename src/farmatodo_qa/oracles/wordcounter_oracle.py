"""Oráculo independiente para WordCounter: función pura de (texto, perfil)."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from farmatodo_qa.oracles.text_rules import CharacterUnit, RuleProfile, TieBreak

_NUMERIC_RE = re.compile(r"^[\d.,]+$")


@dataclass(frozen=True, slots=True)
class Keyword:
    word: str
    count: int

    def __str__(self) -> str:
        return f"{self.word}={self.count}"


def _utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def _is_punctuation(char: str) -> bool:
    return unicodedata.category(char).startswith("P")


def _has_content(token: str) -> bool:
    """Un token cuenta si tiene al menos un carácter que no sea puntuación."""
    return any(not _is_punctuation(char) for char in token)


def _strip_punctuation(token: str) -> str:
    start, end = 0, len(token)
    while start < end and _is_punctuation(token[start]):
        start += 1
    while end > start and _is_punctuation(token[end - 1]):
        end -= 1
    return token[start:end]


@dataclass(frozen=True, slots=True)
class TextOracle:
    """Calcula los valores esperados para un texto según un :class:`RuleProfile`."""

    profile: RuleProfile

    def word_count(self, text: str) -> int:
        tokens = self.profile.word_separator.split(text)
        return sum(1 for token in tokens if token and _has_content(token))

    def character_count(self, text: str) -> int:
        kept = "".join(char for char in text if char not in self.profile.excluded_characters)
        if self.profile.character_unit is CharacterUnit.UTF16:
            return _utf16_length(kept)
        return len(kept)

    def _keyword_candidates(self, text: str) -> list[str]:
        candidates: list[str] = []
        for raw in self.profile.keyword_separator.split(text.lower()):
            token = _strip_punctuation(raw)
            if not token or not _has_content(token):
                continue
            if token in self.profile.keyword_stop_words:
                continue
            if self.profile.keyword_exclude_numeric and _NUMERIC_RE.match(token):
                continue
            if _utf16_length(token) < self.profile.keyword_min_utf16_length:
                continue
            candidates.append(token)
        return candidates

    def keywords(self, text: str) -> list[Keyword]:
        """Todas las palabras clave, ordenadas como las muestra Keyword Density."""
        candidates = self._keyword_candidates(text)
        counts = Counter(candidates)
        first_seen = {word: index for index, word in reversed(list(enumerate(candidates)))}
        if self.profile.keyword_tie_break is TieBreak.FIRST_APPEARANCE:
            ordered = sorted(counts, key=lambda word: (-counts[word], first_seen[word]))
        else:
            ordered = sorted(counts, key=lambda word: (-counts[word], word))
        return [Keyword(word, counts[word]) for word in ordered]

    def top_keywords(self, text: str, n: int = 3) -> list[Keyword]:
        return self.keywords(text)[:n]
