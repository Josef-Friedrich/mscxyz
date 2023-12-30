"""Test submodule “meta.py”."""

from __future__ import annotations

import os
import tempfile
import unittest

import mscxyz
from mscxyz import meta
from mscxyz.meta import (
    Combined,
    Interface,
    InterfaceReadOnly,
    InterfaceReadWrite,
    Meta,
    MetaTag,
    Vbox,
    distribute_field,
    export_to_dict,
    to_underscore,
)
from mscxyz.score_file_classes import MscoreXmlTree
from tests import helper
from tests.helper import ini_file


class TestExceptions(unittest.TestCase):
    def test_read_only_field_error(self):
        with self.assertRaises(meta.ReadOnlyFieldError) as context:
            raise meta.ReadOnlyFieldError("lol")
        self.assertEqual(str(context.exception), "The field “lol” is read only!")

    def test_unkown_field_error(self):
        valid_fields = ("troll", "trill")
        with self.assertRaises(meta.UnkownFieldError) as context:
            raise meta.UnkownFieldError("lol", valid_fields)
        self.assertEqual(
            str(context.exception),
            "Unkown field of name “lol”! Valid field names are: " "troll, trill",
        )

    def test_unmatched_format_string_error(self):
        with self.assertRaises(meta.UnmatchedFormatStringError) as context:
            raise meta.UnmatchedFormatStringError("test", "test")
        self.assertEqual(
            str(context.exception),
            "Your format string “test” " "doesn’t match on this input string: “test”",
        )

    def test_format_string_no_field_error(self):
        with self.assertRaises(meta.FormatStringNoFieldError) as context:
            raise meta.FormatStringNoFieldError("test")
        self.assertEqual(
            str(context.exception), "No fields found in your " "format string “test”!"
        )


class TestFunctions(unittest.TestCase):
    def test_distribute_field(self):
        match = distribute_field("We are the champions - Queen", "$title - $composer")
        self.assertEqual(match, {"composer": "Queen", "title": "We are the champions"})

    def test_to_underscore(self) -> None:
        self.assertEqual(to_underscore("PascalCase"), "_pascal_case")
        self.assertEqual(to_underscore("lowerCamelCase"), "lower_camel_case")

    def test_export_to_dict(self) -> None:
        class Data:
            a = "a"
            b = "b"

        data = Data()
        self.assertEqual(export_to_dict(data, ("a")), {"a": "a"})


class TestClassUnifiedInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.fields = [
            "combined_composer",
            "combined_lyricist",
            "combined_subtitle",
            "combined_title",
            "metatag_arranger",
            "metatag_composer",
            "metatag_copyright",
            "metatag_creation_date",
            "metatag_lyricist",
            "metatag_movement_number",
            "metatag_movement_title",
            "metatag_platform",
            "metatag_poet",
            "metatag_source",
            "metatag_translator",
            "metatag_work_number",
            "metatag_work_title",
            "vbox_composer",
            "vbox_lyricist",
            "vbox_subtitle",
            "vbox_title",
        ]

    def _init_class(self, filename: str, version: int = 2):
        tmp = helper.get_file(filename, version)
        tree = MscoreXmlTree(tmp)
        interface = InterfaceReadWrite(tree.xml_root)
        return interface, tree, tmp

    def _test_subclasses(self, version: int) -> None:
        interface, _, _ = self._init_class("simple.mscx", version)
        self.assertTrue(interface.metatag)
        self.assertTrue(interface.vbox)
        self.assertTrue(interface.combined)

    def test_subclasses(self):
        self._test_subclasses(version=2)
        self._test_subclasses(version=3)

    def test_static_method_split(self) -> None:
        result = InterfaceReadWrite._split("metatag_work_title")
        self.assertEqual(result, {"field": "work_title", "object": "metatag"})
        with self.assertRaises(ValueError):
            InterfaceReadWrite._split("metatag")
        with self.assertRaises(ValueError):
            InterfaceReadWrite._split("lol_work_title")

    def _test_get_simple(self, version: int) -> None:
        interface, _, _ = self._init_class("simple.mscx", version)
        self.assertEqual(interface.vbox_title, "Title")
        self.assertEqual(interface.metatag_work_title, "Title")

    def test_get_simple(self):
        self._test_get_simple(version=2)
        self._test_get_simple(version=3)

    def _test_get_all_values(self, version: str) -> None:
        interface, _, _ = self._init_class("meta-all-values.mscx", version)

        self.assertEqual(interface.combined_composer, "vbox_composer")
        self.assertEqual(interface.combined_lyricist, "vbox_lyricist")
        self.assertEqual(interface.combined_subtitle, "vbox_subtitle")
        self.assertEqual(interface.combined_title, "vbox_title")

        for field in self.fields[4:]:
            self.assertEqual(getattr(interface, field), field)

    def test_get_all_values(self):
        self._test_get_all_values(version=2)
        self._test_get_all_values(version=3)

    def _test_set_all_values(self, version: int):
        interface, tree, tmp = self._init_class("meta-all-values.mscx", version)

        for field in self.fields:
            setattr(interface, field, field + "_test")
            self.assertEqual(getattr(interface, field), field + "_test")

        tree.save()
        tree = MscoreXmlTree(tmp)
        interface = InterfaceReadWrite(tree.xml_root)

        self.assertEqual(interface.combined_composer, "vbox_composer_test")
        self.assertEqual(interface.combined_lyricist, "vbox_lyricist_test")
        self.assertEqual(interface.combined_subtitle, "vbox_subtitle_test")
        self.assertEqual(interface.combined_title, "vbox_title_test")

        for field in self.fields[4:]:
            self.assertEqual(getattr(interface, field), field + "_test")

    def test_set_all_values(self):
        self._test_set_all_values(version=2)
        self._test_set_all_values(version=3)

    def test_method_get_all_fields(self):
        fields = InterfaceReadWrite.get_all_fields()
        self.assertEqual(fields, self.fields)

    def _test_method_export_to_dict(self, version: int):
        interface, _, _ = self._init_class("meta-all-values.mscx", version)
        result = interface.export_to_dict()
        self.assertEqual(
            result,
            {
                "combined_composer": "vbox_composer",
                "combined_lyricist": "vbox_lyricist",
                "combined_subtitle": "vbox_subtitle",
                "combined_title": "vbox_title",
                "metatag_arranger": "metatag_arranger",
                "metatag_composer": "metatag_composer",
                "metatag_copyright": "metatag_copyright",
                "metatag_creation_date": "metatag_creation_date",
                "metatag_lyricist": "metatag_lyricist",
                "metatag_movement_number": "metatag_movement_number",
                "metatag_movement_title": "metatag_movement_title",
                "metatag_platform": "metatag_platform",
                "metatag_poet": "metatag_poet",
                "metatag_source": "metatag_source",
                "metatag_translator": "metatag_translator",
                "metatag_work_number": "metatag_work_number",
                "metatag_work_title": "metatag_work_title",
                "vbox_composer": "vbox_composer",
                "vbox_lyricist": "vbox_lyricist",
                "vbox_subtitle": "vbox_subtitle",
                "vbox_title": "vbox_title",
            },
        )

    def test_method_export_to_dict(self):
        self._test_method_export_to_dict(version=2)
        self._test_method_export_to_dict(version=3)

    def _test_attribute_fields(self, version):
        interface, _, _ = self._init_class("meta-all-values.mscx", version)
        self.assertEqual(interface.fields, self.fields)

    def test_attribute_fields(self):
        self._test_attribute_fields(version=2)
        self._test_attribute_fields(version=3)


