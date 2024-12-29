from __future__ import annotations

import typing
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, Sequence, TypedDict, Union, cast

from lxml.etree import _Attrib, _Element

from mscxyz import utils
from mscxyz.utils import INCH
from mscxyz.xml import XmlManipulator

if typing.TYPE_CHECKING:
    from mscxyz.score import Score

from mscxyz.utils import Dimension


def mm(value: str | float) -> float:
    if not isinstance(value, str):
        return value
    return Dimension(value).to("mm")


def inch(value: str | float) -> float:
    if not isinstance(value, str):
        return value
    return Dimension(value).to("in")


musical_symbol_font_faces = (
    "Leland",
    "Bravura",
    "Emmentaler",
    # "MScore",
    "Gonville",
    # "Gootville",
    "MuseJazz",
    "Petaluma",
    "Finale Maestro",
    "Finale Broadway",
)
"""
Musical symbol font faces

:see: `MuseScore C++ source code: engravingmodule.cpp lines 120-127 <https://github.com/musescore/MuseScore/blob/940f5ce4c83c9168e3be0e1509664a7abffcf9e8/src/engraving/engravingmodule.cpp#L120-L127>`_
"""

musical_text_font_faces = (
    "Leland Text",
    "Bravura Text",
    "Emmentaler Text",  # -> MScore Text
    # "MScore Text",
    "Gonville Text",  # -> Gootville Text
    # "Gootville Text",
    "MuseJazz Text",
    "Petaluma Text",
    "Finale Maestro Text",
    "Finale Broadway Text",
)
"""
Musical text font faces

:see: `MuseScore C++ source code: editstyle.cpp lines 1966-1973 <https://github.com/musescore/MuseScore/blob/940f5ce4c83c9168e3be0e1509664a7abffcf9e8/src/notation/view/widgets/editstyle.cpp#L1966-L1973>`_
"""


text_font_faces = (
    "lyricsOddFontFace",
    "lyricsEvenFontFace",
    "hairpinFontFace",
    "pedalFontFace",
    "chordSymbolAFontFace",
    "chordSymbolBFontFace",
    # "romanNumeralFontFace", # **Campania**
    "nashvilleNumberFontFace",
    "voltaFontFace",
    "ottavaFontFace",
    "tupletFontFace",
    "defaultFontFace",
    "titleFontFace",
    "subTitleFontFace",
    "composerFontFace",
    "lyricistFontFace",
    "fingeringFontFace",
    "lhGuitarFingeringFontFace",
    "rhGuitarFingeringFontFace",
    "stringNumberFontFace",
    "harpPedalDiagramFontFace",
    "harpPedalTextDiagramFontFace",
    "longInstrumentFontFace",
    "shortInstrumentFontFace",
    "partInstrumentFontFace",
    # "dynamicsFontFace",
    "expressionFontFace",
    "tempoFontFace",
    "tempoChangeFontFace",
    "metronomeFontFace",
    "measureNumberFontFace",
    "mmRestRangeFontFace",
    "translatorFontFace",
    "systemFontFace",
    "staffFontFace",
    "rehearsalMarkFontFace",
    "repeatLeftFontFace",
    "repeatRightFontFace",
    "frameFontFace",
    "textLineFontFace",
    "systemTextLineFontFace",
    "glissandoFontFace",
    "bendFontFace",
    "headerFontFace",
    "footerFontFace",
    "instrumentChangeFontFace",
    "stickingFontFace",
    # "figuredBassFontFace", # **MScoreBC**
    "user1FontFace",
    "user2FontFace",
    "user3FontFace",
    "user4FontFace",
    "user5FontFace",
    "user6FontFace",
    "user7FontFace",
    "user8FontFace",
    "user9FontFace",
    "user10FontFace",
    "user11FontFace",
    "user12FontFace",
    "letRingFontFace",
    "palmMuteFontFace",
)

PrimitiveValue = Union[str, int, float]

StyleValue = Optional[Union[PrimitiveValue, dict[str, PrimitiveValue]]]

StyleChange = tuple[str, StyleValue, StyleValue]

StyleChanges = list[StyleChange]

AttibutesDict = dict[str, PrimitiveValue]

Offset = TypedDict("Offset", {"x": Union[float, str], "y": Union[float, str]})


@dataclass
class Margin:
    even_top: float
    odd_top: float
    even_right: float
    odd_right: float
    even_bottom: float
    odd_bottom: float
    even_left: float
    odd_left: float


