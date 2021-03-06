"""Test submodule “lyrics.py”."""


import helper
import mscxyz
import os
import unittest


class TestMscoreLyricsInterface(unittest.TestCase):

    def setUp(self):
        self.score_path = helper.get_tmpfile_path('lyrics.mscx')

    def assertLyricsFileExists(self, number):
        self.assertTrue(
            os.path.isfile(
                self.score_path.replace('.mscx', '_{}.mscx'.format(number))
            )
        )

    def _test_without_arguments(self, version=2):
        self.score_path = helper.get_tmpfile_path('lyrics.mscx', version)
        mscxyz.execute(['lyrics', self.score_path])
        self.assertLyricsFileExists(1)
        self.assertLyricsFileExists(2)
        self.assertLyricsFileExists(3)

    def test_without_arguments(self):
        self._test_without_arguments(version=2)
        self._test_without_arguments(version=3)

    def _test_extract_all(self, version=2):
        self.score_path = helper.get_tmpfile_path('lyrics.mscx', version)
        mscxyz.execute(['lyrics', '--extract', 'all', self.score_path])
        self.assertLyricsFileExists(1)
        self.assertLyricsFileExists(2)
        self.assertLyricsFileExists(3)

    def test_extract_all(self):
        self._test_extract_all(version=2)
        self._test_extract_all(version=3)

    def _test_extract_by_number(self, version=2):
        self.score_path = helper.get_tmpfile_path('lyrics.mscx', version)
        mscxyz.execute(['lyrics', '--extract', '2',  self.score_path])
        self.assertLyricsFileExists(2)

    def test_extract_by_number(self):
        self._test_extract_by_number(version=2)
        self._test_extract_by_number(version=3)


class TestMscoreLyricsInterfaceFix(unittest.TestCase):

    def _test_fix(self, version=2):
        score_path = helper.get_tmpfile_path('lyrics-fix.mscx', version)
        mscxyz.execute(['lyrics', '--fix', score_path])
        self.xml_tree = mscxyz.lyrics.MscoreLyricsInterface(score_path)
        self.lyrics = self.xml_tree.lyrics

        text = []
        syllabic = []
        for element in self.lyrics:
            tag = element['element']
            tag_text = tag.find('text')
            text.append(tag_text.text)
            tag_syllabic = tag.find('syllabic')
            if hasattr(tag_syllabic, 'text'):
                syllabic.append(tag_syllabic.text)

        self.assertEqual(text,
                         ['Al', u'K\xf6pf', 'le', 'chen', 'mei', 'un', 'ne',
                          'ters', 'En', 'Was', 'te', 'si', 'lein.', 'lein.'])
        self.assertEqual(syllabic, ['begin', 'begin', 'end', 'end', 'begin',
                                    'begin', 'end', 'end', 'begin', 'begin',
                                    'middle', 'middle', 'end', 'end'])

    def test_fix(self):
        self._test_fix(version=2)
        self._test_fix(version=3)


class TestMscoreLyricsInterfaceRemap(unittest.TestCase):

    def test_remap(self):
        score_path = helper.get_tmpfile_path('lyrics-remap.mscx')
        mscxyz.execute(['lyrics', '--remap', '2:6', score_path])
        tree = mscxyz.lyrics.MscoreLyricsInterface(score_path)
        text = []
        for element in tree.lyrics:
            tag = element['element']
            tag_text = tag.find('no')
            if hasattr(tag_text, 'text'):
                no = tag_text.text
            else:
                no = '0'
            text.append(no)

        self.assertEqual(text, ['0', '5', '2', '3', '4'])


if __name__ == '__main__':
    unittest.main()
