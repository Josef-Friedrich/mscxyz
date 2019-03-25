"""Test file “__init__.py”"""

import helper
import mscxyz
import unittest


class TestBrokenScoreFile(unittest.TestCase):

    def test_broken_file(self):
        with helper.Capturing() as output:
            mscxyz.execute(['meta', helper.get_tmpfile_path('broken.mscx')])

        self.assertTrue('Error: XMLSyntaxError; message: Start tag expected, '
                        '\'<\' not found, line 1, column 1' in
                        ' '.join(output))


if __name__ == '__main__':
    unittest.main()
