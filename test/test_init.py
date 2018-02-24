# -*- coding: utf-8 -*-

"""Test file “__init__.py”"""

import helper
import unittest
import mscxyz


class TestBrokenFile(unittest.TestCase):

    def test_broken_file(self):
        with helper.Capturing() as output:
            mscxyz.execute(['meta', helper.get_tmpfile_path('broken.mscx')])

        self.assertEqual(output[0], 'Error: XMLSyntaxError; message: Start '
                         'tag expected, \'<\' not found, line 1, column 1; '
                         'code: 4')


if __name__ == '__main__':
    unittest.main()
