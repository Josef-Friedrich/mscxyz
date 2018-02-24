# -*- coding: utf-8 -*-

"""File for various tests"""

import os
import helper
import unittest
import mscxyz
import sys

if sys.prefix == '/usr':
    mscore = True
else:
    mscore = False


class TestFile(unittest.TestCase):
    def setUp(self):
        from mscxyz.fileloader import File
        self.file = File(helper.get_tmpfile_path('simple.mscx'))

    def test_file_object_initialisation(self):
        self.assertTrue(self.file.fullpath)
        self.assertTrue(self.file.dirname)
        self.assertEqual(self.file.filename, 'simple.mscx')
        self.assertEqual(self.file.basename, 'simple')
        self.assertEqual(self.file.extension, 'mscx')


class TestBatch(unittest.TestCase):
    def setUp(self):
        with helper.Capturing():
            self.batch = mscxyz.execute(['meta', '-s',
                                        helper.get_tmpdir_path('batch')])

    def test_batch(self):
        self.assertEqual(len(self.batch), 3)


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

    def export(self, extension):
        score = mscxyz.execute(['export', '--extension', extension,
                               helper.get_tmpfile_path('simple.mscx')])[0]
        export = score.fullpath.replace('mscx', extension)
        self.assertTrue(os.path.isfile(export))

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_pdf(self):
        score = mscxyz.execute(['export',
                               helper.get_tmpfile_path('simple.mscx')])[0]
        self.assertTrue(os.path.isfile(score.fullpath.replace('mscx', 'pdf')))

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_png(self):
        score = mscxyz.execute(
            ['export', '--extension', 'png',
             helper.get_tmpfile_path('simple.mscx')]
        )[0]
        self.assertTrue(
            os.path.isfile(score.fullpath.replace('.mscx', '-1.png')))

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_svg(self):
        self.export('svg')

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_xml(self):
        self.export('xml')

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_mxl(self):
        self.export('mxl')

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_mid(self):
        self.export('mid')


if __name__ == '__main__':
    unittest.main()
