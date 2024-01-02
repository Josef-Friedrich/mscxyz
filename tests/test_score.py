"""Test submodules “score.py”"""


from __future__ import annotations

import filecmp
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from unittest import mock

import pytest
from lxml.etree import _Element

import mscxyz
from mscxyz.score import (
    Score,
    ZipContainer,
    list_scores,
    list_zero_alphabet,
)
from tests import helper


class TestFunctions:
    @staticmethod
    def _list_scores(
        path: str, extension: str = "both", glob: Optional[str] = None
    ) -> list[str]:
        with mock.patch("os.walk") as mockwalk:
            mockwalk.return_value = [
                ("/a", ("bar",), ("lorem.mscx",)),
                ("/a/b", (), ("impsum.mscz", "dolor.mscx", "sit.txt")),
            ]
            return list_scores(path, extension, glob)

    @mock.patch("mscxyz.Meta")
    def test_batch(self, Meta: mock.Mock) -> None:
        mscxyz.execute(["meta", helper.get_dir("batch")])
        assert Meta.call_count == 3

    def test_without_extension(self) -> None:
        result: list[str] = self._list_scores("/test")
        assert result == ["/a/b/dolor.mscx", "/a/b/impsum.mscz", "/a/lorem.mscx"]

    def test_extension_both(self) -> None:
        result: list[str] = self._list_scores("/test", extension="both")
        assert result == ["/a/b/dolor.mscx", "/a/b/impsum.mscz", "/a/lorem.mscx"]

    def test_extension_mscx(self) -> None:
        result: list[str] = self._list_scores("/test", extension="mscx")
        assert result == ["/a/b/dolor.mscx", "/a/lorem.mscx"]

    def test_extension_mscz(self) -> None:
        result: list[str] = self._list_scores("/test", extension="mscz")
        assert result == ["/a/b/impsum.mscz"]

    def test_raises_exception(self) -> None:
        with pytest.raises(ValueError):
            self._list_scores("/test", extension="lol")

    def test_isfile(self) -> None:
        with mock.patch("os.path.isfile") as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores("/a/b/lorem.mscx")
            assert result == ["/a/b/lorem.mscx"]

    def test_isfile_no_match(self) -> None:
        with mock.patch("os.path.isfile") as mock_isfile:
            mock_isfile.return_value = True
            result: list[str] = list_scores("/a/b/lorem.lol")
            assert result == []

    def test_arg_glob_txt(self) -> None:
        result: list[str] = self._list_scores("/test", glob="*.txt")
        assert result == ["/a/b/sit.txt"]

    def test_arg_glob_lol(self) -> None:
        result: list[str] = self._list_scores("/test", glob="*.lol")
        assert result == []

    def test_function_list_zero_alphabet(self) -> None:
        result: list[str] = list_zero_alphabet()
        assert result[0] == "0"
        assert result[26] == "z"


class TestClassScore:
    def setup_method(self) -> None:
        self.score = helper.get_score("simple.mscx")

    def test_attribute_path(self) -> None:
        assert self.score.path.exists()

    def test_attribute_relpath(self) -> None:
        assert self.score.relpath

    def test_attribute_dirname(self) -> None:
        path = Path(self.score.dirname)
        assert path.is_dir()
        assert path.exists()

    def test_attribute_filename(self) -> None:
        assert self.score.filename == "simple.mscx"

    def test_attribute_extension(self) -> None:
        assert self.score.extension == "mscx"

    def test_attribute_basename(self) -> None:
        assert self.score.basename == "simple"

    def test_method_clean(self) -> None:
        score = helper.get_score("clean.mscx", version=3)
        score.clean()
        score.save()
        score = Score(str(score.path))
        xml_tree = score.xml_tree
        assert xml_tree.xpath("/museScore/Score/Style") == []
        assert xml_tree.xpath("//LayoutBreak") == []
        assert xml_tree.xpath("//StemDirection") == []
        assert xml_tree.xpath("//font") == []
        assert xml_tree.xpath("//b") == []
        assert xml_tree.xpath("//i") == []
        assert xml_tree.xpath("//pos") == []
        assert xml_tree.xpath("//offset") == []

    def test_method_save(self) -> None:
        score = helper.get_score("simple.mscx")
        score.save()
        result = helper.read_file(score.path)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_method_save_new_name(self):
        score = helper.get_score("simple.mscx")
        score.save(new_name=str(score.path))
        result = helper.read_file(score.path)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_mscz(self):
        tmp = helper.get_file("simple.mscz")
        tree = Score(tmp)
        result = tree.xml_tree.xpath("/museScore/Score/Style")
        assert isinstance(result, list)
        assert isinstance(result[0], _Element)
        assert result[0].tag == "Style"