class TestClassInterfaceReadOnly(unittest.TestCase):
    def setUp(self):
        self.fields = (
            "readonly_basename",
            "readonly_dirname",
            "readonly_extension",
            "readonly_filename",
            "readonly_relpath",
            "readonly_relpath_backup",
        )
        self.tmp = helper.get_file("simple.mscx")
        self.xml_tree = MscoreXmlTree(self.tmp)
        self.interface = InterfaceReadOnly(self.xml_tree)

    def test_exception(self):
        with self.assertRaises(AttributeError):
            self.interface.readonly_relpath = "lol"

    def test_field_readonly_basename(self):
        self.assertEqual(self.interface.readonly_basename, "simple")

    def test_field_readonly_dirname(self):
        self.assertEqual(self.interface.readonly_dirname, os.path.dirname(self.tmp))

    def test_field_readonly_extension(self):
        self.assertEqual(self.interface.readonly_extension, "mscx")

    def test_field_readonly_filename(self):
        self.assertEqual(self.interface.readonly_filename, "simple.mscx")

    def test_field_readonly_relpath(self):
        self.assertEqual(self.interface.readonly_relpath, self.tmp)

    def test_field_readonly_relpath_backup(self):
        self.assertEqual(
            self.interface.readonly_relpath_backup,
            self.tmp.replace(".mscx", "_bak.mscx"),
        )


class TestClassInterface(unittest.TestCase):
    def setUp(self):
        self.fields = [
            "combined_composer",
            "combined_lyricist",
            "combined_subtitle",
            "combined_title",
            "metatag_arranger",
            "metatag_composer",
            "metatag_copyright",
            "metatag_creation_date",
            "metatag_lyricist",
            "metatag_movement_number",
            "metatag_movement_title",
            "metatag_platform",
            "metatag_poet",
            "metatag_source",
            "metatag_translator",
            "metatag_work_number",
            "metatag_work_title",
            "readonly_abspath",
            "readonly_basename",
            "readonly_dirname",
            "readonly_extension",
            "readonly_filename",
            "readonly_relpath",
            "readonly_relpath_backup",
            "vbox_composer",
            "vbox_lyricist",
            "vbox_subtitle",
            "vbox_title",
        ]

        self.tmp = helper.get_file("meta-all-values.mscx")
        self.xml_tree = MscoreXmlTree(self.tmp)
        self.interface = Interface(self.xml_tree)

    def test_static_method_get_all_fields(self):
        self.assertEqual(Interface.get_all_fields(), self.fields)

    def test_get(self):
        for field in self.fields:
            self.assertTrue(getattr(self.interface, field), field)

    def test_set(self):
        self.interface.vbox_title = "lol"
        self.assertEqual(self.interface.vbox_title, "lol")

    def test_exception(self):
        with self.assertRaises(mscxyz.meta.ReadOnlyFieldError):
            self.interface.readonly_extension = "lol"


class TestClassMetaTag(unittest.TestCase):
    def _init_class(self, filename: str, version: int = 2):
        tmp = helper.get_file(filename, version)
        tree = MscoreXmlTree(tmp)
        meta = MetaTag(tree.xml_root)
        return meta, tree, tmp

    def test_static_method_to_camel_case(self):
        camel_case = MetaTag._to_camel_case
        self.assertEqual(camel_case("work_title"), "workTitle")
        self.assertEqual(camel_case("composer"), "composer")
        self.assertEqual(camel_case("work_title_lol"), "workTitleLol")
        self.assertEqual(camel_case("workTitle"), "workTitle")

    def test_get2(self):
        meta, _, _ = self._init_class("simple.mscx", version=2)
        self.assertEqual(meta.workTitle, "Title")
        self.assertEqual(meta.work_title, "Title")
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, "Composer")

    def test_get3(self):
        meta, _, _ = self._init_class("simple.mscx", version=3)
        self.assertEqual(meta.workTitle, "Title")
        self.assertEqual(meta.work_title, "Title")
        self.assertEqual(meta.arranger, None)
        self.assertEqual(meta.composer, "Composer")

    def test_set2(self):
        meta, tree, tmp = self._init_class("simple.mscx", version=2)
        meta.workTitle = "WT"
        meta.movement_title = "MT"
        tree.save()
        tree = MscoreXmlTree(tmp)
        meta = MetaTag(tree.xml_root)
        self.assertEqual(meta.work_title, "WT")
        self.assertEqual(meta.movementTitle, "MT")
        xml_string = helper.read_file(tmp)
        self.assertTrue('<metaTag name="workTitle">WT</metaTag>' in xml_string)

    def test_set3(self):
        meta, tree, tmp = self._init_class("simple.mscx", version=3)
        meta.workTitle = "WT"
        meta.movement_title = "MT"
        tree.save()
        tree = MscoreXmlTree(tmp)
        meta = MetaTag(tree.xml_root)
        self.assertEqual(meta.work_title, "WT")
        self.assertEqual(meta.movementTitle, "MT")
        xml_string = helper.read_file(tmp)
        self.assertTrue('<metaTag name="workTitle">WT</metaTag>' in xml_string)

    def test_get_exception(self):
        meta, _, _ = self._init_class("simple.mscx")
        with self.assertRaises(mscxyz.meta.UnkownFieldError):
            meta.lol

    def test_set_exception(self):
        meta, tree, tmp = self._init_class("simple.mscx")
        with self.assertRaises(AttributeError):
            meta.lol = "lol"

    def test_clean(self):
        meta, tree, tmp = self._init_class("simple.mscx")
        meta.arranger = "A"
        self.assertEqual(meta.arranger, "A")
        meta.clean()
        self.assertEqual(meta.arranger, "")


