"""File for various tests"""

import os
import unittest
import mscxyz
import sys
import shutil
import tempfile
from distutils.dir_util import copy_tree
import six
if six.PY2:
    from cStringIO import StringIO
else:
    from io import StringIO


def tmp_file(file_token):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files',
        file_token + '.mscx')
    tmp_dir = tempfile.mkdtemp()
    tmp = os.path.join(tmp_dir, file_token + '.mscx')
    shutil.copyfile(orig, tmp)
    return tmp


def tmp_dir(relative_dir):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files', relative_dir)
    tmp = tempfile.mkdtemp()
    copy_tree(orig, tmp)
    return tmp


class Capturing(list):
    def __init__(self, channel='out'):
        self.channel = channel

    def __enter__(self):
        if self.channel == 'out':
            self._pipe = sys.stdout
            sys.stdout = self._stringio = StringIO()
        elif self.channel == 'err':
            self._pipe = sys.stderr
            sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        if self.channel == 'out':
            sys.stdout = self._pipe
        elif self.channel == 'err':
            sys.stderr = self._pipe


def get_testfile(filename):
    return os.path.join(os.path.dirname(__file__), 'files', filename + '.mscx')


class TestMeta(unittest.TestCase):
    def setUp(self):
        from mscxyz.meta import Meta
        self.meta = Meta(get_testfile('simple'))

    def test_get(self):
        self.assertEqual(self.meta.get('title'), 'Title')
        self.assertEqual(self.meta.get('composer'), 'Composer')

    def test_show(self):
        with Capturing() as output:
            mscxyz.execute(['meta', '-s', get_testfile('simple')])

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

        self.assertEqual(output, compare)

class TestFile(unittest.TestCase):
    def setUp(self):
        from mscxyz.fileloader import File
        self.file = File(get_testfile('simple'))

    def test_file_object_initialisation(self):
        self.assertEqual(self.file.fullpath, get_testfile('simple'))
        self.assertEqual(self.file.dirname,
                         os.path.dirname(get_testfile('simple')))
        self.assertEqual(self.file.filename, 'simple.mscx')
        self.assertEqual(self.file.basename, 'simple')
        self.assertEqual(self.file.extension, 'mscx')


class TestCommandlineInterface(unittest.TestCase):
    def test_help_short(self):
        with self.assertRaises(SystemExit) as cm:
            with Capturing() as output:
                mscxyz.execute(['-h'])
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '0')

    def test_help_long(self):
        with self.assertRaises(SystemExit) as cm:
            with Capturing() as output:
                mscxyz.execute(['--help'])
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '0')

    def test_without_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            with Capturing('err') as output:
                mscxyz.execute()
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '2')

    def test_help_text(self):
        with self.assertRaises(SystemExit) as cm:
            with Capturing() as output:
                mscxyz.execute(['-h'])
        self.assertEqual(
            output[0],
            'usage: test.py [-h] [-b] [-g GLOB] [-p PICK] \
[-c CYCLE_LENGTH] [-v]')


class TestRename(unittest.TestCase):
    def setUp(self):
        from mscxyz.rename import Rename
        self.simple = Rename(get_testfile('simple'))
        self.unicode = Rename(get_testfile('unicode'))

    def test_option_format_default(self):
        self.simple.applyFormatString()
        self.assertEqual(self.simple.workname, u'Title (Composer)')

    def test_option_format_given(self):
        self.simple.applyFormatString('${composer}_${title}')
        self.assertEqual(self.simple.workname, u'Composer_Title')

    def test_option_asciify(self):
        self.unicode.applyFormatString()
        self.unicode.asciify()
        self.assertEqual(self.unicode.workname, 'Tuetlae (Coempoesser)')

    def test_option_no_whitespace(self):
        self.simple.applyFormatString()
        self.simple.noWhitespace()
        self.assertEqual(self.simple.workname, 'Title_Composer')


