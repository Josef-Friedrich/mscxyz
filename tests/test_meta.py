"""Test submodule “meta.py”."""

from __future__ import annotations

import os
import tempfile

import pytest

import mscxyz
import mscxyz.meta
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
from mscxyz.score import Score
from tests import helper
from tests.helper import ini_file


class TestExceptions:
    def test_read_only_field_error(self):
        with pytest.raises(meta.ReadOnlyFieldError) as e:
            raise meta.ReadOnlyFieldError("lol")
        assert e.value.args[0] == "The field “lol” is read only!"

    def test_unkown_field_error(self):
        valid_fields = ("troll", "trill")
        with pytest.raises(meta.UnkownFieldError) as e:
            raise meta.UnkownFieldError("lol", valid_fields)
        assert (
            e.value.args[0] == "Unkown field of name “lol”! Valid field names are: "
            "troll, trill"
        )

    def test_unmatched_format_string_error(self):
        with pytest.raises(meta.UnmatchedFormatStringError) as e:
            raise meta.UnmatchedFormatStringError("test", "test")
        assert (
            e.value.args[0] == "Your format string “test” "
            "doesn’t match on this input string: “test”"
        )

    def test_format_string_no_field_error(self):
        with pytest.raises(meta.FormatStringNoFieldError) as e:
            raise meta.FormatStringNoFieldError("test")
        assert e.value.args[0] == "No fields found in your " "format string “test”!"


class TestFunctions:
    def test_distribute_field(self):
        assert distribute_field(
            "We are the champions - Queen", "$title - $composer"
        ) == {"composer": "Queen", "title": "We are the champions"}

    def test_to_underscore(self) -> None:
        assert to_underscore("PascalCase") == "_pascal_case"
        assert to_underscore("lowerCamelCase") == "lower_camel_case"

    def test_export_to_dict(self) -> None:
        class Data:
            a = "a"
            b = "b"

        data = Data()
        assert export_to_dict(data, ("a")) == {"a": "a"}


class TestClassUnifiedInterface:
    def setup_method(self) -> None:
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
        tree = Score(tmp)
        interface = InterfaceReadWrite(tree.xml_root)
        return interface, tree, tmp

    def _test_subclasses(self, version: int) -> None:
        interface, _, _ = self._init_class("simple.mscx", version)
        assert interface.metatag
        assert interface.vbox
        assert interface.combined

    def test_subclasses(self):
        self._test_subclasses(version=2)
        self._test_subclasses(version=3)

    def test_static_method_split(self) -> None:
        result = InterfaceReadWrite._split("metatag_work_title")
        assert result == {"field": "work_title", "object": "metatag"}
        with pytest.raises(ValueError):
            InterfaceReadWrite._split("metatag")
        with pytest.raises(ValueError):
            InterfaceReadWrite._split("lol_work_title")

    def _test_get_simple(self, version: int) -> None:
        interface, _, _ = self._init_class("simple.mscx", version)
        assert interface.vbox_title == "Title"
        assert interface.metatag_work_title == "Title"

    def test_get_simple(self) -> None:
        self._test_get_simple(version=2)
        self._test_get_simple(version=3)

    def _test_get_all_values(self, version: int) -> None:
        interface, _, _ = self._init_class("meta-all-values.mscx", version)

        assert interface.combined_composer == "vbox_composer"
        assert interface.combined_lyricist == "vbox_lyricist"
        assert interface.combined_subtitle == "vbox_subtitle"
        assert interface.combined_title == "vbox_title"

        for field in self.fields[4:]:
            assert getattr(interface, field) == field

    def test_get_all_values(self):
        self._test_get_all_values(version=2)
        self._test_get_all_values(version=3)

    def _test_set_all_values(self, version: int):
        interface, tree, tmp = self._init_class("meta-all-values.mscx", version)

        for field in self.fields:
            setattr(interface, field, field + "_test")
            assert getattr(interface, field) == field + "_test"

        tree.save()
        tree = Score(tmp)
        interface = InterfaceReadWrite(tree.xml_root)

        assert interface.combined_composer == "vbox_composer_test"
        assert interface.combined_lyricist == "vbox_lyricist_test"
        assert interface.combined_subtitle == "vbox_subtitle_test"
        assert interface.combined_title == "vbox_title_test"

        for field in self.fields[4:]:
            assert getattr(interface, field) == field + "_test"

    def test_set_all_values(self):
        self._test_set_all_values(version=2)
        self._test_set_all_values(version=3)

    def test_method_get_all_fields(self):
        fields = InterfaceReadWrite.get_all_fields()
        assert fields == self.fields

    def _test_method_export_to_dict(self, version: int):
        interface, _, _ = self._init_class("meta-all-values.mscx", version)
        result = interface.export_to_dict()
        assert result == {
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
        }

    def test_method_export_to_dict(self) -> None:
        self._test_method_export_to_dict(version=2)
        self._test_method_export_to_dict(version=3)

    def _test_attribute_fields(self, version: int) -> None:
        interface, _, _ = self._init_class("meta-all-values.mscx", version)
        assert interface.fields == self.fields

    def test_attribute_fields(self) -> None:
        self._test_attribute_fields(version=2)
        self._test_attribute_fields(version=3)


