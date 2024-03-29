"""Test submodule “meta.py”."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import meta, supported_versions, utils
from mscxyz.meta import (
    Meta,
    Metatag,
    Vbox,
)
from mscxyz.score import Score
from tests import helper
from tests.helper import Cli


class TestExceptions:
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


def get_meta_tag(filename: str, version: int) -> Metatag:
    score = helper.get_score(filename, version)
    return score.meta.metatag


class TestClassMetaTag:
    @pytest.mark.parametrize(
        "version,msc_version",
        [(2, None), (3, None), (4, "4.20")],
    )
    def test_get(self, version: int, msc_version: str | None) -> None:
        m = get_meta_tag("score.mscz", version)
        assert m.arranger is None
        assert m.audio_com_url is None
        assert m.composer == "Composer"
        assert m.copyright is None
        assert m.creation_date is None
        assert m.work_title == "Title"
        assert m.arranger is None
        assert m.platform == "Linux"
        assert m.msc_version == msc_version

    @pytest.mark.parametrize("version", supported_versions)
    def test_set(self, version: int) -> None:
        m = get_meta_tag("score.mscz", version)
        m.movement_title = "MT"
        m.score.save()
        new_score = m.score.reload()
        assert new_score.meta.metatag.movement_title == "MT"
        assert '<metaTag name="movementTitle">MT</metaTag>' in new_score.read_as_text()

    @pytest.mark.parametrize("version", supported_versions)
    def test_clean(self, version: int) -> None:
        m = get_meta_tag("score.mscz", version)
        m.arranger = "A"
        assert m.arranger == "A"
        m.clean()
        assert m.arranger is None


def get_vbox(filename: str, version: int) -> Vbox:
    score = helper.get_score(filename, version)
    return score.meta.vbox


class TestClassVbox:
    @pytest.mark.parametrize("version", supported_versions)
    def test_get(self, version: int) -> None:
        vbox = get_vbox("score.mscz", version)
        assert vbox.title == "Title"
        assert vbox.subtitle is None
        assert vbox.composer == "Composer"
        assert vbox.lyricist is None

    @pytest.mark.parametrize(
        "filename,version",
        [
            ("simple.mscx", 2),
            ("simple.mscx", 3),
            ("score.mscz", 4),
            ("no-vbox.mscx", 2),
            ("no-vbox.mscx", 3),
            ("no-vbox.mscz", 4),
        ],
    )
    def test_set(self, filename: str, version: int) -> None:
        vbox = get_vbox(filename, version)
        vbox.title = "New Title"
        vbox.score.save()

        new_score = vbox.score.reload()

        assert new_score.meta.vbox.title == "New Title"
        assert "<text>New Title</text>" in new_score.read_as_text()


class TestOptionDistributeField:
    def test_distribute_field(self, score: Score) -> None:
        score.meta.vbox.title = "Mozart: Alla Turca"
        score.save()
        c = Cli(
            "--distribute-field", "vbox_title", "$composer: $title", score
        ).execute()
        f = c.post.fields
        assert f.get("vbox_composer") == "Mozart"
        assert f.get("metatag_composer") == "Mozart"
        assert f.get("vbox_title") == "Alla Turca"
        assert f.get("metatag_work_title") == "Alla Turca"

    def test_distribute_field_multiple_source_fields(self, score: Score) -> None:
        score.meta.vbox.title = "Für Elise - Ludwig van Beethoven"
        score.save()
        c = Cli(
            "--distribute-field",
            "vbox_title,metatag_poet",
            "$title - $composer",
            score,
        ).execute()
        f = c.post.fields
        assert f.get("vbox_composer") == "Ludwig van Beethoven"
        assert f.get("metatag_composer") == "Ludwig van Beethoven"
        assert f.get("vbox_title") == "Für Elise"
        assert f.get("metatag_work_title") == "Für Elise"

    def test_distribute_field_multiple_values(self) -> None:
        c = (
            Cli(
                "--distribute-field",
                "vbox_title",
                "$metatag_work_title - $metatag_composer",
                "--distribute-field",
                "vbox_title",
                "$metatag_movement_title - $metatag_lyricist",
            )
            .append_score("meta-distribute-field.mscz")
            .execute()
        )
        f = c.post.fields
        assert f.get("metatag_lyricist") == "Composer"
        assert f.get("metatag_composer") == "Composer"
        assert f.get("metatag_movement_title") == "Title"
        assert f.get("metatag_work_title") == "Title"

    def test_distribute_field_invalid_format_string(self) -> None:
        with pytest.raises(meta.FormatStringNoFieldError):
            Cli(
                "--distribute-field",
                "vbox_title",
                "lol",
            ).append_score("meta-distribute-field.mscz").execute()

    def test_distribute_field_exception_unmatched(self) -> None:
        stdout = Cli(
            "--catch-errors",
            "--distribute-field",
            "vbox_title",
            "$metatag_work_title - $metatag_composer",
        ).stdout()
        assert "UnmatchedFormatStringError" in stdout


class TestOptionClean:
    def test_clean_all(self) -> None:
        f = Cli("--clean-meta", "all").append_score("meta-all-values.mscz").fields()
        for field in f:
            if not field.readonly:
                assert f.get(field.name) is None, field

    def test_clean_single_field(self) -> None:
        f = (
            Cli("--clean-meta", "vbox_title")
            .append_score("meta-all-values.mscz")
            .execute()
        ).fields()
        assert f.get("vbox_title") is None, "vbox_title"
        assert f.get("vbox_composer") == "vbox_composer", "vbox_composer"

    def test_clean_some_fields(self) -> None:
        f = (
            Cli("--clean-meta", "vbox_title,vbox_composer")
            .append_score("meta-all-values.mscz")
            .execute()
        ).fields()
        assert f.get("vbox_title") is None, "vbox_title"
        assert f.get("vbox_composer") is None, "vbox_composer"
        assert f.get("vbox_subtitle") == "vbox_subtitle", "vbox_subtitle"


class TestStdout:
    def test_verbose_0(self) -> None:
        stdout = Cli("--clean-meta", "all").stdout()
        assert stdout == ""

    def test_verbose_1(self) -> None:
        stdout = (
            Cli("-v", "--clean-meta", "all")
            .append_score("meta-all-values.mscz")
            .stdout()
        )
        lines = stdout.splitlines()
        assert lines[0] == ""
        assert "vbox_title: “vbox_title” ->" in stdout
        assert "path: " not in stdout

    def test_verbose_2(self) -> None:
        assert "path: " in Cli("-vv", "--clean-meta", "all").stdout()


def test_option_metatag() -> None:
    score = Cli(
        "--metatag",
        "arranger",
        "a",
        #
        "--metatag",
        "audio_com_url",
        "acu",
        #
        "--metatag",
        "composer",
        "c",
        #
        "--metatag",
        "copyright",
        "c",
        #
        "--metatag",
        "creation_date",
        "cd",
        #
        "--metatag",
        "lyricist",
        "l",
        #
        "--metatag",
        "movement_number",
        "mn",
        #
        "--metatag",
        "movement_title",
        "mt",
        #
        "--metatag",
        "msc_version",
        "mv",
        #
        "--metatag",
        "platform",
        "p",
        #
        "--metatag",
        "poet",
        "p",
        #
        "--metatag",
        "source",
        "s",
        #
        "--metatag",
        "source_revision_id",
        "sri",
        #
        "--metatag",
        "subtitle",
        "s",
        #
        "--metatag",
        "translator",
        "t",
        #
        "--metatag",
        "work_number",
        "wn",
        #
        "--metatag",
        "work_title",
        "wt",
    ).score()

    m = score.meta.metatag
    assert m.arranger == "a"
    assert m.audio_com_url == "acu"
    assert m.composer == "c"
    assert m.copyright == "c"
    assert m.creation_date == "cd"
    assert m.lyricist == "l"
    assert m.movement_number == "mn"
    assert m.movement_title == "mt"
    assert m.msc_version == "mv"
    assert m.platform == "p"
    assert m.poet == "p"
    assert m.source == "s"
    assert m.source_revision_id == "sri"
    assert m.subtitle == "s"
    assert m.translator == "t"
    assert m.work_number == "wn"
    assert m.work_title == "wt"


def test_option_vbox() -> None:
    score = Cli(
        "--vbox",
        "composer",
        "c",
        #
        "--vbox",
        "lyricist",
        "l",
        #
        "--vbox",
        "subtitle",
        "s",
        #
        "--vbox",
        "title",
        "t",
    ).score()

    v = score.meta.vbox
    assert v.composer == "c"
    assert v.lyricist == "l"
    assert v.subtitle == "s"
    assert v.title == "t"


class TestOptionSetField:
    def test_simple_string(self) -> None:
        s = (
            Cli("--set-field", "vbox_title", "test")
            .append_score("meta-all-values.mscz")
            .score()
        )
        assert s.meta.vbox.title == "test"

    def test_multiple_times(self) -> None:
        s = (
            Cli(
                "--set-field",
                "vbox_title",
                "vt",
                "--set-field",
                "vbox_composer",
                "vc",
            )
            .append_score("meta-all-values.mscz")
            .score()
        )

        assert s.meta.vbox.title == "vt"
        assert s.meta.vbox.composer == "vc"

    def test_with_templating(self) -> None:
        s = (
            Cli(
                "--set-field",
                "vbox_title",
                "$vbox_title ($vbox_composer)",
            )
            .append_score("meta-all-values.mscz")
            .score()
        )
        assert s.meta.vbox.title == "vbox_title (vbox_composer)"


def test_option_log(tmp_path: Path) -> None:
    log = tmp_path / "log.txt"
    Cli("--log", log, "$title-$composer").execute()
    assert open(log, "r").readline() == "Title-Composer\n"


class TestOptionDeleteDuplicates:
    def test_normal(self) -> None:
        s = Cli("--delete-duplicates").append_score("meta-duplicates.mscz").score()
        assert not s.meta.lyricist
        assert not s.meta.subtitle

    def test_move_subtitle(self) -> None:
        s = (
            Cli("--delete-duplicates")
            .append_score("meta-duplicates-move-subtitle.mscz")
            .score()
        )
        assert not s.meta.lyricist
        assert not s.meta.subtitle
        assert s.meta.title == "Title"


def test_option_synchronize() -> None:
    c = Cli("--synchronize").append_score("meta-all-values.mscz").execute()

    pre = c.pre.meta
    post = c.post.meta

    # pre
    assert pre.vbox.title == "vbox_title"
    assert pre.metatag.work_title == "metatag_work_title"
    # post
    assert post.vbox.title == post.metatag.work_title == "vbox_title"

    # pre
    assert pre.vbox.subtitle == "vbox_subtitle"
    assert pre.metatag.movement_title == "metatag_movement_title"
    # post
    assert post.vbox.subtitle == post.metatag.movement_title == "vbox_subtitle"

    # pre
    assert pre.vbox.composer == "vbox_composer"
    assert pre.metatag.composer == "metatag_composer"
    # post
    assert post.vbox.composer == post.metatag.composer == "vbox_composer"

    # pre
    assert pre.vbox.lyricist is None
    assert pre.metatag.lyricist == "metatag_lyricist"
    # post
    assert post.vbox.lyricist == post.metatag.lyricist == "metatag_lyricist"


def test_option_json() -> None:
    score = (Cli("--json").append_score("meta-all-values.mscz").execute()).score()
    json = score.json_file
    assert json.exists()
    assert '"basename": "meta-all-values"' in utils.read_file(json)


class TestClassMeta:
    meta: Meta

    def setup_method(self) -> None:
        self.meta: Meta = helper.get_meta("meta-all-values.mscx")

    def test_method_clean_metadata(self) -> None:
        self.meta.vbox.lyricist = "test"
        self.meta.clean()
        assert self.meta.vbox.title is None
        assert self.meta.vbox.subtitle is None
        assert self.meta.vbox.composer is None
        assert self.meta.vbox.lyricist is None
        assert self.meta.metatag.arranger is None
        assert self.meta.metatag.audio_com_url is None
        assert self.meta.metatag.composer is None
        assert self.meta.metatag.copyright is None
        assert self.meta.metatag.creation_date is None
        assert self.meta.metatag.lyricist is None
        assert self.meta.metatag.movement_number is None
        assert self.meta.metatag.movement_title is None
        assert self.meta.metatag.msc_version is None
        assert self.meta.metatag.platform is None
        assert self.meta.metatag.poet is None
        assert self.meta.metatag.source is None
        assert self.meta.metatag.source_revision_id is None
        assert self.meta.metatag.subtitle is None
        assert self.meta.metatag.translator is None
        assert self.meta.metatag.work_number is None
        assert self.meta.metatag.work_title is None
        assert self.meta.title is None
        assert self.meta.subtitle is None
        assert self.meta.composer is None
        assert self.meta.lyricist is None

    def test_method_delete_duplicates(self) -> None:
        self.meta.lyricist = "test"
        self.meta.composer = "test"
        assert self.meta.lyricist == "test"
        self.meta.delete_duplicates()
        assert self.meta.lyricist is None

    def test_property_title(self, score: Score) -> None:
        assert score.meta.title == "Title"
        new = "New Title"
        score.meta.title = new
        assert score.meta.title == new
        assert score.meta.vbox.title == new
        assert score.meta.metatag.work_title == new

    def test_property_subtitle(self, score: Score) -> None:
        assert score.meta.subtitle is None
        new = "New Subtitle"
        score.meta.subtitle = new
        assert score.meta.subtitle == new
        assert score.meta.vbox.subtitle == new
        assert score.meta.metatag.subtitle == new
        assert score.meta.metatag.movement_title == new

    def test_property_composer(self, score: Score) -> None:
        assert score.meta.composer == "Composer"
        new = "New Composer"
        score.meta.composer = new
        assert score.meta.composer == new
        assert score.meta.vbox.composer == new
        assert score.meta.metatag.composer == new

    def test_property_lyricist(self, score: Score) -> None:
        assert score.meta.lyricist is None
        new = "New Lyricist"
        score.meta.lyricist = new
        assert score.meta.lyricist == new
        assert score.meta.vbox.lyricist == new
        assert score.meta.metatag.lyricist == new
