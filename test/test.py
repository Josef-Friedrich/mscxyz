# -*- coding: utf-8 -*-

"""File for various tests"""

import os
import helper
import unittest
import mscxyz
import mock


class TestFile(unittest.TestCase):
    def setUp(self):
        from mscxyz.score_file_classes import File
        self.file = File(helper.get_tmpfile_path('simple.mscx'))

    def test_file_object_initialisation(self):
        self.assertTrue(self.file.relpath)
        self.assertTrue(self.file.dirname)
        self.assertEqual(self.file.filename, 'simple.mscx')
        self.assertEqual(self.file.basename, 'simple')
        self.assertEqual(self.file.extension, 'mscx')


class TestBatch(unittest.TestCase):

    @mock.patch('mscxyz.Meta')
    def test_batch(self, Meta):
        with helper.Capturing():
            mscxyz.execute(['meta', helper.get_tmpdir_path('batch')])
        self.assertEqual(Meta.call_count, 3)


class TestBackup(unittest.TestCase):

    def setUp(self):
        self.tmp = helper.get_tmpfile_path('simple.mscx')
        self.backup = self.tmp.replace('.mscx', '_bak.mscx')
        with helper.Capturing():
            mscxyz.execute(['--backup', 'meta', self.tmp])

    def test_exists(self):
        self.assertTrue(os.path.isfile(self.backup))

    def test_size(self):
        self.assertEqual(os.path.getsize(self.tmp),
                         os.path.getsize(self.backup))


class TestExport(unittest.TestCase):

    @mock.patch('mscxyz.score_file_classes.mscore')
    def test_export(self, mscore_function):
        tmp = helper.get_tmpfile_path('simple.mscx')
        mscxyz.execute(['export', '--extension', 'mp3', tmp])
        args = mscore_function.call_args_list[0][0][0]
        self.assertEqual(args[0], '--export-to')
        self.assertEqual(args[1], tmp.replace('mscx', 'mp3'))
        self.assertEqual(args[2], tmp)


if __name__ == '__main__':
    unittest.main()
