"""Test file “__init__.py”"""


import pytest

from tests import helper
from tests.helper import Cli, ini_file


# @pytest.mark.skip("Will be fixed later")
def test_broken_file() -> None:
    stdout = Cli(
            helper.get_score("broken.mscx"),

        ).stdout()

    assert (
        "Error: XMLSyntaxError; message: Start tag expected, "
        "'<' not found, line 1, column 1"
        in Cli(
            helper.get_score("broken.mscx"),

        ).stdout()
    )
