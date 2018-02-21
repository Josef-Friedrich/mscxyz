# -*- coding: utf-8 -*-

"""Test module “clean.py”."""

import helper
import unittest
import mscxyz


class TestClean(unittest.TestCase):

    def setUp(self):
        clean = mscxyz.execute(['clean',
                                helper.get_tmpfile_path('formats.mscx')])[0]
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
                helper.get_tmpfile_path('style.mss'),
                helper.get_tmpfile_path('simple.mscx')
            ])[0]
        self.style = helper.read_file(self.score.fullpath)

    def test_style(self):
        self.assertTrue(
            '<staffUpperBorder>77</staffUpperBorder>'
            in self.style
        )
