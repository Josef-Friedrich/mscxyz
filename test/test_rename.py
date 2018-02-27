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


# class TestRename(unittest.TestCase):
#
#     def setUp(self):
#         self.simple = Rename(helper.get_tmpfile_path('simple.mscx'))
#         self.unicode = Rename(helper.get_tmpfile_path('unicode.mscx'))
#
#     def test_option_format_default(self):
#         self.simple.apply_format_string()
#         self.assertEqual(self.simple.workname, u'Title (Composer)')
#
#     def test_option_format_given(self):
#         self.simple.apply_format_string('${vbox_composer}_${vbox_title}')
#         self.assertEqual(self.simple.workname, u'Composer_Title')
#
#     def test_option_asciify(self):
#         self.unicode.apply_format_string()
#         self.unicode.asciify()
#         self.assertEqual(self.unicode.workname, 'Tuetlae (Coempoesser)')
#
#     def test_option_no_whitespace(self):
#         self.simple.apply_format_string()
#         self.simple.no_whitespace()
#         self.assertEqual(self.simple.workname, 'Title_Composer')


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = helper.get_tmpfile_path('meta-all-values.mscx')

    def test_rename(self):
        with helper.Capturing() as output:
            mscxyz.execute(['rename', self.tmp])

        target = os.path.join(os.getcwd(), 'vbox_title (vbox_composer).mscx')

        self.assertTrue(os.path.exists(target))
        os.remove(target)

        print(output)


if __name__ == '__main__':
    unittest.main()
