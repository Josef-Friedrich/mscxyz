"""Test the examples from the README.rst file."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import Score
from tests import helper
from tests.helper import Cli, assert_file_type, cli


class TestSpecifyMusescoreFiles:
    def test_without_an_argument(self) -> None:
        assert (
            "tests/files/by_version/4/score.mscz"
            in Cli("--list-files", append_score=False).stdout()
        )

    def test_dot_to_specify_pwd(self) -> None:
        assert (
            "tests/files/by_version/4/nested-folders/level1/level2/level3/score3.mscz"
            in Cli("-L", ".").stdout()
        )

    def test_pass_multiple_files(self) -> None:
        file2 = "tests/files/by_version/2/score.mscz"
        file3 = "tests/files/by_version/3/score.mscz"
        file4 = "tests/files/by_version/4/score.mscz"

        stdout = Cli(
            "-L",
            file2,
            file3,
            file4,
        ).stdout()

        assert file2 in stdout
        assert file3 in stdout
        assert file4 in stdout

    def test_pass_multiple_directories(self) -> None:
        dir2 = "tests/files/by_version/2"
        dir3 = "tests/files/by_version/3"
        dir4 = "tests/files/by_version/4"

        stdout = Cli(
            "-L",
            dir2,
            dir3,
            dir4,
        ).stdout()

        assert dir2 in stdout
        assert dir3 in stdout
        assert dir4 in stdout

    def test_glob(self) -> None:
        stdout = Cli(
            "-L", "--glob", "*/by_version/4/*.mscz", append_score=False
        ).stdout()
        assert "/by_version/4/" in stdout
        assert ".mscz" in stdout
        assert "/by_version/3/" not in stdout
        assert ".mscx" not in stdout

    def test_mscz_only(self) -> None:
        stdout = Cli("-L", "--mscz", append_score=False).stdout()
        assert "score.mscz" in stdout
        assert "score.mscx" not in stdout

    def test_mscx_only(self) -> None:
        stdout = Cli("-L", "--mscx", append_score=False).stdout()
        assert "score.mscz" not in stdout
        assert "simple.mscx" in stdout

    def test_dont_mix_mscz_and_mscx(self) -> None:
        assert (
            "--mscx: not allowed with argument --mscz"
            in Cli("-L", "--mscz", "--mscx").sysexit()
        )

    def test_dont_mix_mscz_and_glob(self) -> None:
        assert (
            "--glob: not allowed with argument --mscz"
            in Cli("-L", "--mscz", "--glob", "*").sysexit()
        )

    def test_dont_mix_mscx_and_glob(self) -> None:
        assert (
            "--glob: not allowed with argument --mscx"
            in Cli("-L", "--mscx", "-glob", "*").sysexit()
        )


@pytest.mark.slow
@pytest.mark.skipif(
    helper.mscore_executable is None, reason="mscore executable not found"
)
class TestExport:
    def get_export_path(self, score: Score, extension: str) -> Path:
        numbering = ""
        if extension in ("svg", "png"):
            numbering = "-1"
        return Path(str(score.path).replace(".mscz", f"{numbering}.{extension}"))

    @pytest.mark.parametrize(
        "extension, expected",
        [
            ("mscz", "application/zip"),
            ("mscx", "text/xml"),
            ("spos", "text/xml"),
            ("mpos", "text/xml"),
            ("pdf", "application/pdf"),
            ("svg", "image/svg+xml"),
            ("png", "image/png"),
            ("wav", "audio/x-wav"),
            ("mp3", "audio/mpeg"),
            ("ogg", "audio/ogg"),
            ("flac", "audio/flac"),
            ("mid", "audio/midi"),
            ("midi", "audio/midi"),
            ("kar", "audio/midi"),
            ("musicxml", "text/xml"),
            ("xml", "text/xml"),
            ("mxl", "application/zip"),
            ("brf", "text/plain"),
            ("mei", "text/xml"),
        ],
    )
    def test_cli(self, extension: str, expected: str) -> None:
        score = Cli("--export", extension).score()
        dest = self.get_export_path(score, extension)
        assert dest.exists()
        assert_file_type(dest, expected)

    def test_python_api(self) -> None:
        score = helper.get_score("simple.mscz", version=4)
        score.export.to_extension("musicxml")
        dest = self.get_export_path(score, "musicxml")
        assert dest.exists()
        assert_file_type(dest, "text/xml")


class TestStyle:
    def test_set_style_single(self) -> None:
        score = Cli("--style", "staffDistance", "7.5").score()
        assert score.style.get("staffDistance") == "7.5"

    def test_set_style_multiple(self, score: Score) -> None:
        score = Cli(
            "-s",
            "staffUpperBorder",
            "5.5",
            "--style",
            "staffLowerBorder",
            "5.5",
            score,
        ).score()
        assert score.style.get("staffUpperBorder") == "5.5"
        assert score.style.get("staffLowerBorder") == "5.5"

    def test_set_text_fonts(self, score: Score) -> None:
        sty = score.style
        assert sty.get("defaultFontFace") == "FreeSerif"
        assert sty.get("titleFontFace") == "FreeSerif"
        assert sty.get("romanNumeralFontFace") == "Campania"

        cli("--text-font", "Alegreya", score)

        new = sty.reload()
        assert new.get("defaultFontFace") == "Alegreya"
        assert new.get("titleFontFace") == "Alegreya"
        assert new.get("romanNumeralFontFace") == "Campania"

    def test_set_title_fonts(self, score: Score) -> None:
        sty = score.style
        assert sty.get("titleFontFace") == "FreeSerif"
        assert sty.get("subTitleFontFace") == "FreeSerif"

        cli("--title-font", "Alegreya Sans", score)

        new = sty.reload()
        assert new.get("defaultFontFace") == "FreeSerif"
        assert new.get("titleFontFace") == "Alegreya Sans"
        assert new.get("subTitleFontFace") == "Alegreya Sans"

    def test_set_musical_symbols_font(self, score: Score) -> None:
        sty = score.style
        assert sty.get("musicalSymbolFont") == "Leland"
        assert sty.get("dynamicsFont") == "Leland"
        assert sty.get("dynamicsFontFace") == "FreeSerif"

        cli("--musical-symbol-font", "Emmentaler", score)

        new = sty.reload()
        assert new.get("musicalSymbolFont") == "Emmentaler"
        assert new.get("dynamicsFont") == "Emmentaler"
        assert new.get("dynamicsFontFace") == "Emmentaler"

    def test_set_musical_symbol_font(self, score: Score) -> None:
        sty = score.style
        assert sty.get("musicalSymbolFont") == "Leland"
        assert sty.get("dynamicsFont") == "Leland"
        assert sty.get("dynamicsFontFace") == "FreeSerif"

        cli("--musical-symbol-font", "Emmentaler", score)

        new = sty.reload()
        assert new.get("musicalSymbolFont") == "Emmentaler"
        assert new.get("dynamicsFont") == "Emmentaler"
        assert new.get("dynamicsFontFace") == "Emmentaler"

    def test_set_musical_text_font(self, score: Score) -> None:
        sty = score.style
        assert sty.get("musicalTextFont") == "Leland Text"

        cli("--musical-text-font", "Emmentaler Text", score)

        new = sty.reload()
        assert new.get("musicalTextFont") == "Emmentaler Text"


class TestAutocomplete:
    def test_bash(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "bash").sysexit()
        )

    def test_zsh(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "zsh").sysexit()
        )

    def test_tcsh(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "tcsh").sysexit()
        )
