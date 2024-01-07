"""Test submodules “score.py”"""


from __future__ import annotations

import filecmp
import os
import shutil
from pathlib import Path
from typing import Optional

import pytest
from lxml.etree import _Element

import mscxyz
from mscxyz.score import (
    Score,
)
from tests import helper
from tests.helper import simulate_cli_legacy


class TestClassScore:
    def setup_method(self) -> None:
        self.score = helper.get_score("simple.mscx")

    def test_path_constructor(self) -> None:
        score = Score(helper.get_path("simple.mscx"))
        assert score.path.exists()

    def test_attribute_path(self) -> None:
        assert self.score.path.is_file()
        assert self.score.path.exists()

    def test_property_xml_file(self) -> None:
        path = Path(self.score.xml_file)
        assert path.is_file()
        assert path.exists()

    def test_property_style_file(self, score2x: Score, score4z: Score) -> None:
        assert not score2x.style_file
        assert score4z.style_file
        assert score4z.style_file.exists()

    def test_property_zip_container(self, score4z: Score) -> None:
        assert not self.score.zip_container
        assert score4z.zip_container

    def test_property_dirname(self) -> None:
        path = Path(self.score.dirname)
        assert path.is_dir()
        assert path.exists()

    def test_property_filename(self) -> None:
        assert self.score.filename == "simple.mscx"

    def test_property_extension(self) -> None:
        assert self.score.extension == "mscx"

    def test_property_basename(self) -> None:
        assert self.score.basename == "simple"

    def test_method_clean(self) -> None:
        score = helper.get_score("clean.mscx", version=3)
        score.clean()
        score.save()
        score = Score(str(score.path))
        xml_tree = score.xml_root
        assert xml_tree.xpath("/museScore/Score/Style") == []
        assert xml_tree.xpath("//LayoutBreak") == []
        assert xml_tree.xpath("//StemDirection") == []
        assert xml_tree.xpath("//font") == []
        assert xml_tree.xpath("//b") == []
        assert xml_tree.xpath("//i") == []
        assert xml_tree.xpath("//pos") == []
        assert xml_tree.xpath("//offset") == []

    def test_method_save(self) -> None:
        score: Score = helper.get_score("simple.mscx")
        score.save()
        result = helper.read_file(score.path)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_method_save_new_name(self) -> None:
        score: Score = helper.get_score("simple.mscx")
        score.save(new_dest=str(score.path))
        result = helper.read_file(score.path)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_mscz(self) -> None:
        score: Score = helper.get_score("simple.mscz")
        result = score.xml_root.xpath("/museScore/Score/Style")
        assert isinstance(result, list)
        assert isinstance(result[0], _Element)
        assert result[0].tag == "Style"


class TestMethodChangePath:
    score: Score = helper.get_score("simple.mscz")

    def change_path(
        self, extension: Optional[str] = None, suffix: Optional[str] = None
    ) -> str:
        return str(self.score.change_path(extension=extension, suffix=suffix))

    def test_argument_extension(self) -> None:
        assert self.change_path(extension="mscx").endswith(".mscx")

    def test_argument_suffix(self) -> None:
        assert self.change_path(suffix="bak").endswith("_bak.mscz")


class TestScoreMscz3:
    def setup_method(self) -> None:
        self.score: Score = helper.get_score("simple.mscz", version=3)

    def test_attribute_extension(self) -> None:
        assert self.score.extension == "mscz"

    def test_attribute_loadpath(self) -> None:
        assert "simple.mscx" in self.score.xml_file


class TestScoreMscz4:
    def setup_method(self) -> None:
        self.file = Score(
            helper.get_file("simple.mscz", version=4),
        )

    def test_attribute_extension(self) -> None:
        assert self.file.extension == "mscz"


@pytest.mark.parametrize("version,expected", [(2, 2.06), (3, 3.01), (4, 4.2)])
def test_attribute_version(version: int, expected: float) -> None:
    score = helper.get_score("score.mscz", version)
    assert score.version == expected


