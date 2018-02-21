# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import helper
import unittest


class TestRename(unittest.TestCase):
    def setUp(self):
        from mscxyz.rename import Rename
        self.simple = Rename(helper.get_tmpfile_path('simple.mscx'))
        self.unicode = Rename(helper.get_tmpfile_path('unicode.mscx'))

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


if __name__ == '__main__':
    unittest.main()