class TestClassVbox(unittest.TestCase):
    def _init_class(self, filename: str, version: int = 2):
        tmp = helper.get_file(filename, version)
        tree = MscoreXmlTree(tmp)
        vbox = Vbox(tree.xml_root)
        return vbox, tree, tmp

    def _test_init(self, version: int):
        _, tree, tmp = self._init_class("no-vbox.mscx", version)
        tree.save()
        xml_string = helper.read_file(tmp)
        self.assertTrue("<VBox>" in xml_string)

    def test_init(self):
        self._test_init(version=2)
        self._test_init(version=3)

    def _test_get(self, version: int):
        vbox, _, _ = self._init_class("simple.mscx", version)
        self.assertEqual(vbox.Title, "Title")
        self.assertEqual(vbox.Composer, "Composer")
        self.assertEqual(vbox.Subtitle, None)
        self.assertEqual(vbox.title, "Title")
        self.assertEqual(vbox.composer, "Composer")

    def test_get(self):
        self._test_get(version=2)
        self._test_get(version=3)

    def _test_get_exception(self, version):
        vbox, _, _ = self._init_class("simple.mscx", version)
        with self.assertRaises(meta.UnkownFieldError):
            vbox.lol

    def test_get_exception(self):
        self._test_get_exception(version=2)
        self._test_get_exception(version=3)

    def _assert_set(self, filename: str, version: int = 2):
        tmp = helper.get_file(filename, version)
        tree = MscoreXmlTree(tmp)
        vbox = Vbox(tree.xml_root)
        vbox.Title = "lol"
        vbox.composer = "lol"
        tree.save()
        tree = MscoreXmlTree(tmp)
        vbox = Vbox(tree.xml_root)
        self.assertEqual(vbox.title, "lol")
        self.assertEqual(vbox.Composer, "lol")
        xml_string = helper.read_file(tmp)
        self.assertTrue("<text>lol</text>" in xml_string)

    def test_set_with_existing_vbox(self):
        self._assert_set("simple.mscx", version=2)
        self._assert_set("simple.mscx", version=3)

    def test_set_no_inital_vbox(self):
        self._assert_set("no-vbox.mscx", version=2)
        self._assert_set("no-vbox.mscx", version=3)

    def _test_set_exception(self, version: int = 2):
        vbox, _, _ = self._init_class("simple.mscx", version)
        with self.assertRaises(meta.UnkownFieldError):
            vbox.lol = "lol"

    def test_set_exception(self):
        self._test_set_exception(version=2)
        self._test_set_exception(version=3)


class TestClassCombined(unittest.TestCase):
    def _init_class(self, filename: str):
        tmp = helper.get_file(filename)
        tree = MscoreXmlTree(tmp)
        combined = Combined(tree.xml_root)
        return combined, tree, tmp

    def test_getter(self):
        combined, tree, tmp = self._init_class("simple.mscx")
        self.assertEqual(combined.title, "Title")
        self.assertEqual(combined.subtitle, None)
        self.assertEqual(combined.composer, "Composer")
        self.assertEqual(combined.lyricist, None)

    def test_setter(self):
        combined, tree, tmp = self._init_class("simple.mscx")
        combined.title = "T"
        combined.subtitle = "S"
        combined.composer = "C"
        combined.lyricist = "L"
        tree.save()
        combined = Combined(tree.xml_root)
        self.assertEqual(combined.metatag.workTitle, "T")
        self.assertEqual(combined.metatag.movementTitle, "S")
        self.assertEqual(combined.metatag.composer, "C")
        self.assertEqual(combined.metatag.lyricist, "L")

        self.assertEqual(combined.vbox.Title, "T")
        self.assertEqual(combined.vbox.Subtitle, "S")
        self.assertEqual(combined.vbox.Composer, "C")
        self.assertEqual(combined.vbox.Lyricist, "L")