class TestScoreMscz3:
    def setup_method(self) -> None:
        self.score = helper.get_score("simple.mscz", version=3)

    def test_attribute_extension(self) -> None:
        assert self.score.extension == "mscz"

    def test_attribute_loadpath(self) -> None:
        assert "simple.mscx" in self.score.loadpath


class TestScoreMscz4:
    def setup_method(self) -> None:
        self.file = Score(
            helper.get_file("simple.mscz", version=4),
        )

    def test_attribute_extension(self) -> None:
        assert self.file.extension == "mscz"


class TestZipContainer:
    def setup_method(self) -> None:
        self.container = ZipContainer(
            helper.get_file("test.mscz", version=4),
        )

    def test_attribute_tmp_dir(self) -> None:
        assert str(self.container.tmp_dir).startswith(os.path.sep)
        assert self.container.tmp_dir.exists()

    def test_attribute_mscx_file(self) -> None:
        assert str(self.container.mscx_file).endswith(".mscx")
        assert self.container.mscx_file.exists()

    def test_attribute_thumbnail_file(self) -> None:
        path = self.container.thumbnail_file
        assert str(path).endswith("thumbnail.png")
        if path:
            assert path.exists()

    def test_attribute_audiosettings_file(self) -> None:
        path = self.container.audiosettings_file
        assert str(path).endswith("audiosettings.json")
        if path:
            assert path.exists()

    def test_attribute_viewsettings_file(self) -> None:
        path = self.container.viewsettings_file
        assert str(path).endswith("viewsettings.json")
        if path:
            assert path.exists()

    def test_method_save(self) -> None:
        _, dest = tempfile.mkstemp(suffix=".mscz")
        self.container.save(dest)
        container = ZipContainer(dest)
        assert container.mscx_file.exists()


class TestScoreVersion2:
    score = helper.get_score("simple.mscz", 2)

    def test_property_version(self) -> None:
        assert self.score.version == 2.06

    def test_property_version_major(self) -> None:
        assert self.score.version_major == 2

    def test_method_get_version(self) -> None:
        assert self.score.get_version() == 2.06


class TestScoreVersion3:
    score = helper.get_score("simple.mscz", 3)

    def test_property_version(self) -> None:
        assert self.score.version == 3.01

    def test_property_version_major(self) -> None:
        assert self.score.version_major == 3

    def test_method_get_version(self) -> None:
        assert self.score.get_version() == 3.01


class TestScoreVersion4:
    score = helper.get_score("simple.mscz", 4)

    def test_property_version(self) -> None:
        assert self.score.version == 4.2

    def test_property_version_major(self) -> None:
        assert self.score.version_major == 4

    def test_method_get_version(self) -> None:
        assert self.score.get_version() == 4.2


class TestClean:
    def _test_clean(self, version: int = 2) -> None:
        tmp: str = helper.get_file("formats.mscx", version)
        mscxyz.execute(["clean", tmp])
        cleaned: str = helper.read_file(tmp)
        assert "<font" not in cleaned
        assert "<b>" not in cleaned
        assert "<i>" not in cleaned
        assert "<pos" not in cleaned
        assert "<LayoutBreak>" not in cleaned
        assert "<StemDirection>" not in cleaned

    def test_clean(self):
        self._test_clean(version=2)
        self._test_clean(version=3)

    def _test_clean_add_style(self, version: int = 2) -> None:
        tmp = helper.get_file("simple.mscx", version)
        mscxyz.execute(["clean", "--style", helper.get_file("style.mss", version), tmp])
        style = helper.read_file(tmp)
        assert "<staffUpperBorder>77</staffUpperBorder>" in style

    def test_clean_add_style(self):
        self._test_clean_add_style(version=2)
        self._test_clean_add_style(version=3)


class TestFileCompare:
    def assert_diff(self, filename: str, version: int = 2):
        orig: str = os.path.join(os.path.expanduser("~"), filename)
        saved: str = orig.replace(".mscx", "_saved.mscx")
        tmp: str = helper.get_file(filename, version=version)
        shutil.copy2(tmp, orig)
        tree = Score(tmp)
        tree.save(new_name=saved)
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
