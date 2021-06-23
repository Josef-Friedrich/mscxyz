"""Test module “cli.py”."""

from mscxyz import cli
import helper
import mscxyz
import re
import unittest


class TestArgs(unittest.TestCase):

    def test_args_general(self):
        args = cli.parser.parse_args(['help', '.'])
        self.assertEqual(args.general_backup, False)
        self.assertEqual(args.general_colorize, False)
        self.assertEqual(args.general_dry_run, False)
        self.assertEqual(args.general_glob, '*.msc[xz]')
        self.assertEqual(args.general_mscore, False)
        self.assertEqual(args.general_verbose, 0)
        self.assertEqual(args.path, '.')

    def test_args_clean(self):
        args = cli.parser.parse_args(['clean', '.'])
        self.assertEqual(args.clean_style, None)
        self.assertEqual(args.subcommand, 'clean')

    def test_args_export(self):
        args = cli.parser.parse_args(['export', '.'])
        self.assertEqual(args.export_extension, 'pdf')
        self.assertEqual(args.subcommand, 'export')

    def test_args_help(self):
        args = cli.parser.parse_args(['help', '.'])
        self.assertEqual(args.help_markdown, False)
        self.assertEqual(args.help_rst, False)
        self.assertEqual(args.subcommand, 'help')

    def test_args_general_lyrics(self):
        args = cli.parser.parse_args(['lyrics', '.'])
        self.assertEqual(args.lyrics_extract, 'all')
        self.assertEqual(args.lyrics_fix, False)
        self.assertEqual(args.lyrics_remap, None)
        self.assertEqual(args.subcommand, 'lyrics')

    def test_args_general_meta(self):
        args = cli.parser.parse_args(['meta', '.'])
        self.assertEqual(args.meta_clean, None)
        self.assertEqual(args.meta_json, False)
        self.assertEqual(args.meta_set, None)
        self.assertEqual(args.meta_sync, False)
        self.assertEqual(args.subcommand, 'meta')

    def test_args_general_rename(self):
        args = cli.parser.parse_args(['rename', '.'])
        self.assertEqual(args.rename_alphanum, False)
        self.assertEqual(args.rename_ascii, False)
        self.assertEqual(args.rename_format,
                         '$combined_title ($combined_composer)')
        self.assertEqual(args.rename_target, None)
        self.assertEqual(args.subcommand, 'rename')


class TestCommandlineInterface(unittest.TestCase):

    def test_help_short(self):
        with self.assertRaises(SystemExit) as cm:
            with helper.Capturing():
                mscxyz.execute(['-h'])
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '0')

    def test_help_long(self):
        with self.assertRaises(SystemExit) as cm:
            with helper.Capturing():
                mscxyz.execute(['--help'])
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '0')

    def test_without_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            with helper.Capturing('stderr'):
                mscxyz.execute()
        the_exception = cm.exception
        self.assertEqual(str(the_exception), '2')

    def test_help_text(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['-h'])
        self.assertTrue('[-h]' in output[0])


class TestHelp(unittest.TestCase):

    def test_all(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['help', 'all'])
        self.assertTrue(len(output) > 150)

    def test_restructuredtext(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['help', '--rst', 'all'])
        self.assertTrue('.. code-block:: text' in output)

    def test_markdown(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['help', '--markdown', 'all'])
        self.assertTrue('```' in output)

    def test_functions_in_all(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['help', 'all'])
        self.assertTrue('%asciify{text}' in '\n'.join(output))

    def test_functions_in_rename(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['rename', '--help'])
        self.assertTrue('%asciify{text}' in '\n'.join(output))


class TestVersion(unittest.TestCase):

    def test_version(self):
        with self.assertRaises(SystemExit):
            with helper.Capturing() as output:
                mscxyz.execute(['--version'])

        result = re.search('[^ ]* [^ ]*', output[0])
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
