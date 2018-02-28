# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import os
import helper
import unittest
import mscxyz


class TestLyrics(unittest.TestCase):

    def setUp(self):
        self.tmp = helper.get_tmpfile_path('lyrics.mscx')

    def assertLyricsFileExists(self, number):
        self.assertTrue(
            os.path.isfile(
                self.tmp.replace('.mscx', '_{}.mscx'.format(number))
            )
        )

    def test_without_arguments(self):
        mscxyz.execute(['lyrics', self.tmp])
        self.assertLyricsFileExists(1)
        self.assertLyricsFileExists(2)
        self.assertLyricsFileExists(3)

    def test_extract_all(self):
        mscxyz.execute(['lyrics', '--extract', 'all', self.tmp])
        self.assertLyricsFileExists(1)
        self.assertLyricsFileExists(2)
        self.assertLyricsFileExists(3)

    def test_extract_by_number(self):
        mscxyz.execute(['lyrics', '--extract', '2',  self.tmp])
        self.assertLyricsFileExists(2)


class TestLyricsFix(unittest.TestCase):

    def setUp(self):
        self.tmp = helper.get_tmpfile_path('lyrics-fix.mscx')
        mscxyz.execute(['lyrics', '--fix', self.tmp])
        self.xml_tree = mscxyz.lyrics.Lyrics(self.tmp)
        self.lyrics = self.xml_tree.lyrics

    def test_fix(self):
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


class TestLyricsRemap(unittest.TestCase):

    def test_remap(self):
        tmp = helper.get_tmpfile_path('lyrics-remap.mscx')
        mscxyz.execute(['lyrics', '--remap', '2:6', tmp])
        tree = mscxyz.lyrics.Lyrics(tmp)
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
