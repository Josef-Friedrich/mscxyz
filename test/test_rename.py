# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import helper
import unittest
from mscxyz import rename
import mscxyz
import os


class TestFunctions(unittest.TestCase):

    def test_function_prepare_fields(self):
        fields = {
            'field1': ' Subtitle ',
            'field2': 'Title / Composer',
        }
        result = rename.prepare_fields(fields)
        self.assertEqual(result, {
            'field1': 'Subtitle',
            'field2': 'Title - Composer',
        })

    def test_function_asciify(self):
        self.assertEqual(rename.asciify('äöü'), u'aeoeue')
        self.assertEqual(rename.asciify('ß'), u'ss')
        self.assertEqual(rename.asciify('Чайко́вский'), 'Chaikovskii')

    def test_function_replace_to_dash(self):
        self.assertEqual(rename.replace_to_dash('abc', 'a', 'b', 'c'), '---')

    def test_function_delete_characters(self):
        self.assertEqual(rename.delete_characters('abc', 'a', 'b', 'c'), '')

    def test_function_clean_up(self):
        clean = rename.clean_up
        self.assertEqual(clean('-abc-'), 'abc')
        self.assertEqual(clean('a-b-c'), 'a-b-c')
        self.assertEqual(clean('a--b'), 'a_b')
        self.assertEqual(clean('a---b'), 'a_b')
        self.assertEqual(clean('a__b'), 'a_b')
        self.assertEqual(clean('a___b'), 'a_b')

    def test_function_apply_format_string(self):
        from mscxyz import settings
        settings.args = settings.DefaultArguments()
        meta = mscxyz.meta.Meta(
            helper.get_tmpfile_path('meta-all-values.mscx'))
        fields = meta.interface.export_to_dict()
        name = rename.apply_format_string(fields)
        self.assertEqual(name, 'vbox_title (vbox_composer)')

    def test_function_format_filename(self):
        from mscxyz import settings
        settings.args = settings.DefaultArguments()
        settings.args.rename_ascii = True
        settings.args.rename_no_whitespace = True

        f = rename.format_filename
        self.assertEqual(f('  Löl   '), 'Loel')
        self.assertEqual(f('folder/file'), 'folder/file')


class TestIntegration(unittest.TestCase):

    @staticmethod
    def _get(filename):
        return helper.get_tmpfile_path(filename)

    @staticmethod
    def _target_path_cwd(filename):
        return os.path.join(os.getcwd(), filename)

    @staticmethod
    def _execute(args):
        with helper.Capturing() as output:
            mscxyz.execute(args)
        return output

    def test_simple(self):
        output = self._execute(['rename', self._get('simple.mscx')])
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('simple.mscx -> ' in output[0])
        self.assertTrue('Title (Composer).mscx' in output[0])
        os.remove(target)

    def test_without_arguments(self):
        output = self._execute(['rename', self._get('meta-all-values.mscx')])
        target = self._target_path_cwd('vbox_title (vbox_composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('vbox_title (vbox_composer).mscx' in output[0])
        os.remove(target)

    def test_format(self):
        output = self._execute(['rename', '--format',
                                '${vbox_composer}_${vbox_title}',
                                self._get('simple.mscx')])
        target = self._target_path_cwd('Composer_Title.mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Composer_Title.mscx' in output[0])
        os.remove(target)

    def test_no_whitespace(self):
        output = self._execute(['rename', '--no-whitespace',
                                self._get('simple.mscx')])
        target = self._target_path_cwd('Title_Composer.mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Title_Composer.mscx' in output[0])
        os.remove(target)

    def test_unicode(self):
        output = self._execute(['rename', '--ascii',
                                self._get('unicode.mscx')])
        target = self._target_path_cwd('Tuetlae (Coempoesser).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Tuetlae (Coempoesser).mscx' in output[0])
        os.remove(target)


if __name__ == '__main__':
    unittest.main()
