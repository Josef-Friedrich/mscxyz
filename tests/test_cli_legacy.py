"""Test module “cli.py”."""

import re

import pytest
from pytest import CaptureFixture

from mscxyz.cli_legacy import execute, parser
from tests.helper import Cli


class TestArgs:
    def test_args_general(self) -> None:
        args = parser.parse_args(["help", "."])
        assert args.general_backup is False
        assert args.general_colorize is False
        assert args.general_dry_run is False
        assert args.selection_glob == "*.msc[xz]"
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
        assert args.lyrics_extract_legacy == "all"
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
    def test_all(self) -> None:
        stderr = Cli("help", "all", legacy=True, append_score=False).sysexit()
        assert len(stderr) > 150

    def test_restructuredtext(self) -> None:
        stderr = Cli("help", "--rst", "all", legacy=True, append_score=False).sysexit()
        assert ".. code-block:: text" in stderr

    def test_markdown(self) -> None:
        stderr = Cli(
            "help", "--markdown", "all", legacy=True, append_score=False
        ).sysexit()
        assert "```" in stderr

    def test_functions_in_all(self) -> None:
        stderr = Cli("help", "all", legacy=True, append_score=False).sysexit()
        assert "%asciify{text}" in stderr

    def test_functions_in_rename(self) -> None:
        stderr = Cli("rename", "--help", legacy=True, append_score=False).sysexit()
        assert "%asciify{text}" in stderr


class TestVersion:
    def test_version(self) -> None:
        stderr = Cli("--version").sysexit()
        assert re.search("[^ ]* [^ ]*", stderr)