class TestClassInterfaceReadOnly:
    def setup_method(self):
        self.fields = (
            "readonly_basename",
            "readonly_dirname",
            "readonly_extension",
            "readonly_filename",
            "readonly_relpath",
            "readonly_relpath_backup",
        )
        self.tmp = helper.get_file("simple.mscx")
        self.xml_tree = Score(self.tmp)
        self.interface = InterfaceReadOnly(self.xml_tree)

    def test_exception(self):
        with pytest.raises(AttributeError):
            self.interface.readonly_relpath = "lol"

    def test_field_readonly_basename(self):
        assert self.interface.readonly_basename == "simple"

    def test_field_readonly_dirname(self):
        assert self.interface.readonly_dirname == os.path.dirname(self.tmp)

    def test_field_readonly_extension(self):
        assert self.interface.readonly_extension == "mscx"

    def test_field_readonly_filename(self):
        assert self.interface.readonly_filename == "simple.mscx"

    def test_field_readonly_relpath(self):
        assert self.interface.readonly_relpath == self.tmp

    def test_field_readonly_relpath_backup(self):
        assert self.interface.readonly_relpath_backup == self.tmp.replace(
            ".mscx", "_bak.mscx"
        )


class TestClassInterface:
    def setup_method(self):
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
        self.xml_tree = Score(self.tmp)
        self.interface = Interface(self.xml_tree)

    def test_static_method_get_all_fields(self):
        assert Interface.get_all_fields() == self.fields

    def test_get(self):
        for field in self.fields:
            assert getattr(self.interface, field), field

    def test_set(self):
        self.interface.vbox_title = "lol"
        assert self.interface.vbox_title == "lol"

    def test_exception(self):
        with pytest.raises(mscxyz.meta.ReadOnlyFieldError):
            self.interface.readonly_extension = "lol"


class TestClassMetaTag:
    def _init_class(self, filename: str, version: int = 2):
        tmp = helper.get_file(filename, version)
        tree = Score(tmp)
        meta = MetaTag(tree.xml_root)
        return meta, tree, tmp

    def test_static_method_to_camel_case(self) -> None:
        camel_case = MetaTag._to_camel_case
        assert camel_case("work_title") == "workTitle"
        assert camel_case("composer") == "composer"
        assert camel_case("work_title_lol") == "workTitleLol"
        assert camel_case("workTitle") == "workTitle"

    def test_get2(self) -> None:
        meta, _, _ = self._init_class("simple.mscx", version=2)
        assert meta.workTitle == "Title"
        assert meta.work_title == "Title"
        assert meta.arranger is None
        assert meta.composer == "Composer"

    def test_get3(self) -> None:
        meta, _, _ = self._init_class("simple.mscx", version=3)
        assert meta.workTitle == "Title"
        assert meta.work_title == "Title"
        assert meta.arranger is None
        assert meta.composer == "Composer"

    def test_set2(self) -> None:
        meta, tree, tmp = self._init_class("simple.mscx", version=2)
        meta.workTitle = "WT"
        meta.movement_title = "MT"
        tree.save()
        tree = Score(tmp)
        meta = MetaTag(tree.xml_root)
        assert meta.work_title == "WT"
        assert meta.movementTitle == "MT"
        xml_string = helper.read_file(tmp)
        assert '<metaTag name="workTitle">WT</metaTag>' in xml_string

    def test_set3(self) -> None:
        meta, tree, tmp = self._init_class("simple.mscx", version=3)
        meta.workTitle = "WT"
        meta.movement_title = "MT"
        tree.save()
        tree = Score(tmp)
        meta = MetaTag(tree.xml_root)
        assert meta.work_title == "WT"
        assert meta.movementTitle == "MT"
        xml_string = helper.read_file(tmp)
        assert '<metaTag name="workTitle">WT</metaTag>' in xml_string

    def test_get_exception(self):
        meta, _, _ = self._init_class("simple.mscx")
        with pytest.raises(mscxyz.meta.UnkownFieldError):
            meta.lol

    def test_set_exception(self):
        meta, _, _ = self._init_class("simple.mscx")
        with pytest.raises(AttributeError):
            meta.lol = "lol"

    def test_clean(self) -> None:
        meta, _, _ = self._init_class("simple.mscx")
        meta.arranger = "A"
        assert meta.arranger == "A"
        meta.clean()
        assert meta.arranger == ""


