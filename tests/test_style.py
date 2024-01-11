from __future__ import annotations

from typing import Literal

import pytest
from pytest import CaptureFixture

import mscxyz
from mscxyz.score import Score
from mscxyz.style import Style
from tests import helper


def reload(score: Score) -> Style:
    """
    Reloads the style of the given MuseScore file.

    :param score: The MuseScore file to reload the style from.
    :return: The reloaded style.
    """
    score = Score(str(score.path))
    return score.style


def test_method_get_element_create() -> None:
    style: Style = helper.get_style("All_Dudes.mscx", version=2)
    element = style.get_element("x/y/z")
    element.attrib["y"] = "YYY"
    assert element.tag == "z"
    assert style.reload(save=True).get_element("x/y/z").attrib["y"] == "YYY"


def test_method_set_attributes() -> None:
    style: Style = helper.get_style("All_Dudes.mscx", version=3)
    style.set_attributes("XXX", {"one": 1, "two": 2})
    assert style.reload(save=True).get_element("XXX").attrib["one"] == "1"


class TestClassStyle:
    """Test on MuseScore Version 2"""

    style: Style

    def setup_method(self) -> None:
        self.style = helper.get_style("All_Dudes.mscx", version=2)

    def test_attributes_style(self) -> None:
        assert self.style.parent_element.tag == "Style"

    def test_method_get(self) -> None:
        assert self.style.get("staffUpperBorder") == "6.5"

    def test_method_get_muliple_element_path(self) -> None:
        assert self.style.get("page-layout/page-height") == "1584"

    def test_method_get_element(self) -> None:
        assert self.style.get_element("voltaY").tag == "voltaY"

    def test_method_get_value(self) -> None:
        assert self.style.get("voltaY") == "-2"

    def test_method_set_value(self) -> None:
        self.style.set("staffUpperBorder", 99)
        assert self.style.reload(save=True).get("staffUpperBorder") == "99"

    def test_method_set_value_create(self) -> None:
        response = self.style.set("lol", "lol")
        assert response == [("lol", None, "lol")]
        assert self.style.reload(save=True).get("lol") == "lol"

    def test_method_set_value_muliple_element_path(self) -> None:
        response = self.style.set("page-layout/page-height", 99)
        assert response == [("page-layout/page-height", "1584", 99)]
        assert self.style.reload(save=True).get("page-layout/page-height") == "99"

    def test_method_set_muliple_element_path_multiple_times(self) -> None:
        self.style.set("page-layout/page-height", 99)
        self.style.set("page-layout/page-width", 100)
        self.style.set("page-layout/page-depth", 101)
        style_new = self.style.reload(save=True)
        assert style_new.get("page-layout/page-depth") == "101"
        assert style_new.get("page-layout/page-height") == "99"
        assert style_new.get("page-layout/page-width") == "100"

    def test_method_set_value_mulitple_style_names(self) -> None:
        response = self.style.set(["staffUpperBorder", "staffLowerBorder"], 42)
        assert response == [
            ("staffUpperBorder", "6.5", 42),
            ("staffLowerBorder", "6", 42),
        ]

        style_new = self.style.reload(save=True)
        assert style_new.get("staffUpperBorder") == "42"
        assert style_new.get("staffLowerBorder") == "42"

    def test_method_get_text_style(self) -> None:
        title = self.style.get_text_style("Title")
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
        self.style.set_text_style("Title", {"size": 99})
        title = self.style.reload(save=True).get_text_style("Title")
        assert title["size"] == "99"


@pytest.mark.parametrize(
    "version,expected",
    (
        (2, None),
        (3, None),
        (4, "Leland"),
    ),
)
def test_property_get_musical_symbols_font(version: int, expected: str) -> None:
    style = helper.get_style("score.mscz", version)
    assert style.musical_symbol_font == expected


@pytest.mark.parametrize("version", mscxyz.supported_versions)
def test_property_set_musical_symbol_font(version: int) -> None:
    style = helper.get_style("score.mscz", version)
    style.set_musical_symbol_fonts("Test Font")
    assert style.reload(save=True).musical_symbol_font == "Test Font"


