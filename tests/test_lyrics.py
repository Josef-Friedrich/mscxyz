"""Test submodule “lyrics.py”."""

from __future__ import annotations

from typing import Sequence

import pytest

from mscxyz import Score, utils
from tests import helper
from tests.helper import cli, cli_legacy


def is_extraction(score: Score, numbers: int | Sequence[int]) -> bool:
    if isinstance(numbers, int):
        numbers = [numbers]
    for n in numbers:
        if not score.change_path(suffix=n).exists():
            return False
    return True


@pytest.fixture
def lyrics() -> Score:
    return helper.get_score("lyrics.mscz", version=4)


class TestLyricsExtraction:
    @pytest.mark.legacy
    def test_without_arguments_legacy(self, lyrics: Score) -> None:
        cli_legacy("lyrics", lyrics)
        assert is_extraction(lyrics, [1, 2, 3])

    def test_without_arguments(self, lyrics: Score) -> None:
        cli(lyrics)
        assert not is_extraction(lyrics, [1, 2, 3])

    @pytest.mark.legacy
    def test_extract_all_legacy(self, lyrics: Score) -> None:
        cli_legacy("lyrics", "--extract", "all", lyrics)
        assert is_extraction(lyrics, [1, 2, 3])

    def test_extract_all(self, lyrics: Score) -> None:
        cli("--extract-lyrics", "all", lyrics)
        assert is_extraction(lyrics, [1, 2, 3])

    @pytest.mark.legacy
    def test_extract_by_number_legacy(self, lyrics: Score) -> None:
        cli_legacy("lyrics", "--extract", "2", lyrics)
        assert is_extraction(lyrics, 2)
        assert not is_extraction(lyrics, [1, 3])

    def test_extract_by_number(self, lyrics: Score) -> None:
        cli("--extract-lyrics", "2", lyrics)
        assert is_extraction(lyrics, 2)
        assert not is_extraction(lyrics, [1, 3])


class TestLyricsFix:
    def _test_fix(self, version: int = 2) -> None:
        score_path = helper.get_file("lyrics-fix.mscx", version)
        cli_legacy("lyrics", "--fix", score_path)
        score = helper.reload(score_path)
        self.lyrics = score.lyrics.lyrics

        text: list[str] = []
        syllabic: list[str] = []
        for element in self.lyrics:
            tag = element.element
            tag_text = tag.find("text")

            text.append(utils.xml.get_text_safe(tag_text))
            tag_syllabic = tag.find("syllabic")

            syllabic_text = utils.xml.get_text(tag_syllabic)
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

    def test_fix(self) -> None:
        self._test_fix(version=2)
        self._test_fix(version=3)


class TestLyricsRemap:
    def test_remap(self) -> None:
        score_path = helper.get_file("lyrics-remap.mscx")
        cli_legacy("lyrics", "--remap", "2:6", score_path)
        score = helper.reload(score_path)
        text: list[str] = []
        for element in score.lyrics.lyrics:
            tag = element.element
            tag_text = tag.find("no")

            text_no = utils.xml.get_text(tag_text)
            if text_no:
                no = text_no
            else:
                no = "0"
            text.append(no)

        assert text == ["0", "5", "2", "3", "4"]
