"""File for various tests"""


import os
import re
import helper
import unittest
import mscxyz
from mscxyz.utils import is_mscore
import sys
import six


if sys.prefix == '/usr':
    mscore = True
else:
    mscore = False


class TestMeta(unittest.TestCase):
    def setUp(self):
        from mscxyz.meta import Meta
        self.meta = Meta(helper.get_file('simple'))

    def test_get(self):
        self.assertEqual(self.meta.get('title'), 'Title')
        self.assertEqual(self.meta.get('composer'), 'Composer')

    def test_show(self):
        with helper.Capturing() as output:
            mscxyz.execute(['meta', '-s', helper.get_file('simple')])

        compare = [
            '',
            '\x1b[31msimple.mscx\x1b[0m',
            '\x1b[34mfilename\x1b[0m: simple',
            '\x1b[33mworkTitle\x1b[0m: Title',
            '\x1b[33mplatform\x1b[0m: Linux',
            '\x1b[33mcomposer\x1b[0m: Composer',
            '\x1b[32mComposer\x1b[0m: Composer',
            '\x1b[32mTitle\x1b[0m: Title'
        ]

        self.assertTrue('\x1b[33mworkTitle\x1b[0m: Title' in output)
        self.assertEqual(output.sort(), compare.sort())


class TestFile(unittest.TestCase):
    def setUp(self):
        from mscxyz.fileloader import File
        self.file = File(helper.get_file('simple'))

    def test_file_object_initialisation(self):
        self.assertEqual(self.file.fullpath, helper.get_file('simple'))
        self.assertEqual(self.file.dirname,
                         os.path.dirname(helper.get_file('simple')))
        self.assertEqual(self.file.filename, 'simple.mscx')
        self.assertEqual(self.file.basename, 'simple')
        self.assertEqual(self.file.extension, 'mscx')


class TestRename(unittest.TestCase):
    def setUp(self):
        from mscxyz.rename import Rename
        self.simple = Rename(helper.get_file('simple'))
        self.unicode = Rename(helper.get_file('unicode'))

    def test_option_format_default(self):
        self.simple.apply_format_string()
        self.assertEqual(self.simple.workname, u'Title (Composer)')

    def test_option_format_given(self):
        self.simple.apply_format_string('${composer}_${title}')
        self.assertEqual(self.simple.workname, u'Composer_Title')

    def test_option_asciify(self):
        self.unicode.apply_format_string()
        self.unicode.asciify()
        self.assertEqual(self.unicode.workname, 'Tuetlae (Coempoesser)')

    def test_option_no_whitespace(self):
        self.simple.apply_format_string()
        self.simple.no_whitespace()
        self.assertEqual(self.simple.workname, 'Title_Composer')


class TestClean(unittest.TestCase):

    def setUp(self):
        clean = mscxyz.execute(['clean', helper.tmp_file('formats.mscx')])[0]
        self.clean_file = helper.read_file(clean.fullpath)

    def test_font(self):
        self.assertFalse('<font' in self.clean_file)

    def test_b(self):
        self.assertFalse('<b>' in self.clean_file)

    def test_i(self):
        self.assertFalse('<i>' in self.clean_file)

    def test_pos(self):
        self.assertFalse('<pos' in self.clean_file)

    def test_layout_break(self):
        self.assertFalse('<LayoutBreak>' in self.clean_file)

    def test_stem_direction(self):
        self.assertFalse('<StemDirection>' in self.clean_file)


class TestCleanAddStyle(unittest.TestCase):

    def setUp(self):
        self.score = mscxyz.execute(
            [
                'clean',
                '--style',
                helper.tmp_file('style.mss'),
                helper.tmp_file('simple.mscx')
            ])[0]
        self.style = helper.read_file(self.score.fullpath)

    def test_style(self):
        self.assertTrue(
            '<staffUpperBorder>77</staffUpperBorder>'
            in self.style
        )


class TestLyrics(unittest.TestCase):

    def setUp(self):
        self.file = 'lyrics.mscx'
        self.lyrics = mscxyz.execute(['lyrics', helper.tmp_file(self.file)])[0]

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
            ['lyrics', '--extract', 'all', helper.tmp_file(self.file)])[0]

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
            ['lyrics', '--extract', '2', helper.tmp_file(self.file)])[0]

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
            helper.tmp_file('lyrics-fix.mscx')
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
            helper.tmp_file('lyrics-remap.mscx')
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


class TestBatch(unittest.TestCase):
    def setUp(self):
        with helper.Capturing():
            self.batch = mscxyz.execute(['meta', '-s',
                                        helper.tmp_dir('batch')])

    def test_batch(self):
        self.assertEqual(len(self.batch), 3)


class TestBackup(unittest.TestCase):
    def setUp(self):
        with helper.Capturing():
            self.score = mscxyz.execute(
                ['-b', 'meta', '-s', helper.tmp_file('simple.mscx')])[0]
            self.fullpath = self.score.fullpath
            self.fullpath_backup = self.score.fullpath_backup

    def test_path_not_empty(self):
        self.assertTrue(os.path.isfile(self.fullpath_backup))

    def test_path_attribute(self):
        if six.PY2:
            self.assertRegexpMatches(self.fullpath_backup, '_bak')
        else:
            self.assertRegex(self.fullpath_backup, '_bak')

    def test_size(self):
        self.assertEqual(
            os.path.getsize(self.fullpath_backup),
            os.path.getsize(self.fullpath_backup))


class TestExport(unittest.TestCase):
    def export(self, extension):
        score = mscxyz.execute(['export', '--extension', extension,
                               helper.tmp_file('simple.mscx')])[0]
        export = score.fullpath.replace('mscx', extension)
        self.assertTrue(os.path.isfile(export))

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_pdf(self):
        score = mscxyz.execute(['export', helper.tmp_file('simple.mscx')])[0]
        self.assertTrue(os.path.isfile(score.fullpath.replace('mscx', 'pdf')))

    @unittest.skipIf(not mscore, 'export not working in travis')
    def test_png(self):
        score = mscxyz.execute(
            ['export', '--extension', 'png', helper.tmp_file('simple.mscx')]
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


class TestUtils(unittest.TestCase):

    def test_is_mscore(self):
        output = is_mscore('ls')
        if six.PY2:
            self.assertEqual(type(output), str)
        else:
            self.assertEqual(type(output), bytes)
        self.assertTrue(is_mscore('ls'))
        self.assertFalse(is_mscore('nooooooooooooooot'))


class TestVersion(unittest.TestCase):

    def test_version(self):
        with self.assertRaises(SystemExit):
            if six.PY2:
                with helper.Capturing('err') as output:
                    mscxyz.execute(['--version'])
            else:
                with helper.Capturing() as output:
                    mscxyz.execute(['--version'])

        result = re.search('[^ ]* [^ ]*', output[0])
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
