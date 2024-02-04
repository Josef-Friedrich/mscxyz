"""Test module “cli.py”."""

import re

import pytest
from pytest import CaptureFixture

from mscxyz.cli import execute, parser
from tests.helper import Cli


class TestArgparse:
    def test_args_general(self) -> None:
        args = parser.parse_args(["."])
        assert args.general_backup is False
        assert args.general_colorize is False
        assert args.general_dry_run is False
        assert args.selection_glob == "*.msc[xz]"
        assert args.general_mscore is False
        assert args.general_verbose == 0
        assert args.path == ["."]

    def test_args_clean(self) -> None:
        args = parser.parse_args(["--clean", "."])
        assert args.style_clean

    def test_args_export(self) -> None:
        args = parser.parse_args(["--export", "pdf", "."])
        assert args.export_extension == "pdf"

    def test_args_general_lyrics(self) -> None:
        args = parser.parse_args(["--fix-lyrics", "."])
        assert args.lyrics_fix
        assert args.lyrics_remap is None

    def test_args_general_meta(self) -> None:
        args = parser.parse_args(["--synchronize", "."])
        assert args.meta_clean is None
        assert args.meta_json is False
        assert args.meta_set is None
        assert args.meta_sync

    def test_args_general_rename(self) -> None:
        args = parser.parse_args(["--rename", "$title ($composer)", "."])
        assert args.rename_rename == "$title ($composer)"
        assert args.rename_alphanum is False
        assert args.rename_ascii is False
        assert args.rename_target is None


class TestVerbosity:
    def test_0(self) -> None:
        args = parser.parse_args([])
        assert args.general_verbose == 0

    def test_1(self) -> None:
        args = parser.parse_args(["-v"])
        assert args.general_verbose == 1

    def test_2(self) -> None:
        args = parser.parse_args(["-vv"])
        assert args.general_verbose == 2


class TestCommandlineInterface:
    def test_help_short(self) -> None:
        with pytest.raises(SystemExit) as e:
            execute(["-h"])
        assert e.value.code == 0

    def test_help_long(self) -> None:
        with pytest.raises(SystemExit) as e:
            execute(["--help"])
        assert e.value.code == 0

    def test_help_text(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            execute(["-h"])
        capture = capsys.readouterr()
        assert "[-h]" in capture.out


def test_option_help() -> None:
    stderr = Cli("--help", append_score=False).sysexit()
    assert "notation software MuseScore" in stderr


def test_version() -> None:
    stderr = Cli("--version").sysexit()
    assert re.search("[^ ]* [^ ]*", stderr)
