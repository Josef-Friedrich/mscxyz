"""Test the command line interface using subprocess with the real binary. Not meant for tests on Github."""

import subprocess
from pathlib import Path

import pytest

from tests import helper

executable = Path("/usr/local/bin/mscore")

# Remove this markers to test the real binary.
pytestmark = pytest.mark.skip("all tests still WIP")


@pytest.mark.skip(reason="no way of currently testing this")
def invoke(*args: str) -> str:
    """Invoke mscx-manager with an real mscore executable."""
    return subprocess.check_output(
        ("mscx-manager", "--executable", str(executable), *args)
    ).decode("utf-8")


@pytest.mark.skipif(not executable.exists(), reason="mscore not installed")
def test_export_svg() -> None:
    tmp: str = helper.get_file("simple.mscz", version=4)
    invoke("export", "--extension", "svg", tmp)
    dest = Path(tmp.replace(".mscz", "-1.svg"))
    assert dest.exists()
