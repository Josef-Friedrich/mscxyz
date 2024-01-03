"""Test the command line interface using subprocess."""

import os
import subprocess
from unittest import mock

import mscxyz
from tests import helper


def test_help() -> None:
    output: bytes = subprocess.check_output(("mscx-manager", "--help"))
    assert "usage: mscx-manager" in str(output)


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


@mock.patch("mscxyz.score.utils.mscore")
def test_export(mscore_function: mock.Mock) -> None:
    tmp: str = helper.get_file("simple.mscx")
    mscxyz.execute(["export", "--extension", "mp3", tmp])
    args = mscore_function.call_args_list[0][0][0]
    assert args[0] == "--export-to"
    assert args[1] == tmp.replace("mscx", "mp3")
    assert args[2] == tmp
