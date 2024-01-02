from __future__ import annotations

import typing

import lxml
from lxml.etree import _Element

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject

    from mscxyz.score_file_classes import MuseScoreFile


class MscoreStyleInterface:
    """
    Interface specialized for the style manipulation.

    :param relpath: The relative (or absolute) path of a MuseScore file.
    """

    score: "MuseScoreFile"

    style: _Element

    def __init__(self, score: "MuseScoreFile"):
        self.score = score
        styles: _XPathObject = self.score.xml_tree.xpath("/museScore/Score/Style")
        if styles:
            self.style = styles[0]
            """The ``/museScore/Score/Style`` element object, see
            https://lxml.de/tutorial.html#the-element-class
            """
        else:
            self.style: _Element = self._create_parent_style()

    def _create_parent_style(self):
        score: _XPathObject = self.score.xml_tree.xpath("/museScore/Score")
        return lxml.etree.SubElement(score[0], "Style")

    def _create(self, tag: str) -> _Element:
        """
        :param tag: Nested tags are supported, for example ``TextStyle/halign``
        """
        tags = tag.split("/")
        parent = self.style
        for tag in tags:
            element = parent.find(tag)
            if element is None:
                parent = lxml.etree.SubElement(parent, tag)
            else:
                parent = element
        return parent

    def get_element(self, element_path: str, create: bool = False) -> _Element:
        """
        Get a lxml element which is parent to the ``Style`` tag.

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
        element = self.style.find(element_path)
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
        element = self.style.find(element_path)
        if element is None:
            element: _Element = self._create(element_path)
        element.text = str(value)

    def _get_text_style_element(self, name: str) -> _Element:
        if self.score.version_major != 2:
            raise ValueError(
                "This operation is only allowed for MuseScore 2 score files"
            )
        xpath = '//TextStyle/name[contains(., "{}")]'.format(name)
        child = self.score.xml_tree.xpath(xpath)
        if child:
            return child[0].getparent()
        else:
            el_text_style: _Element = lxml.etree.SubElement(self.style, "TextStyle")
            el_name: _Element = lxml.etree.SubElement(el_text_style, "name")
            el_name.text = name
            return el_text_style

    def get_text_style(self, name: str) -> dict[str, str | int | float]:
        """Get text styles. Only MuseScore2!

        :param name: The name of the text style.
        """
        text_style = self._get_text_style_element(name)
        out: dict[str, str] = {}
        for child in text_style.iterchildren():
            out[child.tag] = child.text
        return out

    def set_text_style(self, name: str, values: dict[str, str | int | float]) -> None:
        """Set text styles. Only MuseScore2!

        :param name: The name of the text style.
        :param values: A dictionary. The keys are the tag names, values are
          the text values of the child tags, for example
          ``{size: 14, bold: 1}``.
        """
        text_style = self._get_text_style_element(name)
        for element_name, value in values.items():
            el = text_style.find(element_name)
            if el is None:
                el = lxml.etree.SubElement(text_style, element_name)
            el.text = str(value)
