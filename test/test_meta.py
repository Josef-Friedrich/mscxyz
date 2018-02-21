# -*- coding: utf-8 -*-

"""Test module “meta.py”."""


import unittest
import mscxyz
from mscxyz.meta import MetaTag
from mscxyz.meta import Meta
from mscxyz.tree import Tree
import helper


class TestClassMeta(unittest.TestCase):

    def setUp(self):
        self.meta = Meta(helper.get_file('simple.mscx'))

    def test_get(self):
        self.assertEqual(self.meta.get('title'), 'Title')
        self.assertEqual(self.meta.get('composer'), 'Composer')

    def test_show(self):
        with helper.Capturing() as output:
            mscxyz.execute(['meta', '-s', helper.get_file('simple.mscx')])

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


class TestClassMetaTag(unittest.TestCase):

    def test_get(self):
        tree = Tree(helper.get_file('simple.mscx'))
        meta = MetaTag(tree.root)
        self.assertEqual(meta.workTitle, 'Title')
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, 'Composer')

    def test_set(self):
        tmp = helper.tmp_file('simple.mscx')
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        meta.workTitle = 'lol'
        tree.write()
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        self.assertEqual(meta.workTitle, 'lol')


if __name__ == '__main__':
    unittest.main()
