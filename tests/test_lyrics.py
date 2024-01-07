"""Test submodule “lyrics.py”."""

from __future__ import annotations

import os

from mscxyz import utils
from tests import helper
from tests.helper import cli_legacy


class TestLyrics:
    def setup_method(self) -> None:
        self.score_path = helper.get_file("lyrics.mscx")

    def assert_lyrics_file_exists(self, number: int) -> None:
        assert os.path.isfile(
            self.score_path.replace(".mscx", "_{}.mscx".format(number))
        )

    def _test_without_arguments(self, version: int = 2) -> None:
        self.score_path = helper.get_file("lyrics.mscx", version)
        cli_legacy("lyrics", self.score_path)
        self.assert_lyrics_file_exists(1)
        self.assert_lyrics_file_exists(2)
        self.assert_lyrics_file_exists(3)

    def test_without_arguments(self) -> None:
        self._test_without_arguments(version=2)
        self._test_without_arguments(version=3)

    def _test_extract_all(self, version: int = 2) -> None:
        self.score_path = helper.get_file("lyrics.mscx", version)
        cli_legacy("lyrics", "--extract", "all", self.score_path)
        self.assert_lyrics_file_exists(1)
        self.assert_lyrics_file_exists(2)
        self.assert_lyrics_file_exists(3)

    def test_extract_all(self) -> None:
        self._test_extract_all(version=2)
        self._test_extract_all(version=3)

    def _test_extract_by_number(self, version: int = 2) -> None:
        self.score_path = helper.get_file("lyrics.mscx", version)
        cli_legacy("lyrics", "--extract", "2", self.score_path)
        self.assert_lyrics_file_exists(2)

    def test_extract_by_number(self) -> None:
        self._test_extract_by_number(version=2)
        self._test_extract_by_number(version=3)


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
