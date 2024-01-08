"""Test module “cli.py”."""

import re

import pytest
from pytest import CaptureFixture

from mscxyz.cli_legacy import execute, parser
from tests.helper import cli_legacy


class TestArgs:
    def test_args_general(self) -> None:
        args = parser.parse_args(["help", "."])
        assert args.general_backup is False
        assert args.general_colorize is False
        assert args.general_dry_run is False
        assert args.general_glob == "*.msc[xz]"
        assert args.general_mscore is False
        assert args.general_verbose == 0
        assert args.path == "."

    def test_args_clean(self) -> None:
        args = parser.parse_args(["clean", "."])
        assert args.clean_style is None
        assert args.subcommand == "clean"

    def test_args_export(self) -> None:
        args = parser.parse_args(["export", "."])
        assert args.export_extension == "pdf"
        assert args.subcommand == "export"

    def test_args_help(self) -> None:
        args = parser.parse_args(["help", "."])
        assert args.help_markdown is False
        assert args.help_rst is False
        assert args.subcommand == "help"

    def test_args_general_lyrics(self) -> None:
        args = parser.parse_args(["lyrics", "."])
        assert args.lyrics_extract == "all"
        assert args.lyrics_fix is False
        assert args.lyrics_remap is None
        assert args.subcommand == "lyrics"

    def test_args_general_meta(self) -> None:
        args = parser.parse_args(["meta", "."])
        assert args.meta_clean is None
        assert args.meta_json is False
        assert args.meta_set is None
        assert args.meta_sync is False
        assert args.subcommand == "meta"

    def test_args_general_rename(self) -> None:
        args = parser.parse_args(["rename", "."])
        assert args.rename_alphanum is False
        assert args.rename_ascii is False
        assert args.rename_format == "$combined_title ($combined_composer)"
        assert args.rename_target is None
        assert args.subcommand == "rename"


class TestCommandlineInterface:
    def test_help_short(self) -> None:
        with pytest.raises(SystemExit) as e:
            execute(["-h"])
        assert e.value.code == 0

    def test_help_long(self) -> None:
        with pytest.raises(SystemExit) as e:
            execute(["--help"])
        assert e.value.code == 0

    def test_without_arguments(self) -> None:
        with pytest.raises(SystemExit) as e:
            execute()
        assert e.value.code == 2

    def test_help_text(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            execute(["-h"])
        capture = capsys.readouterr()
        assert "[-h]" in capture.out


class TestHelp:
    def test_all(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("help", "all")
        capture = capsys.readouterr()
        assert len(capture.out) > 150

    def test_restructuredtext(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("help", "--rst", "all")
        capture = capsys.readouterr()
        assert ".. code-block:: text" in capture.out

    def test_markdown(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("help", "--markdown", "all")
        capture = capsys.readouterr()
        assert "```" in capture.out

    def test_functions_in_all(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("help", "all")
        capture = capsys.readouterr()
        assert "%asciify{text}" in capture.out

    def test_functions_in_rename(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("rename", "--help")
        capture = capsys.readouterr()
        assert "%asciify{text}" in capture.out


class TestVersion:
    def test_version(self, capsys: CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit):
            cli_legacy("--version")
        capture = capsys.readouterr()
        assert re.search("[^ ]* [^ ]*", capture.out)