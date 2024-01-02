"""Helper functions for XML handling."""

from __future__ import annotations

import typing

from lxml.etree import _Element

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


def find_safe(element: _Element, path: str) -> _Element:
    result: _Element | None = element.find(path)
    if result is None:
        raise ValueError(f"Path {path} not found in element {element}!")
    return result


def xpath_safe(element: _Element, path: str) -> _Element:
    output: list[_Element] = xpathall_safe(element, path)
    if len(output) > 1:
        raise ValueError(f"XPath “{path}” found more than one element in {element}!")
    return output[0]


def xpathall_safe(element: _Element, path: str) -> list[_Element]:
    result: _XPathObject = element.xpath(path)
    output: list[_Element] = []
    if isinstance(result, list):
        for item in result:
            if isinstance(item, _Element):
                output.append(item)

    if len(output) == 0:
        raise ValueError(f"XPath “{path}” not found in element {element}!")

    return output
