"""Test submodule “utils.py”."""
from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import utils
from mscxyz.xml import Xml
from tests import helper

xml_file = helper.get_file("simple.mscx", 4)

root = helper.get_xml_root("score.mscz", 4)

xml = Xml.new(xml_file)


@pytest.fixture
def custom_xml() -> Xml:
    return Xml(Xml.parse_string("<root><a><b/><c/></a><d>some text<e/></d></root>"))


def test_read() -> None:
    element = xml.parse_file(xml_file)
    assert element.tag == "museScore"


def test_from_file() -> None:
    x = xml.new(xml_file)
    assert x.root.tag == "museScore"


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


def test_xml_write(tmp_path: Path) -> None:
    dest = tmp_path / "test.xml"
    element = Xml.parse_string("<root><a><b/><c/></a><d><e/></d></root>")
    xml.write(dest, element)
    result: str = utils.read_file(dest)
    assert result == (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<root><a><b/><c/></a><d><e/></d></root>\n"
    )


class TestRemove:
    def test_element_with_childs(self, custom_xml: Xml) -> None:
        assert (
            "<root><d>some text<e/></d></root>"
            in custom_xml.remove_tags("a").tostring()
        )

    def test_dot_double_slash_notation(self, custom_xml: Xml) -> None:
        assert (
            "<root><d>some text<e/></d></root>"
            in custom_xml.remove_tags(".//a").tostring()
        )

    def test_double_slash_notation(self, custom_xml: Xml) -> None:
        with pytest.raises(SyntaxError):
            custom_xml.remove_tags("//b")

    def test_childs(self, custom_xml: Xml) -> None:
        assert (
            "<root><a/><d>some text<e/></d></root>"
            in custom_xml.remove_tags(".//b", ".//c").tostring()
        )

    def test_with_text(self, custom_xml: Xml) -> None:
        assert (
            "<root><a><b/><c/></a></root>" in custom_xml.remove_tags(".//d").tostring()
        )

    def test_navigate_in_tree(self, custom_xml: Xml) -> None:
        assert "<root><a><c/></a>" in custom_xml.remove_tags("./a/b").tostring()


class TestStripTags:
    def test_element_with_childs(self, custom_xml: Xml) -> None:
        custom_xml.strip_tags("a")
        assert "<root><b/><c/><d>some text<e/></d></root>" in custom_xml.tostring()

    def test_child_element(self, custom_xml: Xml) -> None:
        custom_xml.strip_tags("b", "c", "d")
        assert "<root><a/>some text<e/></root>" in custom_xml.tostring()

    def test_containing_text(self, custom_xml: Xml) -> None:
        custom_xml.strip_tags("d")
        assert "<root><a><b/><c/></a>some text<e/></root>" in custom_xml.tostring()
