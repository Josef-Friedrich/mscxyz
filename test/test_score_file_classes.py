# -*- coding: utf-8 -*-

"""ScoreFile for various tests"""

from mscxyz.score_file_classes import ScoreFile, list_scores, \
                                      list_zero_alphabet
import helper
import mock
import mscxyz
import unittest


class TestFunctions(unittest.TestCase):

    @staticmethod
    def _list_scores(path, extension='both', glob=None):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('/a', ('bar',), ('lorem.mscx',)),
                ('/a/b', (), ('impsum.mscz', 'dolor.mscx', 'sit.txt')),
            ]
            return list_scores(path, extension, glob)

    @mock.patch('mscxyz.Meta')
    def test_batch(self, Meta):
        with helper.Capturing():
            mscxyz.execute(['meta', helper.get_tmpdir_path('batch')])
        self.assertEqual(Meta.call_count, 3)

    def test_without_extension(self):
        result = self._list_scores('/test')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/b/impsum.mscz',
                                  '/a/lorem.mscx'])

    def test_extension_both(self):
        result = self._list_scores('/test', extension='both')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/b/impsum.mscz',
                                  '/a/lorem.mscx'])

    def test_extension_mscx(self):
        result = self._list_scores('/test', extension='mscx')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/lorem.mscx'])

    def test_extension_mscz(self):
        result = self._list_scores('/test', extension='mscz')
        self.assertEqual(result, ['/a/b/impsum.mscz'])

    def test_raises_exception(self):
        with self.assertRaises(ValueError):
            self._list_scores('/test', extension='lol')

    def test_isfile(self):
        with mock.patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores('/a/b/lorem.mscx')
            self.assertEqual(result, ['/a/b/lorem.mscx'])

    def test_isfile_no_match(self):
        with mock.patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores('/a/b/lorem.lol')
            self.assertEqual(result, [])

    def test_arg_glob_txt(self):
        result = self._list_scores('/test', glob='*.txt')
        self.assertEqual(result, ['/a/b/sit.txt'])

    def test_arg_glob_lol(self):
        result = self._list_scores('/test', glob='*.lol')
        self.assertEqual(result, [])

    def test_function_list_zero_alphabet(self):
        result = list_zero_alphabet()
        self.assertEqual(result[0], '0')
        self.assertEqual(result[26], 'z')


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
