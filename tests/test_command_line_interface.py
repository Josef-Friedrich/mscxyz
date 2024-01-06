"""Test the command line interface using subprocess."""
from __future__ import annotations

import os
import subprocess
from unittest import mock

import pytest

import mscxyz
from tests import helper


def test_help() -> None:
    output: bytes = subprocess.check_output(("musescore-manager", "--help"))
    assert "usage: musescore-manager" in str(output)


class TestBackup:
    tmp: str

    backup: str

    def setup_method(self) -> None:
        self.tmp = helper.get_file("simple.mscx")
        self.backup = self.tmp.replace(".mscx", "_bak.mscx")
        mscxyz.execute(["--backup", "meta", self.tmp])

    def test_exists(self) -> None:
        assert os.path.isfile(self.backup)

    def test_size(self) -> None:
        assert os.path.getsize(self.tmp) == os.path.getsize(self.backup)


class TestExport:
    def execute(self, extension: str) -> tuple[mock.Mock, str]:
        tmp: str = helper.get_file("simple.mscx")
        with mock.patch("mscxyz.score.utils.execute_musescore") as mscore_function:
            mscxyz.execute(["export", "--extension", extension, tmp])
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
