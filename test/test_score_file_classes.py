# -*- coding: utf-8 -*-

"""ScoreFile for various tests"""

from mscxyz.score_file_classes import ScoreFile
import helper
import mock
import mscxyz
import unittest


class TestBatch(unittest.TestCase):

    @mock.patch('mscxyz.Meta')
    def test_batch(self, Meta):
        with helper.Capturing():
            mscxyz.execute(['meta', helper.get_tmpdir_path('batch')])
        self.assertEqual(Meta.call_count, 3)


class TestScoreFile(unittest.TestCase):
    def setUp(self):
        self.file = ScoreFile(helper.get_tmpfile_path('simple.mscx'))

    def test_file_object_initialisation(self):
        self.assertTrue(self.file.relpath)
        self.assertTrue(self.file.dirname)
        self.assertEqual(self.file.filename, 'simple.mscx')
        self.assertEqual(self.file.basename, 'simple')
        self.assertEqual(self.file.extension, 'mscx')


if __name__ == '__main__':
    unittest.main()
