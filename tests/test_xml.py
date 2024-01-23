"""Test submodule “utils.py”."""
from __future__ import annotations


from pathlib import Path


import pytest

from mscxyz import utils
from mscxyz.xml import Xml

from tests import helper


xml_file = helper.get_file("simple.mscx", 4)

root = helper.get_xml_root("score.mscz", 4)

xml = Xml.from_file(xml_file)


def test_read() -> None:
    element = xml.read(xml_file)
    assert element.tag == "museScore"


def test_from_file() -> None:
    x = xml.from_file(xml_file)
    assert x.element.tag == "museScore"


def test_find_safe() -> None:
    element = xml.find_safe(".//Score")
    assert element.tag == "Score"


def test_xpath() -> None:
    element = xml.xpath(".//xxxxxxx")
    assert element is None


class TestXpathSave:
    def test_xpath_safe(self) -> None:
        element = xml.xpath_safe(".//Score")
        assert element.tag == "Score"

    def test_xpath_safe_raise(self) -> None:
        with pytest.raises(ValueError) as e:
            xml.xpath_safe(".//metaTag")
        assert "XPath “.//metaTag” found more than one element in" in e.value.args[0]


def test_xpathall() -> None:
    element = xml.xpathall(".//xxxxxxx")
    assert element is None


def test_xpathall_safe() -> None:
    element = xml.xpathall_safe(".//metaTag")
    assert isinstance(element, list)
    assert len(element) == 16


def test_write(tmp_path: Path) -> None:
    dest = tmp_path / "test.xml"
    element = Xml.parse("<root><a><b/><c/></a><d><e/></d></root>")
    xml.write(dest, element)
    result: str = utils.read_file(dest)
    assert result == (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<root><a><b/><c/></a><d><e/></d></root>\n"
    )
