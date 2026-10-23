"""Oráculos: calculan valores esperados solo a partir del dato de entrada, nunca leyendo el SUT."""

from farmatodo_qa.oracles.text_rules import CODEPOINT_CHARACTERS, WORDCOUNTER_PROFILE, RuleProfile
from farmatodo_qa.oracles.wordcounter_oracle import Keyword, TextOracle

__all__ = ["CODEPOINT_CHARACTERS", "WORDCOUNTER_PROFILE", "Keyword", "RuleProfile", "TextOracle"]
