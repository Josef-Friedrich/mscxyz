# -*- coding: utf-8 -*-

"""Test module “meta.py”."""


import unittest
import mscxyz
from mscxyz.meta import MetaTag, Meta, Vbox, Combined, distribute_field, \
                        UnifedInterface
from mscxyz.tree import Tree
import helper


class TestFunctionDistributeField(unittest.TestCase):

    def test_simple(self):
        match = distribute_field('We are the champions - Queen',
                                 '$title - $composer')
        self.assertEqual(match, {'composer': 'Queen', 'title':
                         'We are the champions'})


class TestClassUnifiedInterface(unittest.TestCase):

    def _init_class(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        interface = UnifedInterface(tree.root)
        return interface, tree, tmp

    def test_subclasses(self):
        interface, tree, tmp = self._init_class('simple.mscx')
        self.assertTrue(interface.metatag)
        self.assertTrue(interface.vbox)
        self.assertTrue(interface.combined)

    def test_static_method_split(self):
        result = UnifedInterface._split('metatag_work_title')
        self.assertEqual(result, {'field': 'work_title', 'object': 'metatag'})
        with self.assertRaises(ValueError):
            UnifedInterface._split('metatag')

    def test_get_simple(self):
        interface, tree, tmp = self._init_class('simple.mscx')
        self.assertEqual(interface.vbox_title, 'Title')
        self.assertEqual(interface.metatag_work_title, 'Title')

    def test_get_all_values(self):
        interface, tree, tmp = self._init_class('meta-all-values.mscx')

        def _assert(field):
            self.assertEqual(getattr(interface, field), field)

        _assert('metatag_arranger')
        _assert('metatag_composer')
        _assert('metatag_copyright')
        _assert('metatag_creation_date')
        _assert('metatag_lyricist')
        _assert('metatag_movement_number')
        _assert('metatag_movement_title')
        _assert('metatag_platform')
        _assert('metatag_poet')
        _assert('metatag_source')
        _assert('metatag_translator')
        _assert('metatag_work_number')
        _assert('metatag_work_title')

    def test_set_all_values(self):
        interface, tree, tmp = self._init_class('meta-all-values.mscx')

        def _set(field):
            setattr(interface, field, field + '_test')
            self.assertEqual(getattr(interface, field), field + '_test')

        def _assert(field):
            self.assertEqual(getattr(interface, field), field + '_test')

        _set('metatag_arranger')
        _set('metatag_composer')
        _set('metatag_copyright')
        _set('metatag_creation_date')
        _set('metatag_lyricist')
        _set('metatag_movement_number')
        _set('metatag_movement_title')
        _set('metatag_platform')
        _set('metatag_poet')
        _set('metatag_source')
        _set('metatag_translator')
        _set('metatag_work_number')
        _set('metatag_work_title')

        _assert('metatag_arranger')
        _assert('metatag_composer')
        _assert('metatag_copyright')
        _assert('metatag_creation_date')
        _assert('metatag_lyricist')
        _assert('metatag_movement_number')
        _assert('metatag_movement_title')
        _assert('metatag_platform')
        _assert('metatag_poet')
        _assert('metatag_source')
        _assert('metatag_translator')
        _assert('metatag_work_number')
        _assert('metatag_work_title')

    def test_method_get_all_fields(self):
        fields = UnifedInterface.get_all_fields()
        self.assertEqual(fields, [
                'combined_composer',
                'combined_lyricist',
                'combined_subtitle',
                'combined_title',
                'metatag_arranger',
                'metatag_composer',
                'metatag_copyright',
                'metatag_creation_date',
                'metatag_lyricist',
                'metatag_movement_number',
                'metatag_movement_title',
                'metatag_platform',
                'metatag_poet',
                'metatag_source',
                'metatag_translator',
                'metatag_work_number',
                'metatag_work_title',
                'vbox_composer',
                'vbox_lyricist',
                'vbox_subtitle',
                'vbox_title',
            ]
        )


class TestClassMeta(unittest.TestCase):

    def setUp(self):
        self.meta = Meta(helper.get_tmpfile_path('simple.mscx'))

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

    def test_static_method_to_camel_case(self):
        camel_case = MetaTag._to_camel_case
        self.assertEqual(camel_case('work_title'), 'workTitle')
        self.assertEqual(camel_case('composer'), 'composer')
        self.assertEqual(camel_case('work_title_lol'), 'workTitleLol')
        self.assertEqual(camel_case('workTitle'), 'workTitle')

    def test_get(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        self.assertEqual(meta.workTitle, 'Title')
        self.assertEqual(meta.work_title, 'Title')
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, 'Composer')

    def test_set(self):
        meta, tree, tmp = self._init_class('simple.mscx')
        meta.workTitle = 'WT'
        meta.movement_title = 'MT'
        tree.save()
        tree = Tree(tmp)
        meta = MetaTag(tree.root)
        self.assertEqual(meta.work_title, 'WT')
        self.assertEqual(meta.movementTitle, 'MT')
        xml_string = helper.read_file(tmp)
        self.assertTrue('<metaTag name="workTitle">WT</metaTag>' in
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
        self.assertEqual(vbox.title, 'Title')
        self.assertEqual(vbox.composer, 'Composer')

    def test_get_exception(self):
        vbox, tree, tmp = self._init_class('simple.mscx')
        with self.assertRaises(AttributeError):
            vbox.lol

    def _assert_set(self, filename):
        tmp = helper.get_tmpfile_path(filename)
        tree = Tree(tmp)
        vbox = Vbox(tree.root)
        vbox.Title = 'lol'
        vbox.composer = 'lol'
        tree.save()
        tree = Tree(tmp)
        vbox = Vbox(tree.root)
        self.assertEqual(vbox.title, 'lol')
        self.assertEqual(vbox.Composer, 'lol')
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


class TestIntegration(unittest.TestCase):

    def test_distribute_field(self):
        tmp = helper.get_tmpfile_path('meta-distribute-field.mscx')
        mscxyz.execute(
            ['meta', '--distribute-field', 'vbox_title',
             '$combined_title - $combined_composer', tmp]
        )

        meta = Meta(tmp)
        iface = meta.interface

        self.assertEqual(iface.vbox_composer, 'Composer')
        self.assertEqual(iface.metatag_composer, 'Composer')
        self.assertEqual(iface.vbox_title, 'Title')
        self.assertEqual(iface.metatag_work_title, 'Title')


if __name__ == '__main__':
    unittest.main()
