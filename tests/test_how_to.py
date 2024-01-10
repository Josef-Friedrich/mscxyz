"""Test the examples from the README.rst file."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import Score
from tests import helper
from tests.helper import assert_file_type, cli, stdout, sysexit


class TestSpecifyMusescoreFiles:
    def test_without_an_argument(self) -> None:
        assert "tests/files/by_version/4/score.mscz" in stdout("--list-files")

    def test_dot_to_specify_pwd(self) -> None:
        assert (
            "tests/files/by_version/4/nested-folders/level1/level2/level3/score3.mscz"
            in stdout("-L", ".")
        )

    def test_pass_multiple_files(self) -> None:
        file2 = "tests/files/by_version/2/score.mscz"
        file3 = "tests/files/by_version/3/score.mscz"
        file4 = "tests/files/by_version/4/score.mscz"

        output = stdout(
            "-L",
            file2,
            file3,
            file4,
        )

        assert file2 in output
        assert file3 in output
        assert file4 in output

    def test_pass_multiple_directories(self) -> None:
        dir2 = "tests/files/by_version/2"
        dir3 = "tests/files/by_version/3"
        dir4 = "tests/files/by_version/4"

        output = stdout(
            "-L",
            dir2,
            dir3,
            dir4,
        )

        assert dir2 in output
        assert dir3 in output
        assert dir4 in output

    def test_glob(self) -> None:
        output = stdout("-L", "--glob", "*/by_version/4/*.mscz")
        assert "/by_version/4/" in output
        assert ".mscz" in output
        assert "/by_version/3/" not in output
        assert ".mscx" not in output

    def test_mscz_only(self) -> None:
        output = stdout("-L", "--mscz")
        assert "score.mscz" in output
        assert "score.mscx" not in output

    def test_mscx_only(self) -> None:
        output = stdout("-L", "--mscx")
        assert "score.mscz" not in output
        assert "simple.mscx" in output

    def test_dont_mix_mscz_and_mscx(self) -> None:
        assert "--mscx: not allowed with argument --mscz" in sysexit(
            "-L", "--mscz", "--mscx"
        )

    def test_dont_mix_mscz_and_glob(self) -> None:
        assert "--glob: not allowed with argument --mscz" in sysexit(
            "-L", "--mscz", "--glob", "*"
        )

    def test_dont_mix_mscx_and_glob(self) -> None:
        assert "--glob: not allowed with argument --mscx" in sysexit(
            "-L", "--mscx", "-glob", "*"
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
        score = helper.get_score("simple.mscz", version=4)
        cli("--export", extension, score)
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
    @pytest.mark.skip(reason="TODO")
    def test_set_style_single(self, score: Score) -> None:
        assert score.style.get("staffDistance") == "6.5"
        cli("--style", "staffDistance", "7.5", score)
        assert score.reload(save=True).style.get("staffDistance") == "7.5"

    @pytest.mark.skip(reason="TODO")
    def test_set_style_multiple(self, score: Score) -> None:
        assert score.style.get("staffUpperBorder") == "7"
        assert score.style.get("staffLowerBorder") == "7"

        cli(
            "--style",
            "staffUpperBorder",
            "5.5",
            "--style",
            "staffLowerBorder",
            "5.5",
            score,
        )
        assert score.reload(save=True).style.get("staffUpperBorder") == "7.5"
        assert score.reload(save=True).style.get("staffLowerBorder") == "7.5"


class TestAutocomplete:
    def test_bash(self) -> None:
        assert "# AUTOMATICALLY GENERATED by `shtab`" in sysexit(
            "--print-completion", "bash"
        )

    def test_zsh(self) -> None:
        assert "# AUTOMATICALLY GENERATED by `shtab`" in sysexit(
            "--print-completion", "zsh"
        )

    def test_tcsh(self) -> None:
        assert "# AUTOMATICALLY GENERATED by `shtab`" in sysexit(
            "--print-completion", "tcsh"
        )
