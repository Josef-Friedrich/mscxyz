"""Test submodule “meta.py”."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

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


def reload(src: Score | str | Path) -> Interface:
    return helper.reload(src).meta.interface


class TestExceptions:
    def test_read_only_field_error(self) -> None:
        with pytest.raises(meta.ReadOnlyFieldError) as e:
            raise meta.ReadOnlyFieldError("lol")
        assert e.value.args[0] == "The field “lol” is read only!"

    def test_unkown_field_error(self) -> None:
        valid_fields = ("troll", "trill")
        with pytest.raises(meta.UnkownFieldError) as e:
            raise meta.UnkownFieldError("lol", valid_fields)
        assert (
            e.value.args[0] == "Unkown field of name “lol”! Valid field names are: "
            "troll, trill"
        )

    def test_unmatched_format_string_error(self) -> None:
        with pytest.raises(meta.UnmatchedFormatStringError) as e:
            raise meta.UnmatchedFormatStringError("test", "test")
        assert (
            e.value.args[0] == "Your format string “test” "
            "doesn’t match on this input string: “test”"
        )

    def test_format_string_no_field_error(self) -> None:
        with pytest.raises(meta.FormatStringNoFieldError) as e:
            raise meta.FormatStringNoFieldError("test")
        assert e.value.args[0] == "No fields found in your " "format string “test”!"


class TestFunctions:
    def test_distribute_field(self) -> None:
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

    def _init_class(
        self, filename: str, version: int = 2
    ) -> tuple[InterfaceReadWrite, Score, str]:
        tmp = helper.get_file(filename, version)
        score = Score(tmp)
        interface = InterfaceReadWrite(score)
        return interface, score, tmp

    def _test_subclasses(self, version: int) -> None:
        interface, _, _ = self._init_class("simple.mscx", version)
        assert interface.metatag
        assert interface.vbox
        assert interface.combined

    def test_subclasses(self) -> None:
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

    def test_get_all_values(self) -> None:
        self._test_get_all_values(version=2)
        self._test_get_all_values(version=3)

    def _test_set_all_values(self, version: int) -> None:
        interface, score, tmp = self._init_class("meta-all-values.mscx", version)

        for field in self.fields:
            setattr(interface, field, field + "_test")
            assert getattr(interface, field) == field + "_test"

        score.save()
        score = Score(tmp)
        interface = InterfaceReadWrite(score)

        assert interface.combined_composer == "vbox_composer_test"
        assert interface.combined_lyricist == "vbox_lyricist_test"
        assert interface.combined_subtitle == "vbox_subtitle_test"
        assert interface.combined_title == "vbox_title_test"

        for field in self.fields[4:]:
            assert getattr(interface, field) == field + "_test"

    def test_set_all_values(self) -> None:
        self._test_set_all_values(version=2)
        self._test_set_all_values(version=3)

    def test_method_get_all_fields(self) -> None:
        fields = InterfaceReadWrite.get_all_fields()
        assert fields == self.fields

    def _test_method_export_to_dict(self, version: int) -> None:
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
    def setup_method(self) -> None:
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

    def test_exception(self) -> None:
        with pytest.raises(AttributeError):
            self.interface.readonly_relpath = "lol"  # type: ignore

    def test_field_readonly_basename(self) -> None:
        assert self.interface.readonly_basename == "simple"

    def test_field_readonly_dirname(self) -> None:
        assert self.interface.readonly_dirname == os.path.dirname(self.tmp)

    def test_field_readonly_extension(self) -> None:
        assert self.interface.readonly_extension == "mscx"

    def test_field_readonly_filename(self) -> None:
        assert self.interface.readonly_filename == "simple.mscx"

    def test_field_readonly_relpath(self) -> None:
        assert self.interface.readonly_relpath == self.tmp

    def test_field_readonly_relpath_backup(self) -> None:
        assert self.interface.readonly_relpath_backup == self.tmp.replace(
            ".mscx", "_bak.mscx"
        )


class TestClassInterface:
    def setup_method(self) -> None:
        self.fields: list[str] = [
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

        self.tmp: str = helper.get_file("meta-all-values.mscx")
        self.xml_tree = Score(self.tmp)
        self.interface = Interface(self.xml_tree)

    def test_static_method_get_all_fields(self) -> None:
        assert Interface.get_all_fields() == self.fields

    def test_get(self) -> None:
        for field in self.fields:
            assert getattr(self.interface, field), field

    def test_set(self) -> None:
        self.interface.vbox_title = "lol"
        assert self.interface.vbox_title == "lol"

    def test_exception(self) -> None:
        with pytest.raises(mscxyz.meta.ReadOnlyFieldError):
            self.interface.readonly_extension = "lol"


def get_meta_tag(filename: str, version: int) -> MetaTag:
    score = helper.get_score(filename, version)
    return score.meta.meta_tag


@pytest.fixture
def meta_tag_v2() -> MetaTag:
    return get_meta_tag("simple.mscx", version=2)


@pytest.fixture
def meta_tag_v3() -> MetaTag:
    return get_meta_tag("simple.mscx", version=3)


@pytest.fixture
def meta_tag_v4() -> MetaTag:
    return get_meta_tag("simple.mscz", version=4)


class TestClassMetaTag:
    def _init_class(
        self, filename: str, version: int = 2
    ) -> tuple[MetaTag, Score, str]:
        tmp = helper.get_file(filename, version)
        score = Score(tmp)
        meta = score.meta.meta_tag
        return meta, score, tmp

    def test_get_v2(self, meta_tag_v2: MetaTag) -> None:
        assert meta_tag_v2.work_title == "Title"
        assert meta_tag_v2.arranger is None
        assert meta_tag_v2.composer == "Composer"

    def test_get_v3(self, meta_tag_v3: MetaTag) -> None:
        assert meta_tag_v3.work_title == "Title"
        assert meta_tag_v3.arranger is None
        assert meta_tag_v3.composer == "Composer"

    def test_get_v4(self, meta_tag_v4: MetaTag) -> None:
        assert meta_tag_v4.work_title == "Title"
        assert meta_tag_v4.arranger is None
        assert meta_tag_v4.composer == "Composer"
        assert meta_tag_v4.creation_date is None
        assert meta_tag_v4.msc_version == "4.20"

    def test_set_v2(self, meta_tag_v2: MetaTag) -> None:
        meta_tag_v2.movement_title = "MT"
        meta_tag_v2.score.save()
        new_score = meta_tag_v2.score.reload()

        assert new_score.meta.meta_tag.movement_title == "MT"
        assert '<metaTag name="movementTitle">MT</metaTag>' in new_score.read_as_text()

    def test_set_v3(self, meta_tag_v3: MetaTag) -> None:
        meta_tag_v3.movement_title = "MT"
        meta_tag_v3.score.save()
        new_score = meta_tag_v3.score.reload()

        assert new_score.meta.meta_tag.work_title == "WT"
        assert '<metaTag name="workTitle">WT</metaTag>' in new_score.read_as_text()

    def test_clean(self) -> None:
        meta, _, _ = self._init_class("simple.mscx")
        meta.arranger = "A"
        assert meta.arranger == "A"
        meta.clean()
        assert meta.arranger == ""


def get_vbox(filename: str, version: int) -> Vbox:
    score = helper.get_score(filename, version)
    return score.meta.vbox


def vbox_v3() -> Vbox:
    return get_vbox("simple.mscx", version=3)


class TestClassVbox:
    def _init_class(self, filename: str, version: int = 2) -> tuple[Vbox, Score, str]:
        tmp = helper.get_file(filename, version)
        score = Score(tmp)
        vbox = Vbox(score)
        return vbox, score, tmp

    def _test_init(self, version: int) -> None:
        _, tree, tmp = self._init_class("no-vbox.mscx", version)
        tree.save()
        xml_string = helper.read_file(tmp)
        assert "<VBox>" in xml_string

    def test_init(self) -> None:
        self._test_init(version=2)
        self._test_init(version=3)

    @pytest.mark.parametrize(
        "version",
        [
            2,
            3,
        ],
    )
    def test_get(self, version: int) -> None:
        vbox = get_vbox("simple.mscx", version)
        assert vbox.subtitle is None
        assert vbox.title == "Title"
        assert vbox.composer == "Composer"

    def _test_get_exception(self, version: int) -> None:
        vbox, _, _ = self._init_class("simple.mscx", version)
        with pytest.raises(meta.UnkownFieldError):
            vbox.lol  # type: ignore

    def test_get_exception(self) -> None:
        self._test_get_exception(version=2)
        self._test_get_exception(version=3)

    @pytest.mark.parametrize(
        "filename,version",
        [
            ("simple.mscx", 2),
            ("simple.mscx", 3),
            ("no-vbox.mscx", 2),
            ("no-vbox.mscx", 3),
        ],
    )
    def test_set(self, filename: str, version: int) -> None:
        vbox = get_vbox(filename, version)
        vbox.title = "New Title"
        vbox.score.save()

        new_score = vbox.score.reload()

        assert new_score.meta.vbox.title == "New Title"
        assert "<text>New Title</text>" in new_score.read_as_text()

    def _test_set_exception(self, version: int = 2) -> None:
        vbox, _, _ = self._init_class("simple.mscx", version)
        with pytest.raises(meta.UnkownFieldError):
            vbox.lol = "lol"  # type: ignore

    def test_set_exception(self) -> None:
        self._test_set_exception(version=2)
        self._test_set_exception(version=3)


class TestClassCombined:
    def _init_class(self, filename: str) -> tuple[Combined, Score, str]:
        tmp = helper.get_file(filename)
        score = Score(tmp)
        c = Combined(score)
        return c, score, tmp

    def test_getter(self) -> None:
        c, _, _ = self._init_class("simple.mscx")
        assert c.title == "Title"
        assert c.subtitle is None
        assert c.composer == "Composer"
        assert c.lyricist is None

    def test_setter(self) -> None:
        c, tree, _ = self._init_class("simple.mscx")
        c.title = "T"
        c.subtitle = "S"
        c.composer = "C"
        c.lyricist = "L"
        tree.save()
        c = Combined(tree)
        assert c.metatag.work_title == "T"
        assert c.metatag.movement_title == "S"
        assert c.metatag.composer == "C"
        assert c.metatag.lyricist == "L"

        assert c.vbox.title == "T"
        assert c.vbox.subtitle == "S"
        assert c.vbox.composer == "C"
        assert c.vbox.lyricist == "L"


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
        i = reload(tmp)
        assert i.vbox_composer == "Composer"
        assert i.metatag_composer == "Composer"
        assert i.vbox_title == "Title"
        assert i.metatag_work_title == "Title"

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
        i = reload(tmp)
        assert i.vbox_composer == "Composer"
        assert i.metatag_composer == "Composer"
        assert i.vbox_title == "Title"
        assert i.metatag_work_title == "Title"

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
        i = reload(tmp)
        assert i.metatag_lyricist == "Composer"
        assert i.metatag_composer == "Composer"
        assert i.metatag_movement_title == "Title"
        assert i.metatag_work_title == "Title"

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
        score = helper.reload(tmp)
        i = score.meta.interface_read_write
        for field in i.fields:
            assert getattr(i, field) is None, field

    def test_clean_single_field(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title", tmp])
        i = reload(tmp)
        assert i.vbox_title is None, "vbox_title"
        assert i.vbox_composer == "vbox_composer", "vbox_composer"

    def test_clean_some_fields(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(["meta", "--clean", "vbox_title,vbox_composer", tmp])
        i = reload(tmp)
        assert i.vbox_title is None, "vbox_title"
        assert i.vbox_composer is None, "vbox_composer"
        assert i.vbox_subtitle == "vbox_subtitle", "vbox_subtitle"

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
        i = reload(tmp)
        assert i.vbox_title == "lol"

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
        i = reload(tmp)
        assert i.vbox_title == "lol"
        assert i.vbox_composer == "troll"

    def test_set_field_with_templating(self) -> None:
        tmp = helper.get_file("meta-all-values.mscx")
        mscxyz.execute(
            ["meta", "--set-field", "vbox_title", "$vbox_title ($vbox_composer)", tmp]
        )
        i = reload(tmp)
        assert i.vbox_title == "vbox_title (vbox_composer)"

    def test_delete_duplicates(self) -> None:
        tmp = helper.get_file("meta-duplicates.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        i = reload(tmp)
        assert not i.combined_lyricist
        assert not i.combined_subtitle

    def test_delete_duplicates_move_subtitle(self) -> None:
        tmp = helper.get_file("meta-duplicates-move-subtitle.mscx")
        mscxyz.execute(["meta", "--delete-duplicates", tmp])
        i = reload(tmp)
        assert not i.combined_lyricist
        assert not i.combined_subtitle
        assert i.combined_title == "Title"

    def test_log(self) -> None:
        tmp = helper.get_file("simple.mscx")
        log = tempfile.mktemp()
        mscxyz.execute(
            ["meta", "--log", log, "$combined_title-$combined_composer", tmp]
        )
        log_file = open(log, "r")
        assert log_file.readline() == "Title-Composer\n"


class TestClassMeta:
    meta: Meta

    def setup_method(self) -> None:
        self.meta: Meta = helper.get_meta("meta-all-values.mscx")

    def test_method_clean_metadata(self) -> None:
        self.meta.interface.combined_lyricist = "test"
        self.meta.clean_metadata("all")
        assert self.meta.interface.combined_lyricist is None

    def test_method_delete_duplicates(self) -> None:
        self.meta.interface.combined_lyricist = "test"
        self.meta.interface.combined_composer = "test"
        assert self.meta.interface.combined_lyricist == "test"
        self.meta.delete_duplicates()
        assert self.meta.interface.combined_lyricist is None

    def test_method_show(self, capsys: pytest.CaptureFixture[str]) -> None:
        self.meta.show({"combined_title": "pre"}, {"combined_title": "post"})
        capture = capsys.readouterr()
        assert capture.out == "combined_title: “pre” -> “post”\n"

    def test_method_export_json(self) -> None:
        result_path: Path = self.meta.export_json()
        assert result_path.exists()

        json: str = helper.read_file(result_path)
        # json = (
        #     '{\n    "combined_composer": "vbox_composer",\n'
        #     '    "combined_lyricist": "vbox_lyricist",\n'
        #     '    "combined_subtitle": "vbox_subtitle",\n'
        #     '    "combined_title": "vbox_title",\n'
        #     '    "metatag_arranger": "metatag_arranger",\n'
        #     '    "metatag_composer": "metatag_composer",\n'
        #     '    "metatag_copyright": "metatag_copyright",\n'
        #     '    "metatag_creation_date": "metatag_creation_date",\n'
        #     '    "metatag_lyricist": "metatag_lyricist",\n'
        #     '    "metatag_movement_number": "metatag_movement_number",\n'
        #     '    "metatag_movement_title": "metatag_movement_title",\n'
        #     '    "metatag_platform": "metatag_platform",\n'
        #     '    "metatag_poet": "metatag_poet",\n'
        #     '    "metatag_source": "metatag_source",\n'
        #     '    "metatag_translator": "metatag_translator",\n'
        #     '    "metatag_work_number": "metatag_work_number",\n'
        #     '    "metatag_work_title": "metatag_work_title",\n'
        #     '    "readonly_abspath": "/tmp/tmp1rv5ybvu/meta-all-values.mscx",\n'
        #     '    "readonly_basename": "meta-all-values",\n'
        #     '    "readonly_dirname": "/tmp/tmp1rv5ybvu",\n'
        #     '    "readonly_extension": "mscx",\n'
        #     '    "readonly_filename": "meta-all-values.mscx",\n'
        #     '    "readonly_relpath": "/tmp/tmp1rv5ybvu/meta-all-values.mscx",\n'
        #     '    "readonly_relpath_backup": "/tmp/tmp1rv5ybvu/meta-all-values_bak.mscx",\n'
        #     '    "vbox_composer": "vbox_composer",\n'
        #     '    "vbox_lyricist": "vbox_lyricist",\n'
        #     '    "vbox_subtitle": "vbox_subtitle",\n'
        #     '    "vbox_title": "vbox_title"\n}'
        # )
        assert '{\n    "combined_composer": "vbox_composer",\n' in json
        assert '"readonly_basename": "meta-all-values"' in json