@pytest.mark.parametrize("version,expected", [(2, 2.06), (3, 3.01), (4, 4.2)])
def test_method_get_version(version: int, expected: float) -> None:
    score = helper.get_score("score.mscz", version)
    assert score.get_version() == expected


@pytest.mark.parametrize("version", mscxyz.supported_versions)
def test_property_version_major(version: int) -> None:
    score = helper.get_score("score.mscz", version)
    assert score.version_major == version


def test_methods_reload(score: Score) -> None:
    assert score.reload().__class__.__name__ == "Score"
    assert score.export.reload().__class__.__name__ == "Export"
    assert score.lyrics.reload().__class__.__name__ == "Lyrics"
    assert score.meta.reload().__class__.__name__ == "Meta"
    assert score.style.reload().__class__.__name__ == "Style"


class TestClean:
    def _test_clean(self, version: int = 2) -> None:
        tmp: str = helper.get_file("formats.mscx", version)
        simulate_cli_legacy("clean", tmp)
        cleaned: str = helper.read_file(tmp)
        assert "<font" not in cleaned
        assert "<b>" not in cleaned
        assert "<i>" not in cleaned
        assert "<pos" not in cleaned
        assert "<LayoutBreak>" not in cleaned
        assert "<StemDirection>" not in cleaned

    def test_clean(self) -> None:
        self._test_clean(version=2)
        self._test_clean(version=3)

    def _test_clean_add_style(self, version: int = 2) -> None:
        tmp = helper.get_file("simple.mscx", version)
        simulate_cli_legacy(
            "clean", "--style", helper.get_file("style.mss", version), tmp
        )
        style = helper.read_file(tmp)
        assert "<staffUpperBorder>77</staffUpperBorder>" in style

    def test_clean_add_style(self) -> None:
        self._test_clean_add_style(version=2)
        self._test_clean_add_style(version=3)


class TestFileCompare:
    def assert_diff(self, filename: str, version: int = 2) -> None:
        orig: str = os.path.join(os.path.expanduser("~"), filename)
        saved: str = orig.replace(".mscx", "_saved.mscx")
        tmp: str = helper.get_file(filename, version=version)
        shutil.copy2(tmp, orig)
        tree = Score(tmp)
        tree.save(new_dest=saved)
        assert filecmp.cmp(orig, saved)
        os.remove(orig)
        os.remove(saved)

    def test_getting_started(self) -> None:
        self.assert_diff("Getting_Started_English.mscx", version=2)
        self.assert_diff("Getting_Started_English.mscx", version=3)

    def test_lyrics(self) -> None:
        self.assert_diff("lyrics.mscx", version=2)
        self.assert_diff("lyrics.mscx", version=3)

    def test_chords(self) -> None:
        self.assert_diff("chords.mscx", version=2)
        self.assert_diff("chords.mscx", version=3)

    def test_unicode(self) -> None:
        self.assert_diff("unicode.mscx", version=2)
        self.assert_diff("unicode.mscx", version=3)

    def test_real_world_ragtime_3(self) -> None:
        self.assert_diff("Ragtime_3.mscx", version=2)
        # self.assertDiff('Ragtime_3.mscx', version=3)

    def test_real_world_zum_tanze(self) -> None:
        self.assert_diff("Zum-Tanze-da-geht-ein-Maedel.mscx", version=2)
        self.assert_diff("Zum-Tanze-da-geht-ein-Maedel.mscx", version=3)

    def test_real_world_all_dudes(self) -> None:
        self.assert_diff("All_Dudes.mscx", version=2)
        self.assert_diff("All_Dudes.mscx", version=3)

    def test_real_world_reunion(self) -> None:
        self.assert_diff("Reunion.mscx", version=2)
        self.assert_diff("Reunion.mscx", version=3)

    def test_real_world_triumph(self) -> None:
        self.assert_diff("Triumph.mscx", version=2)
        self.assert_diff("Triumph.mscx", version=3)
