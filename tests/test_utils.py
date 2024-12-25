"""Test submodule “utils.py”."""

from __future__ import annotations

import os
import tempfile
from typing import Optional
from unittest import mock

import pytest

from mscxyz import utils
from mscxyz.settings import get_args
from mscxyz.utils import Dimension, ListExtension, PathChanger, ZipContainer
from tests import helper
from tests.helper import Cli

args = get_args()
args.general_executable = None


class TestFunctions:
    @staticmethod
    def _list_scores(
        path: str, extension: ListExtension = "both", glob: Optional[str] = None
    ) -> list[str]:
        with (
            mock.patch("os.walk") as mockwalk,
            mock.patch("pathlib.Path.is_dir") as is_dir,
        ):
            is_dir.return_value = True
            mockwalk.return_value = [
                ("/a", ("bar",), ("lorem.mscx",)),
                ("/a/b", (), ("impsum.mscz", "dolor.mscx", "sit.txt")),
            ]
            scores: list[str] = []
            for score in utils.list_path(path, extension, glob):
                scores.append(str(score))
            scores.sort()
            return scores

    @mock.patch("mscxyz.cli.Score")
    def test_batch(self, Score: mock.Mock) -> None:
        Cli("--dry-run", helper.get_dir("batch"), append_score=False).execute()
        assert Score.call_count == 3

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
            self._list_scores("/test", extension="lol")  # type: ignore

    def test_isfile(self) -> None:
        with mock.patch("pathlib.Path.is_file") as mock_isfile:
            mock_isfile.return_value = True
            result = list(utils.list_path("/a/b/lorem.mscx"))
            assert str(result[0]) == "/a/b/lorem.mscx"

    def test_isfile_no_match(self) -> None:
        with mock.patch("pathlib.Path.is_file") as mock_isfile:
            mock_isfile.return_value = True
            result = list(utils.list_path("/a/b/lorem.lol"))
            assert result == []

    def test_arg_glob_txt(self) -> None:
        result: list[str] = self._list_scores("/test", glob="*.txt")
        assert str(result[0]) == "/a/b/sit.txt"

    def test_arg_glob_lol(self) -> None:
        result: list[str] = self._list_scores("/test", glob="*.lol")
        assert result == []

    def test_function_list_zero_alphabet(self) -> None:
        result: list[str] = utils.list_zero_alphabet()
        assert result[0] == "0"
        assert result[26] == "z"


class TestFunctionGetMscoreBin:
    @mock.patch("mscxyz.utils.get_args")
    @mock.patch("platform.system")
    @mock.patch("os.path.exists")
    @mock.patch("subprocess.check_output")
    def test_output(
        self,
        check_output: mock.Mock,
        exists: mock.Mock,
        system: mock.Mock,
        get_args: mock.Mock,
    ) -> None:
        get_args.return_value = args
        system.return_value = "Linux"
        exists.return_value = True
        path = bytes("/usr/local/bin/mscore\n".encode("utf-8"))
        check_output.return_value = path
        output = utils.get_musescore_bin()
        assert output == "/usr/local/bin/mscore"


class TestFunctionMscore:
    @mock.patch("mscxyz.utils.get_musescore_bin")
    @mock.patch("subprocess.Popen")
    def test_function(self, popen: mock.Mock, get_mscore_bin: mock.Mock) -> None:
        get_mscore_bin.return_value = "/bin/mscore"
        popen.return_value = mock.MagicMock(returncode=0)
        result = utils.execute_musescore(["--export-to", "troll.mscz", "lol.mscx"])
        assert result.returncode == 0


root = helper.get_xml_root("simple.mscz", 4)


class TestClassDimension:
    def test_exception(self) -> None:
        with pytest.raises(ValueError):
            Dimension("1")
        with pytest.raises(ValueError):
            Dimension("1xx")

    def test_input_mm_in(self) -> None:
        assert Dimension("1mm").to("in") == 0.03937007874015748

    def test_input_in_in(self) -> None:
        assert Dimension("1in").to("in") == 1

    def test_input_mm_mm(self) -> None:
        assert Dimension("1mm").to("mm") == 1

    def test_input_in_mm(self) -> None:
        assert Dimension("1in").to("mm") == 25.4


class TestClassPathChanger:
    path = PathChanger("test.MSCZ")

    def test_property_extension(self) -> None:
        assert self.path.extension == "mscz"

    def test_property_base(self) -> None:
        assert str(self.path.base) == "test"

    def test_method_change_extension(self) -> None:
        assert str(self.path.change_extension("mscx")) == "test.mscx"

    def test_method_add_suffix(self) -> None:
        assert str(self.path.add_suffix("bak")) == "test_bak.mscz"

    def test_method_change_suffix_extension(self) -> None:
        assert str(self.path.change(suffix="bak", extension="mp3")) == "test_bak.mp3"

    def test_method_change_suffix_only(self) -> None:
        assert str(self.path.change(suffix="bak")) == "test_bak.mscz"

    def test_method_change_extension_only(self) -> None:
        assert str(self.path.change(extension="midi")) == "test.midi"

    def test_method_change_without_arguments(self) -> None:
        assert str(self.path.change()) == "test.MSCZ"


class TestClassZipContainer:
    def setup_method(self) -> None:
        self.container = ZipContainer(
            helper.get_file("test.mscz", version=4),
        )

    def test_attribute_tmp_dir(self) -> None:
        assert str(self.container.tmp_dir).startswith(os.path.sep)
        assert self.container.tmp_dir.exists()

    def test_attribute_xml_file(self) -> None:
        assert str(self.container.xml_file).endswith(".mscx")
        assert self.container.xml_file.exists()

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
        assert container.xml_file.exists()
