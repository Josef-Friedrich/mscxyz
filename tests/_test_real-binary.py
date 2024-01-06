"""Test the command line interface using subprocess with the real binary. 

Not meant for tests on Github.

We import no mscxyz specific code here to be able to run the test outside of the venv.

run “pip install -e .” to install the mscxyz command line interface
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

test_dir: str = os.path.dirname(os.path.abspath(__file__))

mscore_executable: str | None = shutil.which("mscore")

if not mscore_executable:
    raise Exception("find binary not found")


mscx_manager_executable: str | None = shutil.which("musescore-manager")

if not mscx_manager_executable:
    raise Exception("musescore-manager binary not found")

executable = Path(mscore_executable)

open_files = False

if not executable.exists():
    raise Exception(f"MuseScore binary not found: {executable}")

if not shutil.which("find"):
    raise Exception("find binary not found")


def get_path(filename: str, version: int = 2) -> Path:
    return Path(test_dir) / "files" / "by_version" / str(version) / filename


def get_file(filename: str, version: int = 2) -> str:
    orig: Path = get_path(filename, version)
    tmp_dir: str = tempfile.mkdtemp()
    tmp: str = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def open_file(file: str | Path) -> None:
    if not open_files:
        return
    """Open a file wiht xdg-open in the background"""
    subprocess.Popen(("xdg-open", str(file)))


def get_file_type(file: str | Path) -> str:
    """Get the type of a file using the `file` command."""
    output: str = subprocess.check_output(
        ("file", "--brief", "--mime", file), encoding="utf-8"
    )
    return output.split(";")[0]


def assert_file_type(file: str | Path, expected: str) -> None:
    """Assert that the type of a file is equal to the expected type."""
    assert get_file_type(file) == expected


@pytest.fixture
def simple4z() -> str:
    return get_file("simple.mscz", version=4)


def invoke(*args: str) -> subprocess.Popen[str]:
    """Invoke musescore-manager with an real mscore executable."""
    p = subprocess.Popen(
        ("musescore-manager", "--executable", str(executable), *args), encoding="utf-8"
    )
    p.communicate()
    return p


def test_executable() -> None:
    assert executable.exists()


@pytest.mark.parametrize(
    "extension,expected",
    [
        ("mscz", "application/zip"),
        ("mscx", "text/xml"),
        ("spos", "text/xml"),
        ("mpos", "text/xml"),
        ("pdf", "application/pdf"),
        ("svg", "image/svg+xml"),
        ("png", "image/png"),
        ("wav", "audio/x-wav"),
        ("mp3", "audio/mpeg"),
        ("ogg", "audio/ogg"),
        ("flac", "audio/flac"),
        ("mid", "audio/midi"),
        ("midi", "audio/midi"),
        ("kar", "audio/midi"),
        ("musicxml", "text/xml"),
        ("xml", "text/xml"),
        ("mxl", "application/zip"),
        ("brf", "text/plain"),
        ("mei", "text/xml"),
    ],
)
def test_export(extension: str, expected: str) -> None:
    tmp: str = get_file("simple.mscz", version=4)
    p = invoke("export", "--extension", extension, tmp)
    assert p.returncode == 0
    numbering = ""
    if extension in ("svg", "png"):
        numbering = "-1"
    dest = Path(tmp.replace(".mscz", f"{numbering}.{extension}"))
    assert dest.exists()
    assert_file_type(dest, expected)


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
    open_file(tmp)
