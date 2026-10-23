"""El oráculo reproduce, sin navegador, lo observado en wordcounter.net (TC-FW-009)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from farmatodo_qa.oracles import CODEPOINT_CHARACTERS, WORDCOUNTER_PROFILE, TextOracle

OBSERVATIONS = json.loads(
    (Path(__file__).resolve().parents[3] / "data/observations/wordcounter-spike.json").read_text(
        encoding="utf-8"
    )
)["observations"]
ORACLE = TextOracle(WORDCOUNTER_PROFILE)


def _skip_fields(obs: dict[str, Any]) -> set[str]:
    defect = obs.get("defect") or {}
    return set(defect.get("fields", []))


@pytest.mark.case("TC-FW-009")
@pytest.mark.parametrize("obs", OBSERVATIONS, ids=[repr(o["text"])[:40] for o in OBSERVATIONS])
def test_oracle_matches_spike_observation(obs: dict[str, Any]) -> None:
    text = obs["text"]
    skip = _skip_fields(obs)
    if "words" not in skip:
        assert ORACLE.word_count(text) == obs["words"], "palabras"
    if "characters" not in skip:
        assert ORACLE.character_count(text) == obs["characters"], "caracteres"
    if "keywords" not in skip:
        assert [str(k) for k in ORACLE.keywords(text)] == obs["keywords"], "keyword density"


@pytest.mark.case("TC-FW-009")
def test_defective_observations_differ_from_correct_behaviour() -> None:
    """Para los defectos, el oráculo afirma el comportamiento correcto (distinto del observado)."""
    by_text = {o["text"]: o for o in OBSERVATIONS}
    assert [str(k) for k in ORACLE.keywords("uno dos")] == ["uno=1", "dos=1"]
    assert by_text["uno dos"]["keywords"] == ["uno dos=1"]
    assert ORACLE.keywords("---") == []
    assert TextOracle(CODEPOINT_CHARACTERS).character_count("hola 👋 mundo 🌎") == 14


@pytest.mark.case("TC-FW-009")
def test_top_keywords_uses_first_appearance_for_ties() -> None:
    assert [str(k) for k in ORACLE.top_keywords("beta beta alfa alfa gamma gamma delta")] == [
        "beta=2",
        "alfa=2",
        "gamma=2",
    ]


@pytest.mark.case("TC-FW-009")
def test_profile_is_immutable() -> None:
    with pytest.raises(AttributeError):
        WORDCOUNTER_PROFILE.keyword_min_utf16_length = 1  # type: ignore[misc]
