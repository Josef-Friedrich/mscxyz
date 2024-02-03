from __future__ import annotations

import typing
from io import TextIOWrapper
from pathlib import Path
from typing import Literal, Optional, Union

from lxml.etree import (
    XML,
    Element,
    SubElement,
    _Element,
    _ElementTree,
    parse,
    tostring,
)

if typing.TYPE_CHECKING:
    from lxml.etree import _DictAnyStr, _XPathObject


ListExtension = Literal["mscz", "mscx", "both"]

ElementLike = Optional[Union[_Element, _ElementTree, None]]


class XmlManipulator:
    """A wrapper around lxml.etree"""

    root: _Element

    file_path: Optional[Union[str, Path]] = None

    def __init__(
        self,
        element: Optional[_Element] = None,
        file_path: Optional[Union[str, Path]] = None,
        xml_markup: Optional[str] = None,
    ) -> None:
        if element is not None:
            self.root = element
        elif file_path is not None:
            self.root = XmlManipulator.parse_file(file_path)
            self.file_path = file_path
        elif xml_markup is not None:
            self.root = XmlManipulator.parse_string(xml_markup)
        else:
            self.root = Element("root")

    # Crud: Create #############################################################

    @staticmethod
    def parse_file(path: str | Path | TextIOWrapper) -> _Element:
        """
        Read an XML file and return the root element.

        :param path: The path to the XML file.

        :return: The root element of the XML file.
        """
        return parse(path).getroot()

    @staticmethod
    def parse_string(xml_markup: str) -> _Element:
        return XML(xml_markup)

    def tostring(self, element: ElementLike = None) -> str:
        """
        Convert the XML element or tree to a string.

        :param element: The XML element or tree to write.
        """
        element = self.__get_element(element)
        # maybe use: xml_declaration=True, pretty_print=True
        # TestFileCompare not passing ...
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + tostring(element, encoding="UTF-8").decode("utf-8")
            + "\n"
        )

    def write(self, path: str | Path, element: ElementLike = None) -> None:
        """
        Write the XML element or tree to the specified file.

        :param path: The path to the file.
        :param element: The XML element or tree to write.

        :return: None
        """
        element = self.__get_element(element)
        with open(path, "w") as document:
            document.write(self.tostring(element))

    @staticmethod
    def create_element(tag_name: str, attrib: Optional[_DictAnyStr] = None) -> _Element:
        return Element(tag_name, attrib=attrib)

    @staticmethod
    def create_sub_element(
        parent: _Element | str,
        tag_name: str,
        text: Optional[str] = None,
        attrib: Optional[_DictAnyStr] = None,
    ) -> tuple[_Element, _Element]:
        if isinstance(parent, str):
            parent = XmlManipulator.create_element(parent)
        sub_element: _Element = SubElement(parent, tag_name, attrib=attrib)
        if text:
            sub_element.text = text
        return (parent, sub_element)

    # cRud: Read ###############################################################

    def __get_element(self, element: ElementLike = None) -> _Element:
        """
        Get a XML element. If the element argument is a tree, return the root of the element argument.
        If the element argument is None, return the root element of the current instance.

        :param element: The XML element. Defaults to None.
        :return: The XML element.
        """
        if isinstance(element, _ElementTree):
            return element.getroot()
        if element is None:
            return self.root
        return element

    def __normalize_element(self, element: ElementLike = None) -> _Element | None:
        if isinstance(element, _ElementTree):
            return element.getroot()
        return element

    def find(self, element_path: str, element: ElementLike = None) -> _Element | None:
        """
        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support, for example ``.//Note`` selects all ``<Note>`` elements.
        """
        return self.__get_element(element).find(element_path)

    def find_safe(self, element_path: str, element: ElementLike = None) -> _Element:
        """
        Find an element in the given XML element using the specified element path.

        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support, for example ``.//Note`` selects all ``<Note>`` elements.
        :param element: The XML element to search within.

        :return: The found element.

        :raises ValueError: If the element is not found.
        """
        element = self.__get_element(element)
        result: _Element | None = element.find(element_path)
        if result is None:
            raise ValueError(f"Path {element_path} not found in element {element}!")
        return result

    def findall(self, element_path: str, element: ElementLike = None) -> list[_Element]:
        """
        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support, for example ``.//Note`` selects all ``<Note>`` elements.
        """
        return self.__get_element(element).findall(element_path)

    def xpath(self, xpath: str, element: ElementLike = None) -> _Element | None:
        """
        Find the first matching element in the XML tree using XPath.

        :param xpath: The XPath expression to search for.
        :param element: The root element of the XML tree.

        :return: The first matching element or None if no match is found.
        """
        element = self.__get_element(element)
        output: list[_Element] | None = self.xpathall(xpath, element)
        if output and len(output) > 0:
            return output[0]

        return None

    def xpath_safe(self, xpath: str, element: ElementLike = None) -> _Element:
        """
        Safely retrieves the first matching XML element using the given XPath expression.

        :param xpath: The XPath expression to match elements.
        :param element: The XML element to search within.

        :return: The first matching XML element.XPath

        :raises ValueError: If more than one element is found matching the XPath expression.
        """
        element = self.__get_element(element)
        output: list[_Element] = self.xpathall_safe(
            xpath,
            element,
        )
        if len(output) > 1:
            raise ValueError(
                f"XPath “{xpath}” found more than one element in {element}!"
            )
        return output[0]

    def xpathall(
        self, xpath: str, element: ElementLike = None
    ) -> list[_Element] | None:
        """
        Returns a list of elements matching the given XPath expression.

        :param xpath: The XPath expression to match elements.
        :param element: The XML element to search within.

        :return: A list of elements matching the XPath expression, or None if no
          elements are found.
        """
        element = self.__get_element(element)
        result: _XPathObject = element.xpath(xpath)
        output: list[_Element] = []

        if isinstance(result, list):
            for item in result:
                if isinstance(item, _Element):
                    output.append(item)

        if len(output) > 0:
            return output

        return None

    def xpathall_safe(self, xpath: str, element: ElementLike = None) -> list[_Element]:
        """
        Safely retrieves a list of elements matching the given XPath expression within
        the specified element.

        :param xpath: The XPath expression to match elements.
        :param element: The XML element to search within.

        :return: A list of elements matching the XPath expression.

        :raises ValueError: If the XPath expression is not found in the element.
        """
        element = self.__get_element(element)
        output: list[_Element] | None = self.xpathall(xpath, element)
        if output is None:
            raise ValueError(f"XPath “{xpath}” not found in element {element}!")
        return output

    def get_text(self, element: ElementLike = None) -> str | None:
        """
        Get the text content of an XML element.

        :param element: The XML element.

        :return: The text content of the XML element, or None if the element is None.
        """
        element = self.__normalize_element(element)
        if element is None:
            return None
        if element.text is None:
            return None
        return element.text

    def get_text_safe(
        self, element: ElementLike = None, element_path: Optional[str] = None
    ) -> str:
        """
        Safely retrieves the text content from an XML element.

        :param element: The XML element to retrieve the text from.
        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support, for example ``.//Note`` selects all ``<Note>`` elements.

        :return: The text content of the element.

        :raises ValueError: If the element is None or has no text content.
        """
        if element_path is not None:
            element = self.find_safe(element_path)
        else:
            element = self.__get_element(element)
        if element.text is None:
            raise ValueError(f"Element {element} has no text!")
        return element.text

    # crUd: Update #############################################################

    def set_text(
        self, element_path: str, value: str | int | float, element: ElementLike = None
    ) -> XmlManipulator:
        """
        Set the text value of an XML element at the specified element path.

        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support to locate the target element,
          for example ``.//Note`` selects all ``<Note>`` elements.
        :param value: The new value to set for the element's text.
        :param element: The XML element to modify.

        :return: None
        """
        self.find_safe(element_path, element).text = str(value)
        return self

    @staticmethod
    def replace(old: _Element, new: _Element) -> None:
        """
        Replaces an element in its parent with a new element.

        :param old: The element to be replaced.
        :param new: The new element to replace the old element.

        :return: None
        """
        parent: _Element | None = old.getparent()
        if parent is not None:
            parent.replace(old, new)

    # cruD: Delete #############################################################

    @staticmethod
    def remove(element: _Element | None) -> None:
        """
        Remove the given element from its parent.

        :param element: The element to be removed.
        """
        if element is None:
            return None

        parent: _Element | None = element.getparent()
        if parent is None:
            return None

        parent.remove(element)

    def remove_tags(self, *element_paths: str) -> XmlManipulator:
        """
        :param element_path: A `element path expression
          <https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath>`_
          with limited XPath support to locate the target element,
          for example ``.//Note`` selects all ``<Note>`` elements.
        """
        for path in element_paths:
            for element in self.findall(path):
                self.remove(element)
        return self
