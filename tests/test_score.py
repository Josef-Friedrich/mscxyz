"""Test submodules “score.py”"""


from __future__ import annotations

import filecmp
import os
import pathlib
import shutil
import tempfile
from typing import Optional
from unittest import mock

import pytest

import mscxyz
from mscxyz.score import (
    MuseScoreFile,
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
    def test_batch(self, Meta):
        mscxyz.execute(["meta", helper.get_dir("batch")])
        assert Meta.call_count == 3

    def test_without_extension(self):
        result = self._list_scores("/test")
        assert result == ["/a/b/dolor.mscx", "/a/b/impsum.mscz", "/a/lorem.mscx"]

    def test_extension_both(self):
        result = self._list_scores("/test", extension="both")
        assert result == ["/a/b/dolor.mscx", "/a/b/impsum.mscz", "/a/lorem.mscx"]

    def test_extension_mscx(self):
        result = self._list_scores("/test", extension="mscx")
        assert result == ["/a/b/dolor.mscx", "/a/lorem.mscx"]

    def test_extension_mscz(self):
        result = self._list_scores("/test", extension="mscz")
        assert result == ["/a/b/impsum.mscz"]

    def test_raises_exception(self):
        with pytest.raises(ValueError):
            self._list_scores("/test", extension="lol")

    def test_isfile(self):
        with mock.patch("os.path.isfile") as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores("/a/b/lorem.mscx")
            assert result == ["/a/b/lorem.mscx"]

    def test_isfile_no_match(self):
        with mock.patch("os.path.isfile") as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores("/a/b/lorem.lol")
            assert result == []

    def test_arg_glob_txt(self):
        result = self._list_scores("/test", glob="*.txt")
        assert result == ["/a/b/sit.txt"]

    def test_arg_glob_lol(self):
        result = self._list_scores("/test", glob="*.lol")
        assert result == []

    def test_function_list_zero_alphabet(self):
        result = list_zero_alphabet()
        assert result[0] == "0"
        assert result[26] == "z"


class TestClassMuseScoreFile:
    def setup_method(self) -> None:
        self.file = MuseScoreFile(helper.get_file("simple.mscx"))

    def test_attribute_path(self) -> None:
        assert self.file.relpath

    def test_attribute_relpath(self) -> None:
        assert self.file.path.exists()

    def test_attribute_abspath(self) -> None:
        assert self.file.abspath == self.file.loadpath
        pathlib.Path(self.file.abspath).exists()

    def test_attribute_dirname(self) -> None:
        assert self.file.dirname

    def test_attribute_filename(self) -> None:
        assert self.file.filename == "simple.mscx"

    def test_attribute_extension(self) -> None:
        assert self.file.extension == "mscx"

    def test_attribute_basename(self) -> None:
        assert self.file.basename == "simple"

    def test_method_clean(self) -> None:
        tmp = helper.get_file("clean.mscx", version=3)
        tree = MuseScoreFile(tmp)
        tree.clean()
        tree.save()
        tree = MuseScoreFile(tmp)
        xml_tree = tree.xml_tree
        assert xml_tree.xpath("/museScore/Score/Style") == []
        assert xml_tree.xpath("//LayoutBreak") == []
        assert xml_tree.xpath("//StemDirection") == []
        assert xml_tree.xpath("//font") == []
        assert xml_tree.xpath("//b") == []
        assert xml_tree.xpath("//i") == []
        assert xml_tree.xpath("//pos") == []
        assert xml_tree.xpath("//offset") == []

    def test_method_save(self) -> None:
        tmp = helper.get_file("simple.mscx")
        tree = MuseScoreFile(tmp)
        tree.save()
        result = helper.read_file(tmp)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_method_save_new_name(self):
        tmp = helper.get_file("simple.mscx")
        tree = MuseScoreFile(tmp)
        tree.save(new_name=tmp)
        result = helper.read_file(tmp)
        assert '<metaTag name="arranger"></metaTag>' in result

    def test_mscz(self):
        tmp = helper.get_file("simple.mscz")
        tree = MuseScoreFile(tmp)
        result = tree.xml_tree.xpath("/museScore/Score/Style")
        assert result[0].tag == "Style"


@pytest.mark.skip("Not implemented yet")
class TestMuseScoreFileMscz:
    def setup_method(self):
        self.file = MuseScoreFile(helper.get_file("simple.mscz"))

    def test_attribute_extension(self):
        assert self.file.extension == "mscz"

    def test_attribute_loadpath(self):
        assert "simple.mscx" in self.file.loadpath


class TestMuseScoreFileMscz4:
    def setup_method(self):
        self.file = MuseScoreFile(
            helper.get_file("test.mscz", version=4),
        )

    def test_attribute_extension(self):
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


class TestMuseScoreFileVersion2:
    tree = MuseScoreFile(helper.get_file("simple.mscz", 2))

    def test_property_version(self) -> None:
        assert self.tree.version == 2.06

    def test_property_version_major(self) -> None:
        assert self.tree.version_major == 2

    def test_method_get_version(self) -> None:
        assert self.tree.get_version() == 2.06


class TestMuseScoreFileVersion3:
    tree = MuseScoreFile(helper.get_file("simple.mscz", 3))

    def test_property_version(self) -> None:
        assert self.tree.version == 3.01

    def test_property_version_major(self) -> None:
        assert self.tree.version_major == 3

    def test_method_get_version(self) -> None:
        assert self.tree.get_version() == 3.01


class TestMuseScoreFileVersion4:
    tree = MuseScoreFile(helper.get_file("simple.mscz", 4))

    def test_property_version(self) -> None:
        assert self.tree.version == 4.2

    def test_property_version_major(self) -> None:
        assert self.tree.version_major == 4

    def test_method_get_version(self) -> None:
        assert self.tree.get_version() == 4.2


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
    def assertDiff(self, filename: str, version: int = 2):
        orig = os.path.join(os.path.expanduser("~"), filename)
        saved = orig.replace(".mscx", "_saved.mscx")
        tmp = helper.get_file(filename, version=version)
        shutil.copy2(tmp, orig)
        tree = MuseScoreFile(tmp)
        tree.save(new_name=saved)
        assert filecmp.cmp(orig, saved)
        os.remove(orig)
        os.remove(saved)

    def test_getting_started(self):
        self.assertDiff("Getting_Started_English.mscx", version=2)
        self.assertDiff("Getting_Started_English.mscx", version=3)

    def test_lyrics(self):
        self.assertDiff("lyrics.mscx", version=2)
        self.assertDiff("lyrics.mscx", version=3)

    def test_chords(self):
        self.assertDiff("chords.mscx", version=2)
        self.assertDiff("chords.mscx", version=3)

    def test_unicode(self):
        self.assertDiff("unicode.mscx", version=2)
        self.assertDiff("unicode.mscx", version=3)

    def test_real_world_ragtime_3(self):
        self.assertDiff("Ragtime_3.mscx", version=2)
        # self.assertDiff('Ragtime_3.mscx', version=3)

    def test_real_world_zum_tanze(self):
        self.assertDiff("Zum-Tanze-da-geht-ein-Maedel.mscx", version=2)
        self.assertDiff("Zum-Tanze-da-geht-ein-Maedel.mscx", version=3)

    def test_real_world_all_dudes(self):
        self.assertDiff("All_Dudes.mscx", version=2)
        self.assertDiff("All_Dudes.mscx", version=3)

    def test_real_world_reunion(self):
        self.assertDiff("Reunion.mscx", version=2)
        self.assertDiff("Reunion.mscx", version=3)

    def test_real_world_triumph(self):
        self.assertDiff("Triumph.mscx", version=2)
        self.assertDiff("Triumph.mscx", version=3)
