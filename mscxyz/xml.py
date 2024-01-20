from __future__ import annotations

import typing
from io import TextIOWrapper
from pathlib import Path
from typing import Literal, Optional

import lxml
import lxml.etree
from lxml.etree import _Element, _ElementTree

if typing.TYPE_CHECKING:
    from lxml.etree import _DictAnyStr, _XPathObject


ListExtension = Literal["mscz", "mscx", "both"]

ElementLike = _Element | _ElementTree | None


class Xml:
    """A wrapper around lxml.etree"""

    element: _Element

    def __init__(self, element: _Element) -> None:
        self.element = element

    def __get_element(self, element: ElementLike = None) -> _Element:
        if isinstance(element, _ElementTree):
            return element.getroot()
        if element is None:
            return self.element
        return element

    def __normalize_element(self, element: ElementLike = None) -> _Element | None:
        if isinstance(element, _ElementTree):
            return element.getroot()
        return element

    @staticmethod
    def read(path: str | Path | TextIOWrapper) -> _Element:
        """
        Read an XML file and return the root element.

        :param path: The path to the XML file.

        :return: The root element of the XML file.
        """
        return lxml.etree.parse(path).getroot()

    @staticmethod
    def from_file(path: str | Path | TextIOWrapper) -> Xml:
        return Xml(Xml.read(path))

    @staticmethod
    def parse(string: str) -> _Element:
        return lxml.etree.XML(string)

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
            + lxml.etree.tostring(element, encoding="UTF-8").decode("utf-8")
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

    def find_safe(self, path: str, element: ElementLike = None) -> _Element:
        """
        Find an element in the given XML element using the specified element path.

        :param path: The path to the desired element.
        :param element: The XML element to search within.

        :return: The found element.

        :raises ValueError: If the element is not found.
        """

        element = self.__get_element(element)
        result: _Element | None = element.find(path)
        if result is None:
            raise ValueError(f"Path {path} not found in element {element}!")
        return result

    def xpath(self, path: str, element: ElementLike = None) -> _Element | None:
        """
        Find the first matching element in the XML tree using XPath.

        :param path: The XPath expression to search for.
        :param element: The root element of the XML tree.

        :return: The first matching element or None if no match is found.
        """
        element = self.__get_element(element)
        output: list[_Element] | None = self.xpathall(path, element)
        if output and len(output) > 0:
            return output[0]

        return None

    def xpath_safe(self, path: str, element: ElementLike = None) -> _Element:
        """
        Safely retrieves the first matching XML element using the given XPath expression.

        :param path: The XPath expression to match elements.
        :param element: The XML element to search within.

        :return: The first matching XML element.XPath

        :raises ValueError: If more than one element is found matching the XPath expression.
        """
        element = self.__get_element(element)
        output: list[_Element] = self.xpathall_safe(
            path,
            element,
        )
        if len(output) > 1:
            raise ValueError(
                f"XPath “{path}” found more than one element in {element}!"
            )
        return output[0]

    def xpathall(self, path: str, element: ElementLike = None) -> list[_Element] | None:
        """
        Returns a list of elements matching the given XPath expression.

        :param path: The XPath expression to match elements.
        :param element: The XML element to search within.

        :return: A list of elements matching the XPath expression, or None if no
          elements are found.
        """
        element = self.__get_element(element)
        result: _XPathObject = element.xpath(path)
        output: list[_Element] = []

        if isinstance(result, list):
            for item in result:
                if isinstance(item, _Element):
                    output.append(item)

        if len(output) > 0:
            return output

        return None

    def xpathall_safe(self, path: str, element: ElementLike = None) -> list[_Element]:
        """
        Safely retrieves a list of elements matching the given XPath expression within
        the specified element.

        :param element: The XML element to search within.
        :param path: The XPath expression to match elements.

        :return: A list of elements matching the XPath expression.

        :raises ValueError: If the XPath expression is not found in the element.
        """
        element = self.__get_element(element)
        output: list[_Element] | None = self.xpathall(path, element)
        if output is None:
            raise ValueError(f"XPath “{path}” not found in element {element}!")
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

    def get_text_safe(self, element: ElementLike = None) -> str:
        """
        Safely retrieves the text content from an XML element.

        :param element: The XML element to retrieve the text from.

        :return: The text content of the element.

        :raises ValueError: If the element is None or has no text content.
        """
        element = self.__get_element(element)
        if element.text is None:
            raise ValueError(f"Element {element} has no text!")
        return element.text

    def set_text(
        self, path: str, value: str | int | float, element: ElementLike = None
    ) -> None:
        """
        Set the text value of an XML element at the specified element path.

        :param element: The XML element to modify.
        :param path: The element path expression to locate the target element.
        :param value: The new value to set for the element's text.

        :return: None
        """
        self.find_safe(path, element).text = str(value)

    @staticmethod
    def replace(old: _Element, new: _Element) -> None:
        parent: _Element | None = old.getparent()
        if parent is not None:
            parent.replace(old, new)

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

    @staticmethod
    def create_element(tag_name: str) -> _Element:
        return lxml.etree.Element(tag_name)

    @staticmethod
    def create_sub_element(
        parent: _Element,
        tag_name: str,
        text: Optional[str] = None,
        attrib: Optional[_DictAnyStr] = None,
    ) -> _Element:
        element: _Element = lxml.etree.SubElement(parent, tag_name, attrib=attrib)
        if text:
            element.text = text
        return element