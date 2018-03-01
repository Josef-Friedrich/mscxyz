# -*- coding: utf-8 -*-

"""Test the command line interface using subprocess."""

import unittest
import subprocess


class TestCli(unittest.TestCase):

    def test_cli(self):
        output = subprocess.check_output(('mscx-manager', '--help'))
        self.assertTrue('usage: mscx-manager' in str(output))


if __name__ == '__main__':
    unittest.main()
