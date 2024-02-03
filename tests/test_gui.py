"""Test the examples from the README.rst file."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.helper import Cli, get_file, invoke, open_in_gui


@pytest.mark.gui
def test_din_a4_compress_rename() -> None:
    score = (
        Cli(
            "--save-in-mscore",
            "--a4",
            "--rename",
            "_Piano_A4",
            "--only-filename",
            "--staff-space",
            "1.75mm",
            "--margin",
            "15mm",
        )
        .append_score("Im-Fruehtau-zu-Berge.mscz")
        .score()
    )
    dest = score.new(filename="_Piano_A4.mscz")
    assert dest.exists()
    open_in_gui(dest)


@pytest.mark.gui
def test_set_style() -> None:
    tmp = get_file("Ragtime_3.mscz", version=4)
    invoke(
        "style",
        "--set-style",
        "pageWidth",
        "4.13",
        "--set-style",
        "pageHeight",
        "5.83",
        "--set-style",
        "pagePrintableWidth",
        "3.35",
        tmp,
    )
    assert Path(tmp).exists()


@pytest.mark.gui
def test_meta() -> None:
    tmp = get_file("no-vbox.mscz", version=4)
    invoke(
        "meta",
        "--set-field",
        "vbox_title",
        "This is a new title",
        "--set-field",
        "vbox_subtitle",
        "This is a new subtitle",
        "--set-field",
        "vbox_composer",
        "This is a new composer",
        "--set-field",
        "vbox_lyricist",
        "This is a new lyricist",
        tmp,
    )
    assert Path(tmp).exists()
