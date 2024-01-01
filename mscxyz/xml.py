"""Helper functions for XML handling."""

from __future__ import annotations

import typing
from typing import Optional

from lxml.etree import _Element

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


def iter(
    element: _Element, path: Optional[str] = None, xpath: Optional[str] = None
) -> list[_Element]:
    """
    Returns a list of XML elements that match the given path or XPath expression.

    :param element: The root XML element to search within.
    :param path: The path to the XML elements, findall is used https://lxml.de/apidoc/lxml.etree.html#lxml.etree._Element.findall see https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath.
    :param xpath: The XPath expression to match against the XML elements.
    :return: A list of XML elements that match the XPath expression.
    """

    if path:
        return element.findall(path)
    if xpath:
        result: _XPathObject = element.xpath(xpath)
        output: list[_Element] = []
        if isinstance(result, list):
            for item in result:
                if isinstance(item, _Element):
                    output.append(item)
        return output
    raise ValueError("Either path or xpath must be specified.")
