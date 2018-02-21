# -*- coding: utf-8 -*-

"""Test module “meta.py”."""


import unittest
import mscxyz
from mscxyz.meta import MetaTag, Meta, Vbox
from mscxyz.tree import Tree
import helper


class TestClassMeta(unittest.TestCase):

    def setUp(self):
        self.meta = Meta(helper.get_tmpfile_path('simple.mscx'))

    def test_get(self):
        self.assertEqual(self.meta.get('title'), 'Title')
        self.assertEqual(self.meta.get('composer'), 'Composer')

    def test_show(self):
        with helper.Capturing() as output:
            mscxyz.execute(['meta', '-s',
                           helper.get_tmpfile_path('simple.mscx')])

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
        tree = Tree(helper.get_tmpfile_path('simple.mscx'))
        meta = MetaTag(tree.root)
        self.assertEqual(meta.workTitle, 'Title')
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, 'Composer')

    def test_set(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        meta.workTitle = 'lol'
        tree.save()
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        self.assertEqual(meta.workTitle, 'lol')
        xml_string = helper.read_file(tmp)
        self.assertTrue('<metaTag name="workTitle">lol</metaTag>' in
                        xml_string)

    def test_get_exception(self):
        tree = Tree(helper.get_tmpfile_path('simple.mscx'))
        meta_tag = MetaTag(tree.root)
        with self.assertRaises(AttributeError):
            meta_tag.lol

    def test_set_exception(self):
        tree = Tree(helper.get_tmpfile_path('simple.mscx'))
        meta_tag = MetaTag(tree.root)
        with self.assertRaises(AttributeError):
            meta_tag.lol = 'lol'


class TestClassVbox(unittest.TestCase):

    def _init_class(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        vbox = Vbox(tree.root)
        return vbox, tree, tmp

    def test_init(self):
        vbox, tree, tmp = self._init_class('no-vbox.mscx')
        tree.save()
        xml_string = helper.read_file(tmp)
        self.assertTrue('<VBox>' in xml_string)

    def test_get(self):
        vbox, tree, tmp = self._init_class('simple.mscx')
        self.assertEqual(vbox.Title, 'Title')
        self.assertEqual(vbox.Composer, 'Composer')
        self.assertEqual(vbox.Subtitle, None)

    def test_get_exception(self):
        vbox, tree, tmp = self._init_class('simple.mscx')
        with self.assertRaises(AttributeError):
            vbox.lol

    def _assert_set(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        vbox = Vbox(tree.root)
        vbox.Title = 'lol'
        tree.save()
        tree = Tree(tmp)
        vbox = Vbox(tree.root)
        self.assertEqual(vbox.Title, 'lol')
        xml_string = helper.read_file(tmp)
        self.assertTrue('<text>lol</text>' in xml_string)

    def test_set_with_existing_vbox(self):
        self._assert_set('simple.mscx')

    def test_set_no_inital_vbox(self):
        self._assert_set('no-vbox.mscx')

    def test_set_exception(self):
        vbox, tree, tmp = self._init_class('simple.mscx')
        with self.assertRaises(AttributeError):
            vbox.lol = 'lol'


if __name__ == '__main__':
    unittest.main()
