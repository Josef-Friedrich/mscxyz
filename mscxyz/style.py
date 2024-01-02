from __future__ import annotations

import os
import typing

import lxml
import lxml.etree
from lxml.etree import _Element

from mscxyz.xml import find_safe, xpath

if typing.TYPE_CHECKING:
    from mscxyz.score_file_classes import MuseScoreFile


class MscoreStyleInterface:
    """
    Interface specialized for the style manipulation.

    :param relpath: The relative (or absolute) path of a MuseScore file.
    """

    score: "MuseScoreFile"

    element: _Element
    """The ``/museScore/Score/Style`` element object, see
    https://lxml.de/tutorial.html#the-element-class
    """

    def __init__(self, score: "MuseScoreFile"):
        self.score = score
        element = self.score.xml_tree.find("Score/Style")
        if element is not None:
            self.element = element
        else:
            self.element: _Element = self._create_parent_style()

    def _create_parent_style(self):
        score = self.score.xml_tree.find("Score")
        if score is None:
            raise ValueError("The score file has no <Score> tag.")
        return lxml.etree.SubElement(score, "Style")

    def _create(self, tag: str) -> _Element:
        """
        :param tag: Nested tags are supported, for example ``TextStyle/halign``
        """
        tags = tag.split("/")
        parent = self.element
        for tag in tags:
            element = parent.find(tag)
            if element is None:
                parent = lxml.etree.SubElement(parent, tag)
            else:
                parent = element
        return parent

    def get_element(self, element_path: str, create: bool = False) -> _Element:
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
            test = MscoreStyleInterface('text.mscx')
            element = test.get_element('measureNumberOffset', create=True)
            element.attrib['x'] = '0.5'
            element.attrib['y'] = '-2'
            test.save()
        """
        element = self.element.find(element_path)
        if element is None and create:
            element = self._create(element_path)
        return element

    def get_value(self, element_path: str) -> str:
        """
        Get the value (text) of a style tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element = self.get_element(element_path)
        return element.text

    def set_attributes(
        self, element_path: str, attributes: dict[str, str | int | float]
    ) -> _Element:
        """Set attributes on a style child tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element: _Element = self.get_element(element_path, create=True)
        for name, value in attributes.items():
            element.attrib[name] = str(value)
        return element

    def set_value(self, element_path: str, value: str | int | float):
        """
        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element = self.element.find(element_path)
        if element is None:
            element: _Element = self._create(element_path)
        element.text = str(value)

    def _get_text_style_element(self, name: str) -> _Element:
        if self.score.version_major != 2:
            raise ValueError(
                "This operation is only allowed for MuseScore 2 score files"
            )

        child: _Element | None = xpath(
            self.score.xml_root, f'//TextStyle/name[contains(., "{name}")]'
        )

        if child is not None:
            el: _Element | None = child.getparent()
            if el is None:
                raise ValueError(f"Parent not found on element {el}!")
            return el
        else:
            el_text_style: _Element = lxml.etree.SubElement(self.element, "TextStyle")
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

        :param name: The name of the text style, for example ``Title``, ``Subtitle``, ``Lyricist``, ``Fingering``, ``String Number``, ``Dynamics`` etc.
        """
        text_style = self._get_text_style_element(name)
        out: dict[str, str] = {}
        for child in text_style.iterchildren():
            if child.text is not None:
                out[child.tag] = child.text
        return out

    def set_text_style(self, name: str, values: dict[str, str | int | float]) -> None:
        """Set text styles. Only MuseScore2!

        :param name: The name of the text style, for example ``Title``, ``Subtitle``, ``Lyricist``, ``Fingering``, ``String Number``, ``Dynamics`` etc.        :param values: A dictionary. The keys are the tag names, values are
          the text values of the child tags, for example
          ``{size: 14, bold: 1}``.
        """
        text_style = self._get_text_style_element(name)
        for element_name, value in values.items():
            el = text_style.find(element_name)
            if el is None:
                el = lxml.etree.SubElement(text_style, element_name)
            el.text = str(value)

    def merge(self, styles: str) -> None:
        """Merge styles into the XML tree.

        :param styles: The path of the style file or a string containing
          the XML style markup.

        ``styles`` may not contain surrounding ``<Style>`` tags. This input is
        valid:

        .. code :: XML

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

        This input is invalid:

        .. code :: XML

            <?xml version="1.0"?>
            <museScore version="2.06">
              <Style>
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
                </Style>
              </museScore>

        """
        if os.path.exists(styles):
            style: _Element = lxml.etree.parse(styles).getroot()
        else:
            # <?xml ... tag without encoding to avoid this error:
            # ValueError: Unicode strings with encoding declaration are
            # not supported. Please use bytes input or XML fragments without
            # declaration.
            pre = '<?xml version="1.0"?><museScore version="2.06"><Style>'
            post = "</Style></museScore>"
            style = lxml.etree.XML(pre + styles + post)

        parent = find_safe(self.score.xml_root, "Score")
        parent.insert(0, style[0])