"""Test file “__init__.py”"""

import helper
from helper import ini_file
import mscxyz
import unittest


class TestBrokenScoreFile(unittest.TestCase):

    def test_broken_file(self):
        with helper.Capturing() as output:
            mscxyz.execute(['--config-file', ini_file, 'meta',
                            helper.get_tmpfile_path('broken.mscx')])

        print(output)

        self.assertTrue('Error: XMLSyntaxError; message: Start tag expected, '
                        '\'<\' not found, line 1, column 1' in
                        ' '.join(output))


if __name__ == '__main__':
    unittest.main()
