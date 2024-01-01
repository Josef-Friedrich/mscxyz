"""Test module “xml.py”."""

from __future__ import annotations

from mscxyz.xml import iter
from tests import helper


class TestFunctionIterElements:
    tree = helper.get_xml_tree("simple.mscz", 4)

    def test_path(self):
        for item in iter(self.tree.getroot(), path=".//Score"):
            assert item.tag == "Score"

    def test_args_general(self):
        for item in iter(self.tree.getroot(), path=".//Score"):
            assert item.tag == "Score"
