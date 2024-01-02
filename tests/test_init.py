"""Test file “__init__.py”"""


from pytest import CaptureFixture

import mscxyz
from tests import helper
from tests.helper import ini_file


def test_broken_file(capsys: CaptureFixture[str]) -> None:
    mscxyz.execute(
        [
            "--config-file",
            ini_file,
            "meta",
            helper.get_file("broken.mscx"),
        ]
    )
    capture = capsys.readouterr()
    assert (
        "Error: XMLSyntaxError; message: Start tag expected, "
        "'<' not found, line 1, column 1" in capture.out
    )
