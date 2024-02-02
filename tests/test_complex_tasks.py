"""Test the examples from the README.rst file."""

from __future__ import annotations

from tests.helper import Cli


def test_din_a4_compress_rename() -> None:
    score = (
        Cli(
            "--save-in-mscore",
            "--a4",
            "--rename",
            "_Piano_A4",
            "--only-filename",
        )
        .append_score("Im-Fruehtau-zu-Berge.mscz")
        .score()
    )

    dest = score.path.parent / "_Piano_A4.mscz"

    assert dest.exists()
