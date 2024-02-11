"""Test the command line interface using subprocess."""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from tests import helper
from tests.helper import Cli


class TestExport:
    def test_valid_extension(self) -> None:
        tmp: str = helper.get_file("simple.mscx")
        with mock.patch("mscxyz.score.utils.execute_musescore") as mscore_function:
            Cli("--export", "mp3", tmp).execute()
            args = mscore_function.call_args_list[0][0][0]
            assert args[0] == "--export-to"
            assert args[1] == tmp.replace("mscx", "mp3")
            assert args[2] == tmp

    def test_export_fails(self) -> None:
        assert (
            "musescore-manager: error: argument -E/--export: invalid choice: 'xxx' (choose from 'mscz', 'mscx', 'spos', 'mpos', 'pdf', 'svg', 'png', 'wav', 'mp3', 'ogg', 'flac', 'mid', 'midi', 'kar', 'musicxml', 'xml', 'mxl', 'brf', 'mei')"
            in Cli("--export", "xxx").sysexit()
        )


@pytest.mark.slow
def test_compress() -> None:
    score = Cli("--compress").append_score("simple.mscx", 3).score()
    dest = str(score.path).replace(".mscx", ".mscz")
    assert score.exists()
    assert Path(dest).exists()


@pytest.mark.slow
def test_remove_origin() -> None:
    score = Cli("--compress", "--remove-origin").append_score("simple.mscx", 3).score()
    dest = str(score.path).replace(".mscx", ".mscz")
    assert not score.exists()
    assert Path(dest).exists()
