from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Generator

import pytest

from mscxyz import Score
from mscxyz.fields import FieldsManager
from tests import helper


@pytest.fixture(autouse=True)
def score2x() -> Score:
    """Instantiate a Score object from the file simple.mscx (version 2)."""
    return helper.get_score("simple.mscx", version=2)


@pytest.fixture(autouse=True)
def score3x() -> Score:
    """Instantiate a Score object from the file simple.mscx (version 3)."""
    return helper.get_score("simple.mscx", version=3)


@pytest.fixture(autouse=True)
def score4x() -> Score:
    """Instantiate a Score object from the file simple.mscx (version 4)."""
    return helper.get_score("simple.mscx", version=4)


@pytest.fixture(autouse=True)
def score2z() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 2)."""
    return helper.get_score("simple.mscz", version=2)


@pytest.fixture(autouse=True)
def score3z() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 3)."""
    return helper.get_score("simple.mscz", version=3)


@pytest.fixture(autouse=True)
def score4z() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 4)."""
    return helper.get_score("score.mscz", version=4)


@pytest.fixture(autouse=True, scope="function")
def score() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 4)."""
    return helper.get_score("score.mscz", version=4)


@pytest.fixture(autouse=True)
def fields() -> FieldsManager:
    """Instantiate a Score object from the file simple.mscz (version 4)."""
    return helper.get_fields("score.mscz", version=4)


@pytest.fixture(autouse=True)
def score_path() -> Path:
    return helper.get_path("score.mscz", version=4)


@pytest.fixture(autouse=True)
def score_file() -> str:
    return helper.get_file("score.mscz", version=4)


@pytest.fixture(autouse=True)
def nested_dir() -> Path:
    return Path(helper.get_dir("nested-folders", version=4))


def __chdir(dstdir: Path) -> Generator[Path, Any, None]:
    """https://github.com/ar90n/pytest-chdir"""
    lwd = os.getcwd()
    os.chdir(dstdir)
    try:
        yield dstdir
    finally:
        os.chdir(lwd)


@pytest.fixture
def cwd_tmpdir(tmpdir: Path) -> Generator[Path, Any, None]:
    yield from __chdir(tmpdir)


@pytest.fixture
def cwd_test_path() -> Generator[Path, Any, None]:
    yield from __chdir(Path(__file__).parent)
