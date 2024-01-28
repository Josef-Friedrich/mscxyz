from __future__ import annotations

from typing import Literal

import pytest

import mscxyz
from mscxyz.score import Score
from mscxyz.style import Style
from tests import helper
from tests.helper import Cli


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

    def test_method_clean(self) -> None:
        score = helper.get_score("clean.mscx", version=3)
        score.style.clean()
        score.save()
        score = Score(str(score.path))
        xml_tree = score.xml_root
        assert xml_tree.xpath("/museScore/Score/Style") == []
        assert xml_tree.xpath("//LayoutBreak") == []
        assert xml_tree.xpath("//StemDirection") == []
        assert xml_tree.xpath("//font") == []
        assert xml_tree.xpath("//b") == []
        assert xml_tree.xpath("//i") == []
        assert xml_tree.xpath("//pos") == []
        assert xml_tree.xpath("//offset") == []

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

    def test_property_odd_even_header_left_center_right(self) -> None:
        # even
        assert self.style.even_header_left == "$p"
        self.style.even_header_left = "even_header_left"
        assert self.style.even_header_left == "even_header_left"

        self.style.even_header_center = "even_header_center"
        assert self.style.even_header_center == "even_header_center"

        self.style.even_header_right = "even_header_right"
        assert self.style.even_header_right == "even_header_right"

        # odd
        self.style.odd_header_left = "odd_header_left"
        assert self.style.odd_header_left == "odd_header_left"

        self.style.odd_header_center = "odd_header_center"
        assert self.style.odd_header_center == "odd_header_center"

        assert self.style.odd_header_right == "$p"
        self.style.odd_header_right = "odd_header_right"
        assert self.style.odd_header_right == "odd_header_right"

    def test_property_odd_even_footer_left_center_right(self) -> None:
        # even
        self.style.even_footer_left = "even_footer_left"
        assert self.style.even_footer_left == "even_footer_left"

        assert self.style.even_footer_center == "$C"
        self.style.even_footer_center = "even_footer_center"
        assert self.style.even_footer_center == "even_footer_center"

        self.style.even_footer_right = "even_footer_right"
        assert self.style.even_footer_right == "even_footer_right"

        # odd
        self.style.odd_footer_left = "odd_footer_left"
        assert self.style.odd_footer_left == "odd_footer_left"

        assert self.style.odd_footer_center == "$C"
        self.style.odd_footer_center = "odd_footer_center"
        assert self.style.odd_footer_center == "odd_footer_center"

        self.style.odd_footer_right = "odd_footer_right"
        assert self.style.odd_footer_right == "odd_footer_right"


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
    with pytest.raises(ValueError):
        style.musical_symbol_font = "Test Font"
    style.musical_symbol_font = "Gonville"
    assert style.reload(save=True).musical_symbol_font == "Gonville"


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
    with pytest.raises(ValueError):
        style.musical_text_font = "Test Font"
    style.musical_text_font = "Gonville Text"
    assert style.reload(save=True).musical_text_font == "Gootville Text"


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


class TestClean:
    def test_clean(self) -> None:
        c = Cli("--clean").append_score("formats.mscz").execute()

        uncleaned: str = c.pre.read_as_text()
        assert "<font" in uncleaned
        assert "<b>" in uncleaned
        assert "<i>" in uncleaned
        # assert "<pos" in uncleaned
        assert "<LayoutBreak>" in uncleaned
        assert "<StemDirection>" in uncleaned

        cleaned: str = c.post.read_as_text()
        assert "<font" not in cleaned
        assert "<b>" not in cleaned
        assert "<i>" not in cleaned
        assert "<pos" not in cleaned
        assert "<LayoutBreak>" not in cleaned
        assert "<StemDirection>" not in cleaned

    def test_clean_add_style(self) -> None:
        score = (
            Cli("--clean", "--style-file", helper.get_file("Jazz.mss", 4))
            .append_score("score.mscz")
            .score()
        )
        assert "<musicalSymbolFont>MuseJazz</musicalSymbolFont>" in score.read_as_text()


def test_load_style_file() -> None:
    score = helper.get_score("simple.mscx")
    score.style.clean()
    style = helper.get_file("style.mss", 2)
    score.style.load_style_file(style)

    result = score.xml_root.find("Score/Style")
    assert result is not None
    assert result[0].text == "77"


class TestCli:
    def test_option_style_file(self, score: Score) -> None:
        c = Cli("--style-file", helper.get_file("Jazz.mss", 4), score).execute()
        assert c.pre.style.musical_symbol_font == "Leland"
        assert c.post.style.musical_symbol_font == "MuseJazz"

    def test_option_styles_v3(self) -> None:
        stdout = Cli("--styles-v3").stdout()
        assert "user12FrameFgColor" in stdout
        assert "instrumentNameOffset" not in stdout

    def test_option_styles_v4(self) -> None:
        assert "instrumentNameOffset" in Cli("--styles-v4").stdout()

    def test_option_list_fonts(self) -> None:
        assert "harpPedalTextDiagramFontFace: Edwin" in Cli("--list-fonts").stdout()

    def test_option_staff_space(self) -> None:
        c = Cli("--staff-space", "1in").execute()
        assert c.pre.style.staff_space == 1.7639
        assert c.post.style.staff_space == 25.4

    def test_option_page_size(self) -> None:
        score: Score = Cli("--page-size", "150mm", "100mm").score()
        assert score.style.page_width == 5.9055
        assert score.style.page_height == 3.9370

    def test_option_page_size_a4(self) -> None:
        score: Score = Cli("--a4").score()
        # 8.27 in × 11.7 in ?
        assert score.style.page_width == 8.27
        assert score.style.page_height == 11.69

    def test_option_page_size_letter(self) -> None:
        score: Score = Cli("--letter").score()
        assert score.style.page_width == 8.5
        assert score.style.page_height == 11.0

    def test_option_margin(self) -> None:
        score = Cli("--margin", "30mm").score()
        s = score.style

        assert s.margin == 1.1811

        assert s.page_even_top_margin == 1.1811
        assert s.page_odd_top_margin == 1.1811
        assert s.page_even_right_margin == 1.1811
        assert s.page_odd_right_margin == 1.1811
        assert s.page_even_bottom_margin == 1.1811
        assert s.page_odd_bottom_margin == 1.1811
        assert s.page_even_left_margin == 1.1811
        assert s.page_odd_left_margin == 1.1811

    def test_option_header(self) -> None:
        c = Cli("--header").execute()
        assert not c.pre.style.show_header
        assert c.post.style.show_header

        c = Cli("--no-header", c.score()).execute()
        assert c.pre.style.show_header
        assert not c.post.style.show_header

    def test_option_footer(self) -> None:
        c = Cli("--footer").execute()
        assert c.pre.style.show_footer
        assert c.post.style.show_footer

        c = Cli("--no-footer", c.score()).execute()
        assert c.pre.style.show_footer
        assert not c.post.style.show_footer


class TestProperties:
    def test_measure_number_offset(self, score: Score) -> None:
        assert score.style.measure_number_offset == {"x": "0", "y": "-2"}
        score.style.measure_number_offset = {"x": 1.2, "y": 3.0}
        assert score.style.measure_number_offset == {"x": "1.2", "y": "3.0"}
