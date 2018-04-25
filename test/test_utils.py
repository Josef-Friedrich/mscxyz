# -*- coding: utf-8 -*-

"""Test module “utils.py”."""

from mscxyz.utils import get_mscore_bin
import six
import unittest


@unittest.skip('rewritten')
class TestIsMscore(unittest.TestCase):

    def test_output(self):
        output = get_mscore_bin('which')
        self.assertTrue('which' in str(output), output)

    def test_output_type(self):
        output = get_mscore_bin('ls')
        if six.PY2:
            self.assertEqual(type(output), str)
        else:
            self.assertEqual(type(output), bytes)

    def test_existent_command(self):
        self.assertTrue(get_mscore_bin('ls'))

    def test_non_existent(self):
        self.assertFalse(get_mscore_bin('nooooooooooooooot'))


if __name__ == '__main__':
    unittest.main()
