"""Test submodule “utils.py”."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import utils
from mscxyz.xml import XmlManipulator
from tests import helper

xml_file = helper.get_file("simple.mscx", 4)

root = helper.get_xml_root("score.mscz", 4)

xml = XmlManipulator(file_path=xml_file)


@pytest.fixture
def custom_xml() -> XmlManipulator:
    return XmlManipulator(
        XmlManipulator.parse_string("<root><a><b/><c/></a><d>some text<e/></d></root>")
    )


class TestConstructor:
    def test_without_argument(self) -> None:
        assert "<root/>" in XmlManipulator().tostring()

    def test_argument_element(self) -> None:
        assert (
            XmlManipulator(element=xml.create_element("RootElement")).root.tag
            == "RootElement"
        )

    def test_argument_file_path(self) -> None:
        assert XmlManipulator(file_path=xml_file).root.tag == "museScore"

    def test_argument_xml_markup(self) -> None:
        assert XmlManipulator(xml_markup="<a><b><c></c></b></a>").root.tag == "a"


# Crud: Create #################################################################


def test_method_parse_file() -> None:
    assert xml.parse_file(xml_file).tag == "museScore"


def test_method__write(tmp_path: Path) -> None:
    dest = tmp_path / "test.xml"
    element = XmlManipulator.parse_string("<root><a><b/><c/></a><d><e/></d></root>")
    xml.write(dest, element)
    result: str = utils.read_file(dest)
    assert result == (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<root><a><b/><c/></a><d><e/></d></root>\n"
    )


def test_method_create_sub_element() -> None:
    element, _ = xml.create_sub_element("parent", "child", "test")
    assert "<parent><child>test</child></parent>" in xml.tostring(element)


# cRud: Read ###################################################################


def test_method_find_safe() -> None:
    assert xml.find_safe(".//Score").tag == "Score"


def test_method_xpath() -> None:
    assert xml.xpath(".//xxxxxxx") is None


class TestMethodXpathSave:
    def test_xpath_safe(self) -> None:
        element = xml.xpath_safe(".//Score")
        assert element.tag == "Score"

    def test_xpath_safe_raise(self) -> None:
        with pytest.raises(ValueError) as e:
            xml.xpath_safe(".//metaTag")
        assert "XPath “.//metaTag” found more than one element in" in e.value.args[0]


def test_method_xpathall() -> None:
    assert xml.xpathall(".//xxxxxxx") is None


def test_method_xpathall_safe() -> None:
    element = xml.xpathall_safe(".//metaTag")
    assert isinstance(element, list)
    assert len(element) == 16


# crUd: Update #################################################################


def test_method_set_text() -> None:
    assert "<root>text</root>" in XmlManipulator().set_text(".", "text").tostring()


def test_method_replace() -> None:
    x = XmlManipulator(xml_markup="<root><a><b/></a></root>")
    b = x.find_safe(".//b")
    c = x.create_element("c")
    x.replace(b, c)
    assert "<root><a><c/></a></root>" in x.tostring()


# cruD: Delete #################################################################


def test_method_remove() -> None:
    x = XmlManipulator(xml_markup="<root><a><b/></a></root>")
    b = x.find_safe(".//b")
    x.remove(b)
    assert "<root><a/></root>" in x.tostring()


class TestMethodRemoveTags:
    def test_element_with_childs(self, custom_xml: XmlManipulator) -> None:
        assert (
            "<root><d>some text<e/></d></root>"
            in custom_xml.remove_tags("a").tostring()
        )

    def test_dot_double_slash_notation(self, custom_xml: XmlManipulator) -> None:
        assert (
            "<root><d>some text<e/></d></root>"
            in custom_xml.remove_tags(".//a").tostring()
        )

    def test_double_slash_notation(self, custom_xml: XmlManipulator) -> None:
        with pytest.raises(SyntaxError):
            custom_xml.remove_tags("//b")

    def test_childs(self, custom_xml: XmlManipulator) -> None:
        assert (
            "<root><a/><d>some text<e/></d></root>"
            in custom_xml.remove_tags(".//b", ".//c").tostring()
        )

    def test_with_text(self, custom_xml: XmlManipulator) -> None:
        assert (
            "<root><a><b/><c/></a></root>" in custom_xml.remove_tags(".//d").tostring()
        )

    def test_navigate_in_tree(self, custom_xml: XmlManipulator) -> None:
        assert "<root><a><c/></a>" in custom_xml.remove_tags("./a/b").tostring()
