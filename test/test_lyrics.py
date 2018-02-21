# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import os
import helper
import unittest
import mscxyz
import sys


if sys.prefix == '/usr':
    mscore = True
else:
    mscore = False


class TestLyrics(unittest.TestCase):

    def setUp(self):
        self.file = 'lyrics.mscx'
        self.lyrics = mscxyz.execute(['lyrics',
                                     helper.get_tmpfile_path(self.file)])[0]

    def test_files_exist(self):
        tmpdir = os.path.dirname(self.lyrics.fullpath)

        def check(number):
            lyrics_file = os.path.join(
                tmpdir,
                self.file.replace('.mscx', '_' + str(number) + '.mscx'))
            self.assertTrue(os.path.isfile(lyrics_file))

        check(1)
        check(2)
        check(3)


class TestLyricsExtractAll(unittest.TestCase):

    def setUp(self):
        self.file = 'lyrics.mscx'
        self.lyrics = mscxyz.execute(
            ['lyrics', '--extract', 'all',
             helper.get_tmpfile_path(self.file)])[0]

    def tmpFile(self, number):
        return os.path.join(
            os.path.dirname(self.lyrics.fullpath),
            self.file.replace('.mscx', '_' + str(number) + '.mscx')
        )

    def isFile(self, number):
        return os.path.isfile(self.tmpFile(number))

    def test_1(self):
        self.assertTrue(self.isFile(1))

    def test_2(self):
        self.assertTrue(self.isFile(2))

    def test_3(self):
        self.assertTrue(self.isFile(3))


class TestLyricsExtractByNumber(unittest.TestCase):

    def setUp(self):
        self.file = 'lyrics.mscx'
        self.lyrics = mscxyz.execute(
            ['lyrics', '--extract', '2',
             helper.get_tmpfile_path(self.file)])[0]

    def tmpFile(self, number):
        return os.path.join(
            os.path.dirname(self.lyrics.fullpath),
            self.file.replace('.mscx', '_' + str(number) + '.mscx')
        )

    def isFile(self, number):
        return os.path.isfile(self.tmpFile(number))

    def test_1(self):
        self.assertFalse(self.isFile(1))

    def test_2(self):
        self.assertTrue(self.isFile(2))

    def test_3(self):
        self.assertFalse(self.isFile(3))


class TestLyricsFix(unittest.TestCase):

    def setUp(self):
        tmp = mscxyz.execute([
            'lyrics',
            '--fix',
            helper.get_tmpfile_path('lyrics-fix.mscx')
        ])[0]
        self.tree = mscxyz.lyrics.Lyrics(tmp.fullpath)
        self.lyrics = self.tree.lyrics

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

    def setUp(self):
        self.score = mscxyz.execute([
            'lyrics',
            '--remap',
            '2:6',
            helper.get_tmpfile_path('lyrics-remap.mscx')
        ])[0]
        self.tree = mscxyz.lyrics.Lyrics(self.score.fullpath)
        self.lyrics = self.tree.lyrics

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_remap(self):
        text = []
        for element in self.lyrics:
            tag = element['element']
            tag_text = tag.find('text')
            text.append(tag_text.text)

        self.assertEqual(text, ['1', '3', '4', '5', '2'])


if __name__ == '__main__':
    unittest.main()
