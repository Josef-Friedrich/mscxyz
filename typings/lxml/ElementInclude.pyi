"""
This type stub file was generated by pyright.
"""

from lxml import etree

"""
Limited XInclude support for the ElementTree package.

While lxml.etree has full support for XInclude (see
`etree.ElementTree.xinclude()`), this module provides a simpler, pure
Python, ElementTree compatible implementation that supports a simple
form of custom URL resolvers.
"""
XINCLUDE = ...
XINCLUDE_INCLUDE = ...
XINCLUDE_FALLBACK = ...
XINCLUDE_ITER_TAG = ...
DEFAULT_MAX_INCLUSION_DEPTH = ...
class FatalIncludeError(etree.LxmlSyntaxError):
    ...


class LimitedRecursiveIncludeError(FatalIncludeError):
    ...


def default_loader(href, parse, encoding=...): # -> str:
    ...

def include(elem, loader=..., base_url=..., max_depth=...): # -> None:
    ...

