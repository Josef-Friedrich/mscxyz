from __future__ import annotations

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


# @pytest.fixture(scope="session", autouse=True)
# def score4x() -> Score:
#     """Instantiate a Score object from the file simple.mscx (version 4)."""
#     return helper.get_score("simple.mscx", version=4)


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
    return helper.get_score("simple.mscz", version=4)


@pytest.fixture(autouse=True)
def score() -> Score:
    """Instantiate a Score object from the file simple.mscz (version 4)."""
    return helper.get_score("simple.mscz", version=4)
