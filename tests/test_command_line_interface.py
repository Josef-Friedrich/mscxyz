"""Test the command line interface using subprocess."""
from __future__ import annotations

import os
import subprocess
from unittest import mock

import pytest

from mscxyz import Score
from tests import helper
from tests.helper import cli, cli_legacy


def test_help() -> None:
    output: bytes = subprocess.check_output(("musescore-manager", "--help"))
    assert "usage: musescore-manager" in str(output)


@pytest.mark.legacy
def test_help_legacy() -> None:
    output: bytes = subprocess.check_output(("mscx-manager", "--help"))
    assert "usage: mscx-manager" in str(output)


class TestOptionBackup:
    def test_exists(self, score: Score) -> None:
        cli("--backup", score)
        assert os.path.isfile(score.backup_file)

    @pytest.mark.legacy
    def test_exists_legacy(self, score: Score) -> None:
        cli_legacy("--backup", "meta", score)
        assert os.path.isfile(score.backup_file)

    def test_size(self, score: Score) -> None:
        cli("--backup", "--dry-run", score)
        assert os.path.getsize(score.path) == os.path.getsize(score.backup_file)

    @pytest.mark.legacy
    def test_size_legacy(self, score: Score) -> None:
        cli_legacy("--backup", "meta", score)
        assert os.path.getsize(score.path) == os.path.getsize(score.backup_file)


class TestExport:
    def execute(self, extension: str) -> tuple[mock.Mock, str]:
        tmp: str = helper.get_file("simple.mscx")
        with mock.patch("mscxyz.score.utils.execute_musescore") as mscore_function:
            cli_legacy("export", "--extension", extension, tmp)
        return mscore_function, tmp

    def test_valid_extension(self) -> None:
        mscore_function, tmp = self.execute("mp3")
        args = mscore_function.call_args_list[0][0][0]
        assert args[0] == "--export-to"
        assert args[1] == tmp.replace("mscx", "mp3")
        assert args[2] == tmp

    def test_export_fails(self) -> None:
        with pytest.raises(ValueError) as excinfo:
            self.execute("xxx")
        assert (
            str(excinfo.value)
            == "Unsupported extension: xxx! Supported extensions: ('mscz', 'mscx', 'spos', 'mpos', 'pdf', 'svg', 'png', 'wav', 'mp3', 'ogg', 'flac', 'mid', 'midi', 'kar', 'musicxml', 'xml', 'mxl', 'brf', 'mei')"
        )
