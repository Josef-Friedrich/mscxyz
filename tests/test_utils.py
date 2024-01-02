"""Test submodule “utils.py”."""
from __future__ import annotations

from typing import Optional
from unittest import mock

import pytest

import mscxyz
from mscxyz.utils import (
    find_safe,
    get_args,
    get_mscore_bin,
    list_scores,
    list_zero_alphabet,
    mscore,
    xpath,
    xpath_safe,
    xpathall,
    xpathall_safe,
)
from tests import helper

args = get_args()
args.general_executable = None


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
        output = get_mscore_bin()
        assert output == "/usr/local/bin/mscore"


class TestFunctionMscore:
    @mock.patch("mscxyz.utils.get_mscore_bin")
    @mock.patch("subprocess.Popen")
    def test_function(self, popen: mock.Mock, get_mscore_bin: mock.Mock) -> None:
        get_mscore_bin.return_value = "/bin/mscore"
        popen.return_value = mock.MagicMock(returncode=0)
        result = mscore(["--export-to", "troll.mscz", "lol.mscx"])
        assert result.returncode == 0


tree = helper.get_xml_tree("simple.mscz", 4)

root = tree.getroot()


def test_find_safe():
    element = find_safe(root, ".//Score")
    assert element.tag == "Score"


def test_xpath():
    element = xpath(root, ".//xxxxxxx")
    assert element is None


class TestXpathSave:
    def test_xpath_safe(self):
        element = xpath_safe(root, ".//Score")
        assert element.tag == "Score"

    def test_xpath_safe_raise(self):
        with pytest.raises(ValueError) as e:
            xpath_safe(root, ".//metaTag")
        assert "XPath “.//metaTag” found more than one element in" in e.value.args[0]


def test_xpathall():
    element = xpathall(root, ".//xxxxxxx")
    assert element is None


def test_xpathall_safe():
    element = xpathall_safe(root, ".//metaTag")
    assert isinstance(element, list)
    assert len(element) == 16
