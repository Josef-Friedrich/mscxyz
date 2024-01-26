"""Test the command line interface using subprocess."""

from __future__ import annotations

import os

from mscxyz import Score
from tests import helper
from tests.helper import Cli


def test_help() -> None:
    assert "usage: musescore-manager" in Cli("--help").sysexit()


class TestOptionBackup:
    def test_exists(self) -> None:
        score: Score = Cli("--backup").score()
        assert score.backup_file.is_file()

    def test_size(self) -> None:
        score: Score = Cli("--backup", "--dry-run").score()
        assert os.path.getsize(score.path) == os.path.getsize(score.backup_file)


class TestOptionBail:
    def test_no_bail(self) -> None:
        assert "XMLSyntaxError" in Cli(helper.get_file("broken.mscx")).stdout()

    def test_bail(self) -> None:
        assert (
            "XMLSyntaxError" in Cli("--bail", helper.get_file("broken.mscx")).sysexit()
        )
