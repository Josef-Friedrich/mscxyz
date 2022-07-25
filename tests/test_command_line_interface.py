"""Test the command line interface using subprocess."""

import subprocess
import unittest


class TestCli(unittest.TestCase):
    def test_cli(self):
        output = subprocess.check_output(("mscx-manager", "--help"))
        self.assertTrue("usage: mscx-manager" in str(output))


if __name__ == "__main__":
    unittest.main()
