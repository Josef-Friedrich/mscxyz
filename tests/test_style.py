from __future__ import annotations

from mscxyz.score import (
    MscoreStyleInterface,
    Score,
)
from tests import helper


def reload(score: Score) -> MscoreStyleInterface:
    """
    Reloads the style of the given MuseScore file.

    :param score: The MuseScore file to reload the style from.
    :return: The reloaded style.
    """
    score = Score(str(score.path))
    return score.style


def test_method_get_element_create() -> None:
    score: Score = helper.get_score("All_Dudes.mscx", version=2)
    element = score.style.get_element("x/y/z")
    element.attrib["y"] = "YYY"
    assert element.tag == "z"
    score.save()
    assert reload(score).get_element("x/y/z").attrib["y"] == "YYY"


def test_method_set_attributes() -> None:
    helper.get_score
    score = helper.get_score("All_Dudes.mscx", version=3)
    score.style.set_attributes("XXX", {"one": 1, "two": 2})
    score.save()
    assert reload(score).get_element("XXX").attrib["one"] == "1"


class TestClassStyle:
    """Test on MuseScore Version 2"""

    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("All_Dudes.mscx", version=2)

    def test_attributes_style(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_get(self) -> None:
        assert self.score.style.get_value("staffUpperBorder") == "6.5"

    def test_method_get_muliple_element_path(self) -> None:
        assert self.score.style.get_value("page-layout/page-height") == "1584"

    def test_method_get_element(self) -> None:
        assert self.score.style.get_element("voltaY").tag == "voltaY"

    def test_method_get_value(self) -> None:
        assert self.score.style.get_value("voltaY") == "-2"

    def test_method_set_value(self) -> None:
        self.score.style.set_value("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get_value("staffUpperBorder") == "99"

    def test_method_set_value_create(self) -> None:
        self.score.style.set_value("lol", "lol")
        self.score.save()
        assert reload(self.score).get_value("lol") == "lol"

    def test_method_set_value_muliple_element_path(self) -> None:
        self.score.style.set_value("page-layout/page-height", 99)
        self.score.save()
        assert reload(self.score).get_value("page-layout/page-height") == "99"

    def test_method_set_muliple_element_path_multiple_times(self) -> None:
        style = self.score.style
        style.set_value("page-layout/page-height", 99)
        style.set_value("page-layout/page-width", 100)
        style.set_value("page-layout/page-depth", 101)
        self.score.save()
        style_new = reload(self.score)
        assert style_new.get_value("page-layout/page-depth") == "101"
        assert style_new.get_value("page-layout/page-height") == "99"
        assert style_new.get_value("page-layout/page-width") == "100"

    def test_method_get_text_style(self) -> None:
        title = self.score.style.get_text_style("Title")
        assert title == {
            "halign": "center",
            "size": "28",
            "family": "MuseJazz",
            "bold": "1",
            "valign": "top",
            "name": "Title",
            "offsetType": "absolute",
        }

    def test_method_set_text_style(self) -> None:
        self.score.style.set_text_style("Title", {"size": 99})
        self.score.save()

        title = reload(self.score).get_text_style("Title")
        assert title["size"] == "99"


class TestClassMscoreStyleInterface3:
    """Test on MuseScore Version 3"""

    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("All_Dudes.mscx", version=3)

    def test_attributes_style(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_get(self) -> None:
        assert self.score.style.get_value("staffUpperBorder") == "6.5"

    def test_method_set(self) -> None:
        self.score.style.set_value("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get_value("staffUpperBorder") == "99"

    def test_method_set_create(self) -> None:
        self.score.style.set_value("lol", "lol")
        self.score.save()
        assert reload(self.score).get_value("lol") == "lol"


class TestClassMscoreStyleInterfaceWithoutTags:
    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("without-style.mscx")

    def test_load(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_set(self) -> None:
        self.score.style.set_value("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get_value("staffUpperBorder") == "99"

    def test_method_set_element_path_multiple(self) -> None:
        self.score.style.set_value("lol/troll", 99)
        self.score.save()
        assert reload(self.score).get_value("lol/troll") == "99"

    def test_method_get_text_style_unkown(self) -> None:
        unkown = self.score.style.get_text_style("Unkown")
        assert unkown == {"name": "Unkown"}

    def test_method_set_text_style_unkown(self) -> None:
        self.score.style.set_text_style("Unkown", {"size": 99})
        self.score.save()
        unkown = reload(self.score).get_text_style("Unkown")
        assert unkown["size"] == "99"


def test_method_merge_style() -> None:
    score = helper.get_score("simple.mscx")
    styles = """
        <TextStyle>
            <halign>center</halign>
            <valign>bottom</valign>
            <xoffset>0</xoffset>
            <yoffset>-1</yoffset>
            <offsetType>spatium</offsetType>
            <name>Form Section</name>
            <family>Alegreya Sans</family>
            <size>12</size>
            <bold>1</bold>
            <italic>1</italic>
            <sizeIsSpatiumDependent>1</sizeIsSpatiumDependent>
            <frameWidthS>0.1</frameWidthS>
            <paddingWidthS>0.2</paddingWidthS>
            <frameRound>0</frameRound>
            <frameColor r="0" g="0" b="0" a="255"/>
            </TextStyle>
    """
    score.clean()
    score.style.merge(styles)

    result = score.xml_tree.find("Score/Style")
    assert result is not None
    assert result[0][0].tag == "halign"
    assert result[0][0].text == "center"
