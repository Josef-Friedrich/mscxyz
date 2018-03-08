# -*- coding: utf-8 -*-

"""Test module “clean.py”."""

import helper
import mscxyz
import unittest


class TestClean(unittest.TestCase):

    def test_clean(self):
        tmp = helper.get_tmpfile_path('formats.mscx')
        mscxyz.execute(['clean', tmp])
        cleaned = helper.read_file(tmp)
        self.assertFalse('<font' in cleaned)
        self.assertFalse('<b>' in cleaned)
        self.assertFalse('<i>' in cleaned)
        self.assertFalse('<pos' in cleaned)
        self.assertFalse('<LayoutBreak>' in cleaned)
        self.assertFalse('<StemDirection>' in cleaned)

    def test_clean_add_style(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        mscxyz.execute(['clean', '--style',
                        helper.get_tmpfile_path('style.mss'), tmp])
        style = helper.read_file(tmp)
        self.assertTrue('<staffUpperBorder>77</staffUpperBorder>' in style)