class TestClassVbox:
    def _init_class(
        self, filename: str, version: int = 2
    ) -> tuple[Vbox, Score, str]:
        tmp = helper.get_file(filename, version)
        tree = Score(tmp)
        vbox = Vbox(tree.xml_root)
        return vbox, tree, tmp

    def _test_init(self, version: int) -> None:
        _, tree, tmp = self._init_class("no-vbox.mscx", version)
        tree.save()
        xml_string = helper.read_file(tmp)
        assert "<VBox>" in xml_string

    def test_init(self) -> None:
        self._test_init(version=2)
        self._test_init(version=3)

    def _test_get(self, version: int) -> None:
        vbox, _, _ = self._init_class("simple.mscx", version)
        assert vbox.Title == "Title"
        assert vbox.Composer == "Composer"
        assert vbox.Subtitle is None
        assert vbox.title == "Title"
        assert vbox.composer == "Composer"

    def test_get(self) -> None:
        self._test_get(version=2)
        self._test_get(version=3)

    def _test_get_exception(self, version: int) -> None:
        vbox, _, _ = self._init_class("simple.mscx", version)
        with pytest.raises(meta.UnkownFieldError):
            vbox.lol

    def test_get_exception(self) -> None:
        self._test_get_exception(version=2)
        self._test_get_exception(version=3)

    def _assert_set(self, filename: str, version: int = 2) -> None:
        tmp = helper.get_file(filename, version)
        tree = Score(tmp)
        vbox = Vbox(tree.xml_root)
        vbox.Title = "lol"
        vbox.composer = "lol"
        tree.save()
        tree = Score(tmp)
        vbox = Vbox(tree.xml_root)
        assert vbox.title == "lol"
        assert vbox.Composer == "lol"
        xml_string = helper.read_file(tmp)
        assert "<text>lol</text>" in xml_string

    def test_set_with_existing_vbox(self) -> None:
        self._assert_set("simple.mscx", version=2)
        self._assert_set("simple.mscx", version=3)

    def test_set_no_inital_vbox(self) -> None:
        self._assert_set("no-vbox.mscx", version=2)
        self._assert_set("no-vbox.mscx", version=3)

    def _test_set_exception(self, version: int = 2) -> None:
        vbox, _, _ = self._init_class("simple.mscx", version)
        with pytest.raises(meta.UnkownFieldError):
            vbox.lol = "lol"

    def test_set_exception(self) -> None:
        self._test_set_exception(version=2)
        self._test_set_exception(version=3)


class TestClassCombined:
    def _init_class(self, filename: str) -> tuple[Combined, Score, str]:
        tmp = helper.get_file(filename)
        tree = Score(tmp)
        combined = Combined(tree.xml_root)
        return combined, tree, tmp

    def test_getter(self) -> None:
        combined, _, _ = self._init_class("simple.mscx")
        assert combined.title == "Title"
        assert combined.subtitle is None
        assert combined.composer == "Composer"
        assert combined.lyricist is None

    def test_setter(self):
        combined, tree, _ = self._init_class("simple.mscx")
        combined.title = "T"
        combined.subtitle = "S"
        combined.composer = "C"
        combined.lyricist = "L"
        tree.save()
        combined = Combined(tree.xml_root)
        assert combined.metatag.workTitle == "T"
        assert combined.metatag.movementTitle == "S"
        assert combined.metatag.composer == "C"
        assert combined.metatag.lyricist == "L"

        assert combined.vbox.Title == "T"
        assert combined.vbox.Subtitle == "S"
        assert combined.vbox.Composer == "C"
        assert combined.vbox.Lyricist == "L"


