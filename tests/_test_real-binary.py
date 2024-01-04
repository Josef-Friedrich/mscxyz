"""Test the command line interface using subprocess with the real binary. Not meant for tests on Github."""

from __future__ import annotations

# from tests import helper
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

test_dir = os.path.dirname(os.path.abspath(__file__))

executable = Path("/usr/local/bin/mscore")


def get_path(filename: str, version: int = 2) -> Path:
    return Path(test_dir) / "files" / "by_version" / str(version) / filename


def get_file(filename: str, version: int = 2) -> str:
    orig: Path = get_path(filename, version)
    tmp_dir: str = tempfile.mkdtemp()
    tmp: str = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def open_file(file: str | Path) -> str:
    return subprocess.check_output(("xdg-open", str(file))).decode("utf-8")


@pytest.fixture
def simple4z() -> str:
    return get_file("simple.mscz", version=4)


@pytest.mark.skip(reason="no way of currently testing this")
def invoke(*args: str) -> str:
    """Invoke mscx-manager with an real mscore executable."""
    return subprocess.check_output(
        ("mscx-manager", "--executable", str(executable), *args)
    ).decode("utf-8")


def test_executable() -> None:
    assert executable.exists()


def test_export_svg(simple4z: str) -> None:
    invoke("export", "--extension", "svg", simple4z)
    dest = Path(simple4z.replace(".mscz", "-1.svg"))
    assert dest.exists()


def test_export_pdf(simple4z: str) -> None:
    invoke("export", simple4z)
    dest = Path(simple4z.replace(".mscz", ".pdf"))
    assert dest.exists()
    open_file(dest)
