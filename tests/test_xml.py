"""Test module “xml.py”."""

from __future__ import annotations

import pytest

from mscxyz.xml import find_safe, xpath, xpath_safe, xpathall, xpathall_safe
from tests import helper

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