class TestIntegration:
    def test_distribute_field(self) -> None:
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
        assert iface.vbox_composer == "Composer"
        assert iface.metatag_composer == "Composer"
        assert iface.vbox_title == "Title"
        assert iface.metatag_work_title == "Title"

    def test_distribute_field_multple_source_fields(self) -> None:
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
        assert iface.vbox_composer == "Composer"
        assert iface.metatag_composer == "Composer"
        assert iface.vbox_title == "Title"
        assert iface.metatag_work_title == "Title"

    def test_distribute_field_multiple_values(self) -> None:
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
        assert iface.metatag_lyricist == "Composer"
        assert iface.metatag_composer == "Composer"
        assert iface.metatag_movement_title == "Title"
        assert iface.metatag_work_title == "Title"

    def test_distribute_field_invalid_format_string(self) -> None:
        tmp = helper.get_file("meta-distribute-field.mscx")
        with pytest.raises(meta.FormatStringNoFieldError):
            mscxyz.execute(["meta", "--distribute-field", "vbox_title", "lol", tmp])

    def test_distribute_field_exception_unmatched(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mscxyz.execute(
            [
                "meta",
                "--distribute-field",
                "vbox_title",
                "$metatag_work_title - $metatag_composer",
                helper.get_file("simple.mscx"),
            ]
        )
        capture = capsys.readouterr()
        assert "UnmatchedFormatStringError" in capture.out

    def test_clean_all(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "all", tmp])
        meta = Meta(tmp)
        iface = meta.interface_read_write
        for field in iface.fields:
            assert getattr(iface, field) is None, field

    def test_clean_single_field(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title", tmp])
        meta = Meta(tmp)
        iface = meta.interface
        assert iface.vbox_title is None, "vbox_title"
        assert iface.vbox_composer == "vbox_composer", "vbox_composer"

    def test_clean_some_fields(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title,vbox_composer", tmp])
        meta = Meta(tmp)
        iface = meta.interface
        assert iface.vbox_title is None, "vbox_title"
        assert iface.vbox_composer is None, "vbox_composer"
        assert iface.vbox_subtitle == "vbox_subtitle", "vbox_subtitle"

    def test_show(self, capsys: pytest.CaptureFixture[str]) -> None:
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

        capture = capsys.readouterr()
        lines = capture.out.splitlines()
        assert lines[0] == ""
        assert "meta-all-values.mscx" in capture.out
        assert lines[-1] == "vbox_title: “vbox_title” -> “”"

    def test_show_simple_unverbose(self, capsys: pytest.CaptureFixture[str]) -> None:
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
        capture = capsys.readouterr()
        lines = capture.out.splitlines()
        assert lines[0] == ""
        assert "simple.mscx" in capture.out
        assert lines[2] == "combined_composer: “Composer” -> “”"
        assert lines[3] == "combined_title: “Title” -> “”"
        assert lines[-1] == "vbox_title: “Title” -> “”"

    def test_show_verbose(self, capsys: pytest.CaptureFixture[str]) -> None:
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
        capture = capsys.readouterr()
        lines = capture.out.splitlines()
        assert lines[0] == ""
        assert "simple.mscx" in capture.out
        assert lines[2] == "combined_composer: “Composer” -> “”"
        assert lines[3] == "combined_lyricist: "
        assert lines[-2] == "vbox_subtitle: "
        assert lines[-1] == "vbox_title: “Title” -> “”"

    def test_show_verbose_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        mscxyz.execute(["meta", "--clean", "all", helper.get_file("simple.mscx")])
        capture = capsys.readouterr()
        assert "readonly_basename" in capture.out
        assert "readonly_abspath" not in capture.out
        assert "readonly_relpath_backup" not in capture.out

    def test_show_verbose_one(self, capsys: pytest.CaptureFixture[str]) -> None:
        mscxyz.execute(["-v", "meta", "--clean", "all", helper.get_file("simple.mscx")])
        capture = capsys.readouterr()
        assert "readonly_abspath" in capture.out
        assert "readonly_relpath_backup" not in capture.out

    def test_show_verbose_two(self, capsys: pytest.CaptureFixture[str]) -> None:
        mscxyz.execute(
            [
                "-vv",
                "meta",
                "--clean",
                "all",
                helper.get_file("simple.mscx"),
            ]
        )
        capture = capsys.readouterr()
        assert "readonly_relpath_backup" in capture.out

    def test_set_field_simple_string(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--set-field", "vbox_title", "lol", tmp])
        meta = Meta(tmp)
        assert meta.interface.vbox_title == "lol"

    def test_set_field_multiple_times(self) -> None:
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
        assert meta.interface.vbox_title == "lol"
        assert meta.interface.vbox_composer == "troll"

    def test_set_field_with_templating(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(
            ["meta", "--set-field", "vbox_title", "$vbox_title ($vbox_composer)", tmp]
        )
        meta = Meta(tmp)
        assert meta.interface.vbox_title == "vbox_title (vbox_composer)"

    def test_delete_duplicates(self) -> None:
        tmp = helper.get_file("meta-duplicates.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        meta = Meta(tmp)
        assert not meta.interface.combined_lyricist
        assert not meta.interface.combined_subtitle

    def test_delete_duplicates_move_subtitle(self) -> None:
        tmp = helper.get_file("meta-duplicates-move-subtitle.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        meta = Meta(tmp)
        assert not meta.interface.combined_lyricist
        assert not meta.interface.combined_subtitle
        assert meta.interface.combined_title == "Title"

    def test_log(self) -> None:
        tmp = helper.get_file("simple.mscx")
        log = tempfile.mktemp()
        mscxyz.execute(
            ["meta", "--log", log, "$combined_title-$combined_composer", tmp]
        )
        log_file = open(log, "r")
        assert log_file.readline() == "Title-Composer\n"
