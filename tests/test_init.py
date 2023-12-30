"""Test file “__init__.py”"""

import unittest

import mscxyz
from tests import helper
from tests.helper import ini_file


class TestBrokenMscoreFile(unittest.TestCase):
    def test_broken_file(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "--config-file",
                    ini_file,
                    "meta",
                    helper.get_tmpfile_path("broken.mscx"),
                ]
            )
        self.assertTrue(
            "Error: XMLSyntaxError; message: Start tag expected, "
            "'<' not found, line 1, column 1" in " ".join(output)
        )


if __name__ == "__main__":
    unittest.main()
