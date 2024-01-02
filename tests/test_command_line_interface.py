"""Test the command line interface using subprocess."""

import subprocess
import unittest


class TestCli:
    def test_cli(self):
        output = subprocess.check_output(("mscx-manager", "--help"))
        assert "usage: mscx-manager" in str(output)


if __name__ == "__main__":
    unittest.main()