@pytest.mark.parametrize(
    "version,expected",
    (
        (2, None),
        (3, None),
        (4, "Leland Text"),
    ),
)
def test_property_get_musical_text_font(
    version: Literal[2, 3, 4], expected: str | None
) -> None:
    style = helper.get_style("score.mscz", version)
    assert style.musical_text_font == expected


@pytest.mark.parametrize("version", mscxyz.supported_versions)
def test_property_set_musical_text_font(version: int) -> None:
    style = helper.get_style("score.mscz", version)
    style.set_musical_text_font("Test Font")
    assert style.reload(save=True).musical_text_font == "Test Font"


class TestVersion3:
    """Test on MuseScore Version 3"""

    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("All_Dudes.mscx", version=3)

    def test_attributes_style(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_get(self) -> None:
        assert self.score.style.get("staffUpperBorder") == "6.5"

    def test_method_set(self) -> None:
        self.score.style.set("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get("staffUpperBorder") == "99"

    def test_method_set_create(self) -> None:
        self.score.style.set("lol", "lol")
        self.score.save()
        assert reload(self.score).get("lol") == "lol"


class TestVersion4:
    """Test on MuseScore Version 4"""

    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("All_Dudes.mscz", version=4)

    def test_attributes_style(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_get(self) -> None:
        assert self.score.style.get("staffUpperBorder") == "6.5"

    def test_method_set(self) -> None:
        self.score.style.set("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get("staffUpperBorder") == "99"

    def test_method_set_create(self) -> None:
        self.score.style.set("lol", "lol")
        self.score.save()
        assert reload(self.score).get("lol") == "lol"


class TestClassStyleWithoutTags:
    score: Score

    def setup_method(self) -> None:
        self.score = helper.get_score("without-style.mscx")

    def test_load(self) -> None:
        assert self.score.style.parent_element.tag == "Style"

    def test_method_set(self) -> None:
        self.score.style.set("staffUpperBorder", 99)
        self.score.save()
        assert reload(self.score).get("staffUpperBorder") == "99"

    def test_method_set_element_path_multiple(self) -> None:
        self.score.style.set("lol/troll", 99)
        self.score.save()
        assert reload(self.score).get("lol/troll") == "99"

    def test_method_get_text_style_unkown(self) -> None:
        unkown = self.score.style.get_text_style("Unkown")
        assert unkown == {"name": "Unkown"}

    def test_method_set_text_style_unkown(self) -> None:
        self.score.style.set_text_style("Unkown", {"size": 99})
        self.score.save()
        unkown = reload(self.score).get_text_style("Unkown")
        assert unkown["size"] == "99"


@pytest.mark.parametrize(
    "styles",
    (
        "<pageWidth>8.27</pageWidth>",
        """<?xml version="1.0"?>
    <museScore version="2.06">
        <Style>
            <pageWidth>8.27</pageWidth>
        </Style>
    </museScore>
    """,
    ),
)
def test_method_set_all(styles: str) -> None:
    style = helper.get_style("simple.mscx")
    style.load_styles_as_string(styles)
    result = style.score.xml_root.find("Score/Style")
    assert result is not None
    assert result[0].tag == "pageWidth"
    assert result[0].text == "8.27"


def test_load_style_file() -> None:
    score = helper.get_score("simple.mscx")
    score.clean()
    style = helper.get_file("style.mss", 2)
    score.style.load_style_file(style)

    result = score.xml_root.find("Score/Style")
    assert result is not None
    assert result[0].text == "77"


class TestCli:
    def test_option_styles_v3(self, capsys: CaptureFixture[str]) -> None:
        stdout = helper.stdout("--styles-v3")
        assert "user12FrameFgColor" in stdout
        assert "instrumentNameOffset" not in stdout

    def test_option_styles_v4(self) -> None:
        assert "instrumentNameOffset" in helper.stdout("--styles-v4")

    def test_option_list_fonts(self, score: Score) -> None:
        stdout = helper.stdout("--list-fonts", str(score.path))
        assert "harpPedalTextDiagramFontFace: Edwin" in stdout
