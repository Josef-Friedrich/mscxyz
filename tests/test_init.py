"""Test file “__init__.py”"""


from tests import helper
from tests.helper import Cli, ini_file


def test_broken_file() -> None:
    assert (
        "Error: XMLSyntaxError; message: Start tag expected, "
        "'<' not found, line 1, column 1"
        in Cli(
            "--config-file",
            ini_file,
            "meta",
            helper.get_score("broken.mscx"),
            legacy=True,
        ).sysexit()
    )
