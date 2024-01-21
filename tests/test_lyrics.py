"""Test submodule “lyrics.py”."""

from __future__ import annotations

from typing import Sequence

import pytest

import mscxyz
from mscxyz import Score
from tests import helper
from tests.helper import Cli


@pytest.fixture
def lyrics() -> Score:
    return helper.get_score("lyrics.mscz", version=4)


@pytest.mark.parametrize(
    "filename, expected",
    (
        ("score.mscz", 0),
        ("lyrics.mscz", 3),
        ("lyrics_number-of-verses.mscz", 7),
    ),
)
def test_property_number_of_verse(filename: str, expected: int) -> None:
    score = helper.get_score(filename, version=4)
    assert score.lyrics.number_of_verses == expected


def is_extraction(score: Score, numbers: int | Sequence[int]) -> bool:
    if isinstance(numbers, int):
        numbers = [numbers]
    for n in numbers:
        if not score.change_path(suffix=n).exists():
            return False
    return True


class TestLyricsExtraction:
    def test_without_arguments(self, lyrics: Score) -> None:
        Cli("lyrics", lyrics).execute()
        assert not is_extraction(lyrics, [1, 2, 3])

    def test_extract_all(self, lyrics: Score) -> None:
        Cli("--extract-lyrics", "all", lyrics).execute()
        assert is_extraction(lyrics, [1, 2, 3])

    def test_extract_by_number(self, lyrics: Score) -> None:
        Cli("--extract-lyrics", "2", lyrics).execute()
        assert is_extraction(lyrics, 2)
        assert not is_extraction(lyrics, [1, 3])


@pytest.mark.parametrize(
    "version",
    mscxyz.supported_versions,
)
def test_fix(version: int) -> None:
    score = Cli("--fix-lyrics").append_score("lyrics-fix.mscx", version).score()
    lyrics = score.lyrics.elements

    text: list[str] = []
    syllabic: list[str] = []
    for element in lyrics:
        tag = element.element
        tag_text = tag.find("text")

        text.append(score.xml.get_text_safe(tag_text))
        tag_syllabic = tag.find("syllabic")

        syllabic_text = score.xml.get_text(tag_syllabic)
        if syllabic_text:
            syllabic.append(syllabic_text)

    assert text == [
        "Al",
        "K\xf6pf",
        "le",
        "chen",
        "mei",
        "un",
        "ne",
        "ters",
        "En",
        "Was",
        "te",
        "si",
        "lein.",
        "lein.",
    ]

    assert syllabic == [
        "begin",
        "begin",
        "end",
        "end",
        "begin",
        "begin",
        "end",
        "end",
        "begin",
        "begin",
        "middle",
        "middle",
        "end",
        "end",
    ]


def test_remap() -> None:
    score = helper.get_score("lyrics-remap.mscx")

    Cli("lyrics", "--remap", "2:6", score, legacy=True).execute()
    new_score = score.reload()
    nos: list[int] = []

    for element in new_score.lyrics.elements:
        nos.append(element.no)

    assert nos == [1, 6, 3, 4, 5]
