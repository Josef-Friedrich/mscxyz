# -*- coding: utf-8 -*-

"""Test module “utils.py”."""

from mscxyz.utils import is_mscore
import six
import unittest


class TestIsMscore(unittest.TestCase):

    def test_output(self):
        output = is_mscore('which')
        self.assertTrue('which' in str(output), output)

    def test_output_type(self):
        output = is_mscore('ls')
        if six.PY2:
            self.assertEqual(type(output), str)
        else:
            self.assertEqual(type(output), bytes)

    def test_existent_command(self):
        self.assertTrue(is_mscore('ls'))

    def test_non_existent(self):
        self.assertFalse(is_mscore('nooooooooooooooot'))


if __name__ == '__main__':
    unittest.main()
