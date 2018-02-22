# -*- coding: utf-8 -*-

"""Test module “meta.py”."""


import unittest
import mscxyz
from mscxyz.meta import MetaTag, Meta, Vbox, Combined
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

    def _init_class(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        return meta, tree, tmp

    def test_get(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        self.assertEqual(meta.workTitle, 'Title')
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, 'Composer')

    def test_set(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        meta.workTitle = 'lol'
        tree.save()
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        self.assertEqual(meta.workTitle, 'lol')
        xml_string = helper.read_file(tmp)
        self.assertTrue('<metaTag name="workTitle">lol</metaTag>' in
                        xml_string)

    def test_get_exception(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        with self.assertRaises(AttributeError):
            meta.lol

    def test_set_exception(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        with self.assertRaises(AttributeError):
            meta.lol = 'lol'

    def test_clean(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        meta.arranger = 'A'
        self.assertEqual(meta.arranger, 'A')
        meta.clean()
        self.assertEqual(meta.arranger, '')


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


class TestClassCombined(unittest.TestCase):

    def _init_class(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        combined = Combined(tree.root)
        return combined, tree, tmp

    def test_getter(self):
        combined, tree, tmp = self._init_class('simple.mscx')
        self.assertEqual(combined.title, 'Title')
        self.assertEqual(combined.subtitle, None)
        self.assertEqual(combined.composer, 'Composer')
        self.assertEqual(combined.lyricist, None)

    def test_setter(self):
        combined, tree, tmp = self._init_class('simple.mscx')
        combined.title = 'T'
        combined.subtitle = 'S'
        combined.composer = 'C'
        combined.lyricist = 'L'
        tree.save()
        combined = Combined(tree.root)
        self.assertEqual(combined.metatag.workTitle, 'T')
        self.assertEqual(combined.metatag.movementTitle, 'S')
        self.assertEqual(combined.metatag.composer, 'C')
        self.assertEqual(combined.metatag.lyricist, 'L')

        self.assertEqual(combined.vbox.Title, 'T')
        self.assertEqual(combined.vbox.Subtitle, 'S')
        self.assertEqual(combined.vbox.Composer, 'C')
        self.assertEqual(combined.vbox.Lyricist, 'L')


if __name__ == '__main__':
    unittest.main()
