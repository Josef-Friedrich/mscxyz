"""Test the examples from the README.rst file."""

from __future__ import annotations

from pathlib import Path

from lxml.etree import _Element

from mscxyz import Score, list_score_paths
from tests.helper import cli, stdout

def test_specify_musescore_files(score_file: str) -> None:
    stdout("--list-files")
