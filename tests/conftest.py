from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import Score
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


@pytest.fixture(autouse=True)
def score() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 4)."""
    return helper.get_score("score.mscz", version=4)


@pytest.fixture(autouse=True)
def score_path() -> Path:
    return helper.get_path("score.mscz", version=4)


@pytest.fixture(autouse=True)
def score_file() -> str:
    return helper.get_file("score.mscz", version=4)


@pytest.fixture(autouse=True)
def nested_dir() -> Path:
    return Path(helper.get_dir("nested-folders", version=4))
