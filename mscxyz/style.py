from __future__ import annotations

import typing
from io import TextIOWrapper
from pathlib import Path
from typing import Optional, Sequence, TypedDict, Union, cast

import lxml
import lxml.etree
from lxml.etree import _Attrib, _Element

from mscxyz import utils

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


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

    def __init__(self, score: "Score") -> None:
        self.score = score

        if self.score.style_file:
            self.parent_element = utils.xml.find_safe(
                utils.xml.read(self.score.style_file), "Style"
            )
        else:
            element: _Element | None = self.score.xml_root.find("Score/Style")
            if element is not None:
                self.parent_element = element
            else:
                self.parent_element: _Element = self.__create_parent_style()

    def __create_parent_style(self) -> _Element:
        """
        Create the parent style element.

        :return: The created parent style element.
        """
        score: _Element | None = self.score.xml_root.find("Score")
        if score is None:
            raise ValueError("The score file has no <Score> tag.")
        return lxml.etree.SubElement(score, "Style")

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
                parent = lxml.etree.SubElement(parent, tag)
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
            return float(value)
        return None

    def __get_attributes(self, style_name: str) -> _Attrib:
        element: _Element = self.get_element(style_name)
        return element.attrib

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
                element.text = str(value)
        return response

    def __get_text_style_element(self, name: str) -> _Element:
        if self.score.version_major != 2:
            raise ValueError(
                "This operation is only allowed for MuseScore 2 score files"
            )

        child: _Element | None = utils.xml.xpath(
            self.score.xml_root, f'//TextStyle/name[contains(., "{name}")]'
        )

        if child is not None:
            el: _Element | None = child.getparent()
            if el is None:
                raise ValueError(f"Parent not found on element {el}!")
            return el
        else:
            el_text_style: _Element = lxml.etree.SubElement(
                self.parent_element, "TextStyle"
            )
            el_name: _Element = lxml.etree.SubElement(el_text_style, "name")
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
                element = lxml.etree.SubElement(text_style, element_name)
            element.text = str(value)

    def get_all_fonts(self) -> list[tuple[str, str]]:
        """
        Returns a list of tuples containing the tag name and the font face.
        """
        output: list[tuple[str, str]] = []
        for element in self.parent_element:
            if "FontFace" in element.tag:
                output.append((element.tag, utils.xml.get_text_safe(element)))
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
        return self.get("musicalSymbolFont", raise_exception=False)

    def set_musical_symbol_fonts(self, font_face: str) -> StyleChanges:
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
        return self.set(
            ("musicalSymbolFont", "dynamicsFont", "dynamicsFontFace"), font_face
        )

    @property
    def musical_text_font(self) -> str | None:
        return self.get("musicalTextFont", raise_exception=False)

    def set_musical_text_font(self, font_face: str) -> StyleChanges:
        """
        .. code :: XML

            <musicalTextFont>Leland Text</musicalTextFont>
        """
        return self.set("musicalTextFont", font_face)

    def __set_parent_style_element(self, parent_style: _Element) -> None:
        score_element: _Element = utils.xml.find_safe(self.score.xml_root, "Score")
        score_element.insert(0, parent_style)
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

        style = lxml.etree.XML(styles)
        self.__set_parent_style_element(style[0])

    def load_style_file(self, file: str | Path | TextIOWrapper) -> None:
        style: _Element = utils.xml.read(file)
        self.__set_parent_style_element(style[0])

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
    def page_width(self) -> float | None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L43"""
        return self.__get_float("pageWidth")

    @page_width.setter
    def page_width(self, value: float) -> None:
        self.set("pageWidth", value)

    @property
    def page_height(self) -> float | None:
        """
        https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L44
        """
        return self.__get_float("pageHeight")

    @page_height.setter
    def page_height(self, value: float) -> None:
        self.set("pageHeight", value)

    def page_printable_width(self, value: float) -> None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L45"""
        self.set("pagePrintableWidth", value)

    def margin(self, value: float) -> None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L46-L51"""
        self.set(
            (
                "pageEvenLeftMargin",
                "pageOddLeftMargin",
                "pageEvenTopMargin",
                "pageEvenBottomMargin",
                "pageOddTopMargin",
                "pageOddBottomMargin",
            ),
            value,
        )

    def max_system_distance(self, value: float) -> None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L61"""
        self.set("maxSystemDistance", value)

    def header(self, value: str) -> None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L497-L502"""
        self.set(
            [
                "evenHeaderL",
                "evenHeaderC",
                "evenHeaderR",
                "oddHeaderL",
                "oddHeaderC",
                "oddHeaderR",
            ],
            value,
        )

    def footer(self, value: str) -> None:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L507-L512"""
        self.set(
            [
                "evenFooterL",
                "evenFooterC",
                "evenFooterR",
                "oddFooterL",
                "oddFooterC",
                "oddFooterR",
            ],
            value,
        )

    @property
    def spatium(self) -> float | None:
        """
        https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L640
        """
        return self.__get_float("Spatium")

    @spatium.setter
    def spatium(self, value: float) -> None:
        self.set("Spatium", value)

    @property
    def measure_number_offset(self) -> Offset:
        """https://github.com/musescore/MuseScore/blob/e0f941733ac2c0959203a5e99252eb4c58f67606/src/engraving/style/styledef.cpp#L1008


        .. code :: XML

            <measureNumberOffset x="0" y="-2"/>
        """
        return cast(Offset, self.__get_attributes("measureNumberOffset"))

    @measure_number_offset.setter
    def measure_number_offset(self, value: Offset) -> None:
        self.set("measureNumberOffset", cast(AttibutesDict, value))
