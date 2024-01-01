"""Test module “cli.py”."""

import re

import pytest
from pytest import CaptureFixture

import mscxyz
from mscxyz import cli
from tests import helper


class TestArgs:
    def test_args_general(self):
        args = cli.parser.parse_args(["help", "."])
        assert args.general_backup is False
        assert args.general_colorize is False
        assert args.general_dry_run is False
        assert args.general_glob == "*.msc[xz]"
        assert args.general_mscore is False
        assert args.general_verbose == 0
        assert args.path == "."

    def test_args_clean(self):
        args = cli.parser.parse_args(["clean", "."])
        assert args.clean_style is None
        assert args.subcommand == "clean"

    def test_args_export(self):
        args = cli.parser.parse_args(["export", "."])
        assert args.export_extension == "pdf"
        assert args.subcommand == "export"

    def test_args_help(self):
        args = cli.parser.parse_args(["help", "."])
        assert args.help_markdown is False
        assert args.help_rst is False
        assert args.subcommand == "help"

    def test_args_general_lyrics(self):
        args = cli.parser.parse_args(["lyrics", "."])
        assert args.lyrics_extract == "all"
        assert args.lyrics_fix is False
        assert args.lyrics_remap is None
        assert args.subcommand == "lyrics"

    def test_args_general_meta(self):
        args = cli.parser.parse_args(["meta", "."])
        assert args.meta_clean is None
        assert args.meta_json is False
        assert args.meta_set is None
        assert args.meta_sync is False
        assert args.subcommand == "meta"

    def test_args_general_rename(self):
        args = cli.parser.parse_args(["rename", "."])
        assert args.rename_alphanum is False
        assert args.rename_ascii is False
        assert args.rename_format == "$combined_title ($combined_composer)"
        assert args.rename_target is None
        assert args.subcommand == "rename"


def test_cap_sys(capsys: CaptureFixture[str]) -> None:
    print("lol")
    captured = capsys.readouterr()
    assert captured.out == "lol\n"


class TestCommandlineInterface:
    def test_help_short(self):
        with pytest.raises(SystemExit) as e:
            with helper.Capturing():
                mscxyz.execute(["-h"])
        assert e.value.code == 0

    def test_help_long(self):
        with pytest.raises(SystemExit) as e:
            with helper.Capturing():
                mscxyz.execute(["--help"])
        assert e.value.code == 0

    def test_without_arguments(self):
        with pytest.raises(SystemExit) as e:
            with helper.Capturing("stderr"):
                mscxyz.execute()
        assert e.value.code == 2

    def test_help_text(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["-h"])
        assert "[-h]" in output[0]


class TestHelp:
    def test_all(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["help", "all"])
        assert len(output) > 150

    def test_restructuredtext(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["help", "--rst", "all"])
        assert ".. code-block:: text" in output

    def test_markdown(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["help", "--markdown", "all"])
        assert "```" in output

    def test_functions_in_all(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["help", "all"])
        assert "%asciify{text}" in "\n".join(output)

    def test_functions_in_rename(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["rename", "--help"])
        assert "%asciify{text}" in "\n".join(output)


class TestVersion:
    def test_version(self):
        with pytest.raises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(["--version"])

        result = re.search("[^ ]* [^ ]*", output[0])
        assert result