class TestClean(unittest.TestCase):
    def setUp(self):
        clean = mscxyz.execute(['clean', tmp_file('formats')])[0]
        tmp = open(clean.fullpath)
        self.clean_file = tmp.read()
        tmp.close()

    def test_font(self):
        if '<font' in self.clean_file:
            self.fail('Found font>')

    def test_b(self):
        if '<b>' in self.clean_file:
            self.fail('Found <b>')

    def test_i(self):
        if '<i>' in self.clean_file:
            self.fail('Found <i>')

    def test_pos(self):
        if '<pos' in self.clean_file:
            self.fail('Found <pos>')

    def test_layout_break(self):
        if '<LayoutBreak>' in self.clean_file:
            self.fail('Found <LayoutBreak>')

    def test_stem_direction(self):
        if '<StemDirection>' in self.clean_file:
            self.fail('Found <StemDirection>')


class TestLyrics(unittest.TestCase):
    def setUp(self):
        self.token = 'lyrics'
        self.lyrics = mscxyz.execute(['lyrics', tmp_file(self.token)])[0]

    def test_files_exist(self):
        tmpdir = os.path.dirname(self.lyrics.fullpath)

        def check(number):
            lyrics_file = os.path.join(
                tmpdir, self.token + '_' + str(number) + '.mscx')
            if not os.path.isfile(lyrics_file):
                self.fail(lyrics_file)

        check(1)
        check(2)
        check(3)


class TestLyricsExtractByNumber(unittest.TestCase):
    def setUp(self):
        self.token = 'lyrics'
        self.lyrics = mscxyz.execute(
            ['lyrics', '--number', '2', tmp_file(self.token)])[0]

    def test_files_exist(self):
        tmpdir = os.path.dirname(self.lyrics.fullpath)

        def tmpfile(number):
            return os.path.join(tmpdir,
                                self.token + '_' + str(number) + '.mscx')

        if os.path.isfile(tmpfile(1)):
            self.fail(tmpfile(1))

        if not os.path.isfile(tmpfile(2)):
            self.fail(tmpfile(2))

        if os.path.isfile(tmpfile(3)):
            self.fail(tmpfile(3))


class TestLyricsFix(unittest.TestCase):
    def setUp(self):
        tmp = mscxyz.execute(['lyrics', '--fix', tmp_file('lyrics-fix')])[0]
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


class TestBatch(unittest.TestCase):
    def setUp(self):
        with Capturing() as output:
            self.batch = mscxyz.execute(['meta', '-s', tmp_dir('batch')])

    def test_batch(self):
        self.assertEqual(len(self.batch), 3)


class TestBackup(unittest.TestCase):
    def setUp(self):
        with Capturing() as output:
            self.score = mscxyz.execute(
                ['-b', 'meta', '-s', tmp_file('simple')])[0]
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
        score = mscxyz.execute(
            ['export', '--extension', extension, tmp_file('simple')])[0]
        export = score.fullpath.replace('mscx', extension)
        self.assertTrue(os.path.isfile(export))

    @unittest.skip('export not working in travis')
    def test_pdf(self):
        score = mscxyz.execute(['export', tmp_file('simple')])[0]
        self.assertTrue(os.path.isfile(score.fullpath.replace('mscx', 'pdf')))

    @unittest.skip('export not working in travis')
    def test_png(self):
        score = mscxyz.execute(
            ['export', '--extension', 'png', tmp_file('simple')])[0]
        self.assertTrue(
            os.path.isfile(score.fullpath.replace('.mscx', '-1.png')))

    @unittest.skip('export not working in travis')
    def test_svg(self):
        self.export('svg')

    @unittest.skip('export not working in travis')
    def test_xml(self):
        self.export('xml')

    @unittest.skip('export not working in travis')
    def test_mxl(self):
        self.export('mxl')

    @unittest.skip('export not working in travis')
    def test_mid(self):
        self.export('mid')


if __name__ == '__main__':
    unittest.main()
