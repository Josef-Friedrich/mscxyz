# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import helper
import unittest
from mscxyz.rename import Rename
from mscxyz import rename


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


class TestRename(unittest.TestCase):

    def setUp(self):
        self.simple = Rename(helper.get_tmpfile_path('simple.mscx'))
        self.unicode = Rename(helper.get_tmpfile_path('unicode.mscx'))

    def test_option_format_default(self):
        self.simple.apply_format_string()
        self.assertEqual(self.simple.workname, u'Title (Composer)')

    def test_option_format_given(self):
        self.simple.apply_format_string('${vbox_composer}_${vbox_title}')
        self.assertEqual(self.simple.workname, u'Composer_Title')

    def test_option_asciify(self):
        self.unicode.apply_format_string()
        self.unicode.asciify()
        self.assertEqual(self.unicode.workname, 'Tuetlae (Coempoesser)')

    def test_option_no_whitespace(self):
        self.simple.apply_format_string()
        self.simple.no_whitespace()
        self.assertEqual(self.simple.workname, 'Title_Composer')


if __name__ == '__main__':
    unittest.main()