class Style:
    """
    Interface specialized for the style manipulation.

    :param relpath: The relative (or absolute) path of a MuseScore file.

    v3: https://github.com/musescore/MuseScore/blob/4566605d92467b0f5a36b3731b64150500e48583/libmscore/style.cpp

    v4: https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp
    """

    score: "Score"

    parent_element: _Element
    """The parent ``/museScore/Score/Style`` element that contains all style tags.
    """

    @property
    def xml(self) -> XmlManipulator:
        return self.score.xml

    def __init__(self, score: "Score") -> None:
        self.score = score
        parent_element = self.__get_parent_element()
        if self.score.style_file:
            self.parent_element = self.xml.find_safe(
                "Style",
                self.xml.parse_file(self.score.style_file),
            )
            self.xml.replace(parent_element, self.parent_element)
        else:
            self.parent_element = parent_element

    def __get_parent_element(self) -> _Element:
        """
        Get the parent style element. The element is created if it doesn’t exists.

        :return: The created parent style element.
        """
        parent_element = self.xml.find("Score/Style")
        if parent_element is not None:
            return parent_element
        score: _Element | None = self.xml.find("Score")
        if score is None:
            raise ValueError("The score file has no <Score> tag.")
        _, sub_element = self.xml.create_sub_element(score, "Style")
        return sub_element

    def __create_nested_element(self, tag: str) -> _Element:
        """
        Create a nested XML element based on the given tag.

        :param tag: The tag for the nested element. Nested tags are supported, for example `TextStyle/halign`.

        :return: The created nested element.
        """
        tags: list[str] = tag.split("/")
        parent: _Element = self.parent_element
        for tag in tags:
            element: _Element | None = parent.find(tag)
            if element is None:
                _, parent = self.xml.create_sub_element(parent, tag)
            else:
                parent = element
        return parent

    @property
    def styles(self) -> list[_Element]:
        """
        Return all style elements (all XML elements inside the ``<Style>``) as a list.

        :return: A list of all style elements.
        """
        output: list[_Element] = []
        for element in self.parent_element:
            output.append(element)
        return output

    def get_element(self, element_path: str) -> _Element:
        """
        Determines an lxml element that is a child to the ``Style`` tag

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        :param create: Create the element if not present in the parent
          ``Style`` tag.

        Example code:

        .. code:: Python

            # Set attributes on a maybe non-existent style tag.
            # <measureNumberOffset x="0.5" y="-2"/>
            test = Style('text.mscx')
            element = test.get_element('measureNumberOffset')
            element.attrib['x'] = '0.5'
            element.attrib['y'] = '-2'
            test.save()
        """
        element: _Element | None = self.parent_element.find(element_path)
        if element is None:
            element = self.__create_nested_element(element_path)
        return element

    def __get_float(self, style_name: str) -> float | None:
        value: str | None = self.get(style_name, raise_exception=False)
        if value is not None:
            return utils.round_float(value)
        return None

    def __get_float_default(self, style_name: str, default: float) -> float:
        value: float | None = self.__get_float(style_name)
        if value is not None:
            return value
        return default

    def __get_bool(self, style_name: str) -> bool | None:
        value: str | None = self.get(style_name, raise_exception=False)
        if value is not None:
            return value == "1"
        return None

    def __get_bool_default(self, style_name: str, default: bool) -> bool:
        value: bool | None = self.__get_bool(style_name)
        if value is not None:
            return value
        return default

    def __get_str_default(self, style_name: str, default: str) -> str:
        value: str | None = self.get(style_name, raise_exception=False)
        if value is not None:
            return value
        return default

    def __get_attributes(self, style_name: str) -> _Attrib:
        element: _Element = self.get_element(style_name)
        return element.attrib

    def clean(self) -> None:
        """Remove the style, the layout breaks, the stem directions and the
        ``font``, ``b``, ``i``, ``pos``, ``offset`` tags"""
        self.xml.remove_tags(
            ".//LayoutBreak",
            ".//StemDirection",
            ".//font",
            ".//b",
            ".//i",
            ".//pos",
            ".//offset",
        )
        self.parent_element.clear()

    def get(self, style_name: str, raise_exception: bool = True) -> str | None:
        """
        Get a style value by its style name (element path) of a style tag.

        :param style_name: see
          http://lxml.de/tutorial.html#elementpath
        """
        element: _Element = self.get_element(style_name)
        if element.text is None:
            if raise_exception:
                raise ValueError(f"Element {element} has no text!")
            return None
        else:
            return element.text

    def set_attributes(self, style_name: str, attributes: AttibutesDict) -> _Element:
        """Set attributes on a style child tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element: _Element = self.get_element(style_name)
        for name, value in attributes.items():
            element.attrib[name] = str(value)
        return element

    def set(self, style_name: str | Sequence[str], value: StyleValue) -> StyleChanges:
        """
        Sets the value of an XML element identified by the given element path.

        :param style_name: A style name or multiple style names as a list or a
          element path expression. For more information, refer to
          http://lxml.de/tutorial.html#elementpath
        :param value: The value to be set for the XML element.
          It can be a string, integer, or float.
        """
        style_names: list[str] = []
        if isinstance(style_name, str):
            style_names = [style_name]
        else:
            style_names = list(style_name)

        response: StyleChanges = []
        for style_name in style_names:
            element: _Element = self.get_element(style_name)
            change: StyleChange = (
                style_name,
                self.get(style_name, raise_exception=False),
                value,
            )
            response.append(change)
            if isinstance(value, dict):
                for name, value in value.items():
                    element.attrib[name] = str(value)
            else:
                if isinstance(value, float):
                    value = utils.round_float(value)
                element.text = str(value)
        return response

    def __get_text_style_element(self, name: str) -> _Element:
        if self.score.version_major != 2:
            raise ValueError(
                "This operation is only allowed for MuseScore 2 score files"
            )

        child: _Element | None = self.xml.xpath(
            f'//TextStyle/name[contains(., "{name}")]'
        )

        if child is not None:
            el: _Element | None = child.getparent()
            if el is None:
                raise ValueError(f"Parent not found on element {el}!")
            return el
        else:
            _, el_text_style = self.xml.create_sub_element(
                self.parent_element, "TextStyle"
            )
            _, el_name = self.xml.create_sub_element(el_text_style, "name")
            el_name.text = name
            return el_text_style

    def get_text_style(self, name: str) -> dict[str, str]:
        """Get text styles as a dictonary. Only MuseScore2!

        .. code :: XML

            <Style>
                <TextStyle>
                    <halign>center</halign>
                    <valign>top</valign>
                    <offsetType>absolute</offsetType>
                    <name>Title</name>
                    <family>MuseJazz</family>
                    <size>28</size>
                    <bold>1</bold>
                </TextStyle>
            </Style>

        .. code :: Python

            {
                "halign": "center",
                "size": "28",
                "family": "MuseJazz",
                "bold": "1",
                "valign": "top",
                "name": "Title",
                "offsetType": "absolute",
            }

        :param name: The name of the text style, for example ``Title``, ``Subtitle``,
          ``Lyricist``, ``Fingering``, ``String Number``, ``Dynamics`` etc.
        """
        text_style = self.__get_text_style_element(name)
        out: dict[str, str] = {}
        for child in text_style.iterchildren():
            if child.text is not None:
                out[child.tag] = child.text
        return out

    def set_text_style(self, name: str, values: dict[str, str | int | float]) -> None:
        """Set text styles. Only MuseScore2!

        :param name: The name of the text style, for example ``Title``, ``Subtitle``,
          ``Lyricist``, ``Fingering``, ``String Number``, ``Dynamics`` etc.
        :param values: A dictionary. The keys are the tag names, values are
          the text values of the child tags, for example
          ``{size: 14, bold: 1}``.
        """
        text_style: _Element = self.__get_text_style_element(name)
        for element_name, value in values.items():
            element: _Element | None = text_style.find(element_name)
            if element is None:
                _, element = self.xml.create_sub_element(text_style, element_name)
            element.text = str(value)

    def get_all_fonts(self) -> list[tuple[str, str]]:
        """
        Returns a list of tuples containing the tag name and the font face.
        """
        output: list[tuple[str, str]] = []
        for element in self.parent_element:
            if "FontFace" in element.tag:
                output.append((element.tag, self.xml.get_text_safe(element)))
        return output

    def print_all_font_faces(self) -> None:
        for style in self.get_all_fonts():
            print(f"{style[0]}: {style[1]}")

    def set_text_fonts(self, new_font_face: str) -> StyleChanges:
        """
        Set the font face for nearly all font face related styles
        except for ``romanNumeralFontFace``, ``figuredBassFontFace``,
        ``dynamicsFontFace``, ``musicalSymbolFont`` and ``musicalTextFont``.

        Default values in v3 and v4:

        * ``lyricsOddFontFace``: Edwin
        * ``lyricsEvenFontFace``: Edwin
        * ``hairpinFontFace``: Edwin
        * ``pedalFontFace``: Edwin
        * ``chordSymbolAFontFace``: Edwin
        * ``chordSymbolBFontFace``: Edwin
        * ``romanNumeralFontFace``: **Campania**
        * ``nashvilleNumberFontFace``: Edwin
        * ``voltaFontFace``: Edwin
        * ``ottavaFontFace``: Edwin
        * ``tupletFontFace``: Edwin
        * ``defaultFontFace``: Edwin
        * ``titleFontFace``: Edwin
        * ``subTitleFontFace``: Edwin
        * ``composerFontFace``: Edwin
        * ``lyricistFontFace``: Edwin
        * ``fingeringFontFace``: Edwin
        * ``lhGuitarFingeringFontFace``: Edwin
        * ``rhGuitarFingeringFontFace``: Edwin
        * ``stringNumberFontFace``: Edwin
        * ``harpPedalDiagramFontFace``: Edwin
        * ``harpPedalTextDiagramFontFace``: Edwin
        * ``longInstrumentFontFace``: Edwin
        * ``shortInstrumentFontFace``: Edwin
        * ``partInstrumentFontFace``: Edwin
        * ``dynamicsFontFace``: **Edwin**
        * ``expressionFontFace``: Edwin
        * ``tempoFontFace``: Edwin
        * ``tempoChangeFontFace``: Edwin
        * ``metronomeFontFace``: Edwin
        * ``measureNumberFontFace``: Edwin
        * ``mmRestRangeFontFace``: Edwin
        * ``translatorFontFace``: Edwin
        * ``systemFontFace``: Edwin
        * ``staffFontFace``: Edwin
        * ``rehearsalMarkFontFace``: Edwin
        * ``repeatLeftFontFace``: Edwin
        * ``repeatRightFontFace``: Edwin
        * ``frameFontFace``: Edwin
        * ``textLineFontFace``: Edwin
        * ``systemTextLineFontFace``: Edwin
        * ``glissandoFontFace``: Edwin
        * ``bendFontFace``: Edwin
        * ``headerFontFace``: Edwin
        * ``footerFontFace``: Edwin
        * ``instrumentChangeFontFace``: Edwin
        * ``stickingFontFace``: Edwin
        * ``figuredBassFontFace``: **MScoreBC**
        * ``user1FontFace``: Edwin
        * ``user2FontFace``: Edwin
        * ``user3FontFace``: Edwin
        * ``user4FontFace``: Edwin
        * ``user5FontFace``: Edwin
        * ``user6FontFace``: Edwin
        * ``user7FontFace``: Edwin
        * ``user8FontFace``: Edwin
        * ``user9FontFace``: Edwin
        * ``user10FontFace``: Edwin
        * ``user11FontFace``: Edwin
        * ``user12FontFace``: Edwin
        * ``letRingFontFace``: Edwin
        * ``palmMuteFontFace``: Edwin

        :param font_face: The new font face to be set.

        :return: A list of tuples representing the changes made. Each tuple
          contains the tag name, the old font face, and the new font face.
        """
        return self.set(text_font_faces, new_font_face)

    def set_title_fonts(self, font_face: str) -> StyleChanges:
        return self.set(("titleFontFace", "subTitleFontFace"), font_face)

    @property
    def musical_symbol_font(self) -> str | None:
        """

        v3

        .. code :: XML

            <musicalSymbolFont>Leland</musicalSymbolFont>
            <dynamicsFontFace>Leland</dynamicsFontFace>

        v4 // OBSOLETE after version 4.1. Dynamic text now takes its setting from expression.

        .. code :: XML

            <musicalSymbolFont>Leland</musicalSymbolFont>
            <dynamicsFont>Leland</dynamicsFont>

        """
        return self.get("musicalSymbolFont", raise_exception=False)

    @musical_symbol_font.setter
    def musical_symbol_font(self, font_face: str) -> None:
        if font_face not in musical_symbol_font_faces:
            raise ValueError(
                f"Font face {font_face} is not a valid musical symbol font face. Valid values are {musical_symbol_font_faces}."
            )
        self.set(("musicalSymbolFont", "dynamicsFont", "dynamicsFontFace"), font_face)

    @property
    def musical_text_font(self) -> str | None:
        """
        .. code :: XML

            <musicalTextFont>Leland Text</musicalTextFont>
        """
        return self.get("musicalTextFont", raise_exception=False)

    @musical_text_font.setter
    def musical_text_font(self, font_face: str) -> None:
        if font_face not in musical_text_font_faces:
            raise ValueError(
                f"Font face {font_face} is not a valid musical text font face. Valid values are {musical_text_font_faces}."
            )
        # https://github.com/musescore/MuseScore/blob/940f5ce4c83c9168e3be0e1509664a7abffcf9e8/src/notation/view/widgets/editstyle.cpp#L1968-L1969
        self.set(
            "musicalTextFont",
            font_face.replace("Emmentaler", "MScore").replace("Gonville", "Gootville"),
        )

    def __replace_parent_element(self, parent_style: _Element) -> None:
        self.xml.replace(self.parent_element, parent_style)
        self.parent_element = parent_style

    def load_styles_as_string(self, styles: str) -> None:
        """Load styles into the XML tree and replace the old styles.

        :param styles: A string containing the XML style markup.

        For example this inputs are valid:

        Without declaration:

        .. code :: XML

            <pageWidth>8.27</pageWidth>

        With declaration:

        .. code :: XML

            <?xml version="1.0"?>
            <museScore version="2.06">
                <Style>
                    <pageWidth>8.27</pageWidth>
        """

        if "<Style>" not in styles:
            styles = f'<?xml version="1.0"?>\n<museScore version="{self.score.version}"><Style>{styles}</Style></museScore>'

        style = self.xml.parse_string(styles)
        self.__replace_parent_element(style[0])

    def load_style_file(self, file: str | Path | TextIOWrapper) -> None:
        style: _Element = self.xml.parse_file(file)
        self.__replace_parent_element(style[0])

    def reload(self, save: bool = False) -> Style:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Style object.

        :see: :meth:`mscxyz.score.Score.reload`
        """
        return self.score.reload(save).style

    # The properties in the order they are arranged in this file: https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp

    @property
    def page_width(self) -> float:
        """
        The page width in ``inch``.

        .. code :: XML

            <pageWidth>8.5</pageWidth>

        :see: `MuseScore C++ source code: styledef.cpp line 43 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L43>`_
        """
        return self.__get_float_default("pageWidth", 210 / INCH)

    @page_width.setter
    def page_width(self, value: float) -> None:
        self.set("pageWidth", value)

    @property
    def page_height(self) -> float:
        """
        The page height in ``inch``.

        .. code :: XML

            <pageHeight>11.69</pageHeight>

        :see: `MuseScore C++ source code: styledef.cpp line 44 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L44>`_
        """
        return self.__get_float_default("pageHeight", 297 / INCH)

    @page_height.setter
    def page_height(self, value: float) -> None:
        self.set("pageHeight", value)

    def set_page_size(self, width: float | str, height: float | str) -> None:
        """
        Set the page size in ``inch``. At the same time, the
        :attr:`page_printable_width` attribute is set so that the margins do not change.

        :param width: The page width in ``inch`` as a float or a dimension string in ``mm`` or ``in``.
        :param height: The page height in ``inch`` as a float or a dimension string in ``mm`` or ``in``.

        :see: :attr:`page_width`
        :see: :attr:`page_height`
        :see: :attr:`page_printable_width`

        .. rubric:: Example

        .. code-block:: python

            score.style.set_page_size("210mm", "297mm")
            # or:
            score.style.set_page_size(8.2677165354 , 11.6929133858)
        """
        old_page_width = self.page_width
        new_page_width = inch(width)

        self.page_width = new_page_width
        self.page_height = inch(height)

        self.page_printable_width = (
            new_page_width / old_page_width * self.page_printable_width
        )

    def set_page_size_a4(self) -> None:
        """
        Set the page size to A4 (210mm x 297mm).
        """
        self.set_page_size(8.27, 11.69)

    def set_page_size_letter(self) -> None:
        """
        Set the page size to Letter (8.5in x 11in).
        """
        self.set_page_size(8.5, 11)

    # page even/odd top/right/bottom/left margin # in CSS order ################

    @property
    def page_even_top_margin(self) -> float:
        """
        The top margin of the even pages in ``inch``.

        .. code :: XML

            <pageEvenTopMargin>0.393701</pageEvenTopMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 48 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L48>`_
        """
        return self.__get_float_default("pageEvenTopMargin", 15 / INCH)

    @page_even_top_margin.setter
    def page_even_top_margin(self, value: float) -> None:
        self.set("pageEvenTopMargin", value)

    @property
    def page_odd_top_margin(self) -> float:
        """
        The top margin of the odd pages in ``inch``.

        .. code :: XML

            <pageOddTopMargin>0.393701</pageOddTopMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 50 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L50>`_
        """
        return self.__get_float_default("pageOddTopMargin", 15 / INCH)

    @page_odd_top_margin.setter
    def page_odd_top_margin(self, value: float) -> None:
        self.set("pageOddTopMargin", value)

    @property
    def page_even_right_margin(self) -> float:
        """
        The top right of the even pages in ``inch``.

        .. code :: XML

            <pageWidth>8.5</pageWidth>
            <pagePrintableWidth>7.7126</pagePrintableWidth>
            <pageEvenLeftMargin>0.393701</pageEvenLeftMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 45 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L45>`_
        """
        return utils.round_float(
            self.page_width - self.page_printable_width - self.page_even_left_margin
        )

    @page_even_right_margin.setter
    def page_even_right_margin(self, value: float) -> None:
        self.set(
            "pagePrintableWidth", self.page_width - self.page_even_left_margin - value
        )

    @property
    def page_odd_right_margin(self) -> float:
        """
        The right margin of the odd pages in ``inch``.

        .. code :: XML

            <pageWidth>8.5</pageWidth>
            <pagePrintableWidth>7.7126</pagePrintableWidth>
            <pageOddLeftMargin>0.393701</pageOddLeftMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 45 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L45>`_
        """
        return utils.round_float(
            self.page_width - self.page_printable_width - self.page_odd_left_margin
        )

    @page_odd_right_margin.setter
    def page_odd_right_margin(self, value: float) -> None:
        self.set(
            "pagePrintableWidth", self.page_width - self.page_odd_left_margin - value
        )

    @property
    def page_even_bottom_margin(self) -> float:
        """
        The bottom margin of the even pages in ``inch``.

        .. code :: XML

            <pageEvenBottomMargin>0.787403</pageEvenBottomMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 49 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L49>`_
        """
        return self.__get_float_default("pageEvenBottomMargin", 15 / INCH)

    @page_even_bottom_margin.setter
    def page_even_bottom_margin(self, value: float) -> None:
        self.set("pageEvenBottomMargin", value)

    @property
    def page_odd_bottom_margin(self) -> float:
        """
        The bottom margin of the odd pages in ``inch``.

        .. code :: XML

            <pageOddBottomMargin>0.787403</pageOddBottomMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 51 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L51>`_
        """
        return self.__get_float_default("pageOddBottomMargin", 15 / INCH)

    @page_odd_bottom_margin.setter
    def page_odd_bottom_margin(self, value: float) -> None:
        self.set("pageOddBottomMargin", value)

    @property
    def page_even_left_margin(self) -> float:
        """
        The left margin of the even pages in ``inch``.

        .. code :: XML

            <pageEvenLeftMargin>0.393701</pageEvenLeftMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 46 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L46>`_
        """
        return self.__get_float_default("pageEvenLeftMargin", 15 / INCH)

    @page_even_left_margin.setter
    def page_even_left_margin(self, value: float) -> None:
        self.set("pageEvenLeftMargin", value)

    @property
    def page_odd_left_margin(self) -> float:
        """
        The left margin of the odd pages in ``inch``.

        .. code :: XML

            <pageOddLeftMargin>0.393701</pageOddLeftMargin>

        :see: `MuseScore C++ source code: styledef.cpp line 47 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L47>`_
        """
        return self.__get_float_default("pageOddLeftMargin", 15 / INCH)

    @page_odd_left_margin.setter
    def page_odd_left_margin(self, value: float) -> None:
        self.set("pageOddLeftMargin", value)

    @property
    def page_printable_width(self) -> float:
        """
        The printable width of the page in ``inch``. This property is used to calculate the right margin.

        .. code :: XML

            <pagePrintableWidth>7.7126</pagePrintableWidth>

        :see: `MuseScore C++ source code: styledef.cpp line 45 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L45>`_
        """
        return self.__get_float_default("pagePrintableWidth", 180 / INCH)

    @page_printable_width.setter
    def page_printable_width(self, value: float) -> None:
        self.set("pagePrintableWidth", value)

    @property
    def margin(self) -> Margin | float:
        """
        The margin of a page in ``inch``.

        .. code :: XML

            <pagePrintableWidth>7.7126</pagePrintableWidth>
            <pageEvenLeftMargin>0.393701</pageEvenLeftMargin>
            <pageOddLeftMargin>0.393701</pageOddLeftMargin>
            <pageEvenTopMargin>0.393701</pageEvenTopMargin>
            <pageEvenBottomMargin>0.787403</pageEvenBottomMargin>
            <pageOddTopMargin>0.393701</pageOddTopMargin>
            <pageOddBottomMargin>0.787403</pageOddBottomMargin>

        :see: `MuseScore C++ source code: styledef.cpp lines 46-51 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L46-L51>`_
        """
        margin = Margin(
            even_top=self.page_even_top_margin,
            odd_top=self.page_odd_top_margin,
            even_right=self.page_even_right_margin,
            odd_right=self.page_odd_right_margin,
            even_bottom=self.page_even_bottom_margin,
            odd_bottom=self.page_odd_bottom_margin,
            even_left=self.page_even_top_margin,
            odd_left=self.page_odd_top_margin,
        )

        margin_single_value: float = margin.even_top
        for attr in margin.__dict__:
            if getattr(margin, attr) != margin_single_value:
                return margin
        return margin_single_value

    @margin.setter
    def margin(self, value: float) -> None:
        self.page_even_top_margin = value
        self.page_odd_top_margin = value
        self.page_even_bottom_margin = value
        self.page_odd_bottom_margin = value
        self.page_even_left_margin = value
        self.page_odd_left_margin = value

        # After page_even_left_margin and page_odd_left_margin
        self.page_even_right_margin = value
        self.page_odd_right_margin = value

    @property
    def max_system_distance(self) -> float:
        """
        The maximum system distance in ``sp`` (staff space).

        .. code :: XML

            <maxSystemDistance>15</maxSystemDistance>

        :see: `MuseScore C++ source code: styledef.cpp line 61 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L61>`_
        """
        return self.__get_float_default("maxSystemDistance", 15.0)

    @max_system_distance.setter
    def max_system_distance(self, value: float) -> None:
        self.set("maxSystemDistance", value)

    # header ###################################################################

    @property
    def show_header(self) -> bool:
        """
        Show the header on the page.

        .. code :: XML

            <showHeader>1</showHeader>

        :see: `MuseScore C++ source code: styledef.cpp line 494 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L494>`_
        """
        return self.__get_bool_default("showHeader", True)

    @show_header.setter
    def show_header(self, value: bool) -> None:
        self.set("showHeader", int(value))

    @property
    def header_first_page(self) -> bool:
        """
        Show the header on the first page.

        .. code :: XML

            <headerFirstPage>1</headerFirstPage>

        :see: `MuseScore C++ source code: styledef.cpp line 495 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L495>`_
        """
        return self.__get_bool_default("headerFirstPage", False)

    @header_first_page.setter
    def header_first_page(self, value: bool) -> None:
        self.set("headerFirstPage", int(value))

    @property
    def header_odd_even(self) -> bool:
        """
        Use different headers for odd and even pages.

        .. code :: XML

            <headerOddEven>1</headerOddEven>

        :see: `MuseScore C++ source code: styledef.cpp line 496 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L496>`_
        """
        return self.__get_bool_default("headerOddEven", True)

    @header_odd_even.setter
    def header_odd_even(self, value: bool) -> None:
        self.set("headerOddEven", int(value))

    # even/odd header l/c/r ####################################################

    @property
    def even_header_left(self) -> Optional[str]:
        """
        .. code :: XML

            <evenHeaderL>$p</evenHeaderL>

        :see: `MuseScore C++ source code: styledef.cpp line 497 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L497>`_
        """
        return self.get("evenHeaderL", False)

    @even_header_left.setter
    def even_header_left(self, value: str) -> None:
        self.set("evenHeaderL", value)

    @property
    def even_header_center(self) -> Optional[str]:
        """
        .. code :: XML

            <evenHeaderC></evenHeaderC>

        :see: `MuseScore C++ source code: styledef.cpp line 498 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L498>`_
        """
        return self.get("evenHeaderC", False)

    @even_header_center.setter
    def even_header_center(self, value: str) -> None:
        self.set("evenHeaderC", value)

    @property
    def even_header_right(self) -> Optional[str]:
        """
        .. code :: XML

            <evenHeaderR></evenHeaderR>

        :see: `MuseScore C++ source code: styledef.cpp line 499 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L499>`_
        """
        return self.get("evenHeaderR", False)

    @even_header_right.setter
    def even_header_right(self, value: str) -> None:
        self.set("evenHeaderR", value)

    @property
    def odd_header_left(self) -> Optional[str]:
        """
        .. code :: XML

            <oddHeaderL></oddHeaderL>

        :see: `MuseScore C++ source code: styledef.cpp line 500 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L500>`_
        """
        return self.get("oddHeaderL", False)

    @odd_header_left.setter
    def odd_header_left(self, value: str) -> None:
        self.set("oddHeaderL", value)

    @property
    def odd_header_center(self) -> Optional[str]:
        """
        .. code :: XML

            <oddHeaderC></oddHeaderC>

        :see: `MuseScore C++ source code: styledef.cpp line 501 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L501>`_
        """
        return self.get("oddHeaderC", False)

    @odd_header_center.setter
    def odd_header_center(self, value: str) -> None:
        self.set("oddHeaderC", value)

    @property
    def odd_header_right(self) -> Optional[str]:
        """
        .. code :: XML

            <oddHeaderR>$p</oddHeaderR>

        :see: `MuseScore C++ source code: styledef.cpp line 502 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L502>`_
        """
        return self.get("oddHeaderR", False)

    @odd_header_right.setter
    def odd_header_right(self, value: str) -> None:
        self.set("oddHeaderR", value)

    def set_header_all(self, left: str, center: str, right: str) -> None:
        """
        Set the header for all pages.

        :param left: The left part of the header.
        :param center: The center part of the header.
        :param right: The right part of the header.

        :see: :attr:`even_header_left`
        :see: :attr:`even_header_center`
        :see: :attr:`even_header_right`
        :see: :attr:`odd_header_left`
        :see: :attr:`odd_header_center`
        :see: :attr:`odd_header_right`
        """
        self.show_header = True
        self.header_odd_even = False
        self.even_header_left = left
        self.even_header_center = center
        self.even_header_right = right
        self.odd_header_left = left
        self.odd_header_center = center
        self.odd_header_right = right

    def set_header_odd_even(
        self,
        odd_left: str,
        even_left: str,
        odd_center: str,
        even_center: str,
        odd_right: str,
        even_right: str,
    ) -> None:
        """
        Set different headers for odd and even pages.

        :see: :attr:`even_header_left`
        :see: :attr:`even_header_center`
        :see: :attr:`even_header_right`
        :see: :attr:`odd_header_left`
        :see: :attr:`odd_header_center`
        :see: :attr:`odd_header_right`
        """
        self.show_header = True
        self.header_odd_even = True
        self.even_header_left = even_left
        self.even_header_center = even_center
        self.even_header_right = even_right
        self.odd_header_left = odd_left
        self.odd_header_center = odd_center
        self.odd_header_right = odd_right

    def clear_header(self) -> None:
        self.show_header = False
        self.even_header_left = ""
        self.even_header_center = ""
        self.even_header_right = ""
        self.odd_header_left = ""
        self.odd_header_center = ""
        self.odd_header_right = ""

    # footer ###################################################################

    @property
    def show_footer(self) -> bool:
        """
        Show the footer on the page.

        .. code :: XML

            <showFooter>1</showFooter>

        :see: `MuseScore C++ source code: styledef.cpp line 503 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L503>`_
        """
        return self.__get_bool_default("showFooter", True)

    @show_footer.setter
    def show_footer(self, value: bool) -> None:
        self.set("showFooter", int(value))

    @property
    def footer_first_page(self) -> bool:
        """
        Show the footer on the first page.

        .. code :: XML

            <footerFirstPage>1</footerFirstPage>

        :see: `MuseScore C++ source code: styledef.cpp line 505 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L505>`_
        """
        return self.__get_bool_default("footerFirstPage", True)

    @footer_first_page.setter
    def footer_first_page(self, value: bool) -> None:
        self.set("footerFirstPage", int(value))

    @property
    def footer_odd_even(self) -> bool:
        """
        Use different footers for odd and even pages.

        .. code :: XML

            <footerOddEven>1</footerOddEven>

        :see: `MuseScore C++ source code: styledef.cpp line 506 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L506>`_
        """
        return self.__get_bool_default("footerOddEven", True)

    @footer_odd_even.setter
    def footer_odd_even(self, value: bool) -> None:
        self.set("footerOddEven", int(value))

    # even/odd footer l/c/r ####################################################

    @property
    def even_footer_left(self) -> Optional[str]:
        """
        .. code :: XML

            <evenFooterL></evenFooterL>

        :see: `MuseScore C++ source code: styledef.cpp line 507 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L507>`_
        """
        return self.get("evenFooterL", False)

    @even_footer_left.setter
    def even_footer_left(self, value: str) -> None:
        self.set("evenFooterL", value)

    @property
    def even_footer_center(self) -> Optional[str]:
        """
        .. code :: XML

            <evenFooterC>$C</evenFooterC>

        :see: `MuseScore C++ source code: styledef.cpp line 508 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L508>`_
        """
        return self.get("evenFooterC", False)

    @even_footer_center.setter
    def even_footer_center(self, value: str) -> None:
        self.set("evenFooterC", value)

    @property
    def even_footer_right(self) -> Optional[str]:
        """
        .. code :: XML

            <evenFooterR></evenFooterR>

        :see: `MuseScore C++ source code: styledef.cpp line 509 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L509>`_
        """
        return self.get("evenFooterR", False)

    @even_footer_right.setter
    def even_footer_right(self, value: str) -> None:
        self.set("evenFooterR", value)

    @property
    def odd_footer_left(self) -> Optional[str]:
        """
        .. code :: XML

            <oddFooterL></oddFooterL>

        :see: `MuseScore C++ source code: styledef.cpp line 510 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L510>`_
        """
        return self.get("oddFooterL", False)

    @odd_footer_left.setter
    def odd_footer_left(self, value: str) -> None:
        self.set("oddFooterL", value)

    @property
    def odd_footer_center(self) -> Optional[str]:
        """
        .. code :: XML

             <oddFooterC>$C</oddFooterC>

        :see: `MuseScore C++ source code: styledef.cpp line 511 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L511>`_
        """
        return self.get("oddFooterC", False)

    @odd_footer_center.setter
    def odd_footer_center(self, value: str) -> None:
        self.set("oddFooterC", value)

    @property
    def odd_footer_right(self) -> Optional[str]:
        """
        .. code :: XML

            <oddFooterR></oddFooterR>

        :see: `MuseScore C++ source code: styledef.cpp line 512 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L512>`_
        """
        return self.get("oddFooterR", False)

    @odd_footer_right.setter
    def odd_footer_right(self, value: str) -> None:
        self.set("oddFooterR", value)

    def set_footer_all(self, left: str, center: str, right: str) -> None:
        """
        Set the footer for all pages.

        :param left: The left part of the footer.
        :param center: The center part of the footer.
        :param right: The right part of the footer.

        :see: :attr:`even_footer_left`
        :see: :attr:`even_footer_center`
        :see: :attr:`even_footer_right`
        :see: :attr:`odd_footer_left`
        :see: :attr:`odd_footer_center`
        :see: :attr:`odd_footer_right`
        """
        self.show_footer = True
        self.footer_odd_even = False
        self.even_footer_left = left
        self.even_footer_center = center
        self.even_footer_right = right
        self.odd_footer_left = left
        self.odd_footer_center = center
        self.odd_footer_right = right

    def set_footer_odd_even(
        self,
        odd_left: str,
        even_left: str,
        odd_center: str,
        even_center: str,
        odd_right: str,
        even_right: str,
    ) -> None:
        """
        Set the footer for odd and even pages.

        :see: :attr:`even_footer_left`
        :see: :attr:`even_footer_center`
        :see: :attr:`even_footer_right`
        :see: :attr:`odd_footer_left`
        :see: :attr:`odd_footer_center`
        :see: :attr:`odd_footer_right`
        """
        self.show_footer = True
        self.footer_odd_even = True
        self.even_footer_left = even_left
        self.even_footer_center = even_center
        self.even_footer_right = even_right
        self.odd_footer_left = odd_left
        self.odd_footer_center = odd_center
        self.odd_footer_right = odd_right

    def clear_footer(self) -> None:
        self.show_footer = False
        self.even_footer_left = ""
        self.even_footer_center = ""
        self.even_footer_right = ""
        self.odd_footer_left = ""
        self.odd_footer_center = ""
        self.odd_footer_right = ""

    # staff ####################################################################

    @property
    def staff_space(self) -> float | None:
        """
        The staff space in ``mm``, default values are ``1.750mm`` = ``0.069in``

        .. code :: XML

            <Spatium>1.74978</Spatium>

        styledef.cpp#L640 default 24.8 ???

        :see: `MuseScore C++ source code: styledef.cpp line 640 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L640>`_
        """
        return self.__get_float("Spatium")

    @staff_space.setter
    def staff_space(self, value: float) -> None:
        self.set("Spatium", value)

    @property
    def measure_number_offset(self) -> Offset:
        """
        .. code :: XML

            <measureNumberOffset x="0" y="-2"/>

        :see: `MuseScore C++ source code: styledef.cpp line 1008 <https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L1008>`_
        """
        return cast(Offset, self.__get_attributes("measureNumberOffset"))

    @measure_number_offset.setter
    def measure_number_offset(self, value: Offset) -> None:
        self.set("measureNumberOffset", cast(AttibutesDict, value))

    def reset_small_staffs(self) -> None:
        """
        Reset all small staffs to normal size.

        .. code-block:: xml

            <Part id="1">
                <Staff id="1">
                    <StaffType group="pitched">
                    <name>stdNormal</name>
                    <small>1</small>
                    </StaffType>
                    </Staff>
                <trackName>Voice</trackName>
                <Instrument id="voice">
                    <trackName>Voice</trackName>
                    <minPitchP>36</minPitchP>
                    <maxPitchP>94</maxPitchP>
        """
        for element in self.xml.findall(".//StaffType/small"):
            if element.text == "1":
                self.xml.remove(element)

    # lyrics ###################################################################

    @property
    def lyrics_font_size(self) -> float:
        even = self.__get_float("lyricsEvenFontSize")
        odd = self.__get_float("lyricsOddFontSize")
        if even is None or odd is None or even != odd:
            raise Exception(
                f"Lyrics even and odd size differs: even: {even} odd: {odd}"
            )
        return even

    @lyrics_font_size.setter
    def lyrics_font_size(self, value: float) -> None:
        self.set("lyricsEvenFontSize", value)
        self.set("lyricsOddFontSize", value)

    @property
    def lyrics_min_distance(self) -> Optional[float]:
        """
        default: 0.25

        https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L80


        """
        return self.__get_float("lyricsMinDistance")

    @lyrics_min_distance.setter
    def lyrics_min_distance(self, value: float) -> None:
        self.set("lyricsMinDistance", value)