class TestIntegration(unittest.TestCase):
    def test_distribute_field(self):
        tmp = helper.get_file("meta-distribute-field.mscx")
        mscxyz.execute(
            [
                "meta",
                "--distribute-field",
                "vbox_title",
                "$combined_title - $combined_composer",
                tmp,
            ]
        )
        meta = Meta(tmp)
        iface = meta.interface
        self.assertEqual(iface.vbox_composer, "Composer")
        self.assertEqual(iface.metatag_composer, "Composer")
        self.assertEqual(iface.vbox_title, "Title")
        self.assertEqual(iface.metatag_work_title, "Title")

    def test_distribute_field_multple_source_fields(self):
        tmp = helper.get_file("Title - Composer.mscx")
        mscxyz.execute(
            [
                "meta",
                "--distribute-field",
                "vbox_title,readonly_basename",
                "$combined_title - $combined_composer",
                tmp,
            ]
        )
        meta = Meta(tmp)
        iface = meta.interface
        self.assertEqual(iface.vbox_composer, "Composer")
        self.assertEqual(iface.metatag_composer, "Composer")
        self.assertEqual(iface.vbox_title, "Title")
        self.assertEqual(iface.metatag_work_title, "Title")

    def test_distribute_field_multiple_values(self):
        tmp = helper.get_file("meta-distribute-field.mscx")
        mscxyz.execute(
            [
                "meta",
                "--distribute-field",
                "vbox_title",
                "$metatag_work_title - $metatag_composer",
                "--distribute-field",
                "vbox_title",
                "$metatag_movement_title - $metatag_lyricist",
                tmp,
            ]
        )
        meta = Meta(tmp)
        iface = meta.interface
        self.assertEqual(iface.metatag_lyricist, "Composer")
        self.assertEqual(iface.metatag_composer, "Composer")
        self.assertEqual(iface.metatag_movement_title, "Title")
        self.assertEqual(iface.metatag_work_title, "Title")

    def test_distribute_field_invalid_format_string(self):
        tmp = helper.get_file("meta-distribute-field.mscx")
        with self.assertRaises(meta.FormatStringNoFieldError):
            mscxyz.execute(["meta", "--distribute-field", "vbox_title", "lol", tmp])

    def test_distribute_field_exception_unmatched(self):
        tmp = helper.get_file("simple.mscx")
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "meta",
                    "--distribute-field",
                    "vbox_title",
                    "$metatag_work_title - $metatag_composer",
                    tmp,
                ]
            )
        self.assertTrue("UnmatchedFormatStringError" in output[-1])

    def test_clean_all(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "all", tmp])
        meta = Meta(tmp)
        iface = meta.interface_read_write
        for field in iface.fields:
            self.assertEqual(getattr(iface, field), None, field)

    def test_clean_single_field(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title", tmp])
        meta = Meta(tmp)
        iface = meta.interface
        self.assertEqual(iface.vbox_title, None, "vbox_title")
        self.assertEqual(iface.vbox_composer, "vbox_composer", "vbox_composer")

    def test_clean_some_fields(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title,vbox_composer", tmp])
        meta = Meta(tmp)
        iface = meta.interface
        self.assertEqual(iface.vbox_title, None, "vbox_title")
        self.assertEqual(iface.vbox_composer, None, "vbox_composer")
        self.assertEqual(iface.vbox_subtitle, "vbox_subtitle", "vbox_subtitle")

    def test_show(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "--config-file",
                    ini_file,
                    "meta",
                    "--clean",
                    "all",
                    helper.get_file("meta-all-values.mscx"),
                ]
            )

        self.assertEqual(output[0], "")
        self.assertTrue("meta-all-values.mscx" in " ".join(output))
        self.assertEqual(output[-1], "vbox_title: “vbox_title” -> “”")

    def test_show_simple_unverbose(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "--config-file",
                    ini_file,
                    "meta",
                    "--clean",
                    "all",
                    helper.get_file("simple.mscx"),
                ]
            )
        self.assertEqual(output[0], "")
        self.assertTrue("simple.mscx" in " ".join(output))
        self.assertEqual(output[2], "combined_composer: “Composer” -> “”")
        self.assertEqual(output[3], "combined_title: “Title” -> “”")
        self.assertEqual(output[-1], "vbox_title: “Title” -> “”")

    def test_show_verbose(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "--config-file",
                    ini_file,
                    "--verbose",
                    "meta",
                    "--clean",
                    "all",
                    helper.get_file("simple.mscx"),
                ]
            )
        self.assertEqual(output[0], "")
        self.assertTrue("simple.mscx" in " ".join(output))
        self.assertEqual(output[2], "combined_composer: “Composer” -> “”")
        self.assertEqual(output[3], "combined_lyricist: ")
        self.assertEqual(output[-2], "vbox_subtitle: ")
        self.assertEqual(output[-1], "vbox_title: “Title” -> “”")

    def test_show_verbose_zero(self):
        with helper.Capturing() as output:
            mscxyz.execute(["meta", "--clean", "all", helper.get_file("simple.mscx")])
        output = " ".join(output)
        self.assertTrue("readonly_basename" in output)
        self.assertFalse("readonly_abspath" in output)
        self.assertFalse("readonly_relpath_backup" in output)

    def test_show_verbose_one(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                ["-v", "meta", "--clean", "all", helper.get_file("simple.mscx")]
            )
        output = " ".join(output)
        self.assertTrue("readonly_abspath" in output)
        self.assertFalse("readonly_relpath_backup" in output)

    def test_show_verbose_two(self):
        with helper.Capturing() as output:
            mscxyz.execute(
                [
                    "-vv",
                    "meta",
                    "--clean",
                    "all",
                    helper.get_file("simple.mscx"),
                ]
            )
        output = " ".join(output)
        self.assertTrue("readonly_relpath_backup" in output)

    def test_set_field_simple_string(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--set-field", "vbox_title", "lol", tmp])
        meta = Meta(tmp)
        self.assertEqual(meta.interface.vbox_title, "lol")

    def test_set_field_multiple_times(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(
            [
                "meta",
                "--set-field",
                "vbox_title",
                "lol",
                "--set-field",
                "vbox_composer",
                "troll",
                tmp,
            ]
        )
        meta = Meta(tmp)
        self.assertEqual(meta.interface.vbox_title, "lol")
        self.assertEqual(meta.interface.vbox_composer, "troll")

    def test_set_field_with_templating(self):
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(
            ["meta", "--set-field", "vbox_title", "$vbox_title ($vbox_composer)", tmp]
        )
        meta = Meta(tmp)
        self.assertEqual(meta.interface.vbox_title, "vbox_title (vbox_composer)")

    def test_delete_duplicates(self):
        tmp = helper.get_file("meta-duplicates.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        meta = Meta(tmp)
        self.assertFalse(meta.interface.combined_lyricist)
        self.assertFalse(meta.interface.combined_subtitle)

    def test_delete_duplicates_move_subtitle(self):
        tmp = helper.get_file("meta-duplicates-move-subtitle.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        meta = Meta(tmp)
        self.assertFalse(meta.interface.combined_lyricist)
        self.assertFalse(meta.interface.combined_subtitle)
        self.assertEqual(meta.interface.combined_title, "Title")

    def test_log(self):
        tmp = helper.get_file("simple.mscx")
        log = tempfile.mktemp()
        mscxyz.execute(
            ["meta", "--log", log, "$combined_title-$combined_composer", tmp]
        )
        log_file = open(log, "r")
        self.assertEqual(log_file.readline(), "Title-Composer\n")


if __name__ == "__main__":
    unittest.main()
