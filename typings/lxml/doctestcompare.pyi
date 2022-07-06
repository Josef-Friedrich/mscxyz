"""
This type stub file was generated by pyright.
"""

import doctest

"""
lxml-based doctest output comparison.

Note: normally, you should just import the `lxml.usedoctest` and
`lxml.html.usedoctest` modules from within a doctest, instead of this
one::

    >>> import lxml.usedoctest # for XML output

    >>> import lxml.html.usedoctest # for HTML output

To use this module directly, you must call ``lxmldoctest.install()``,
which will cause doctest to use this in all subsequent calls.

This changes the way output is checked and comparisons are made for
XML or HTML-like content.

XML or HTML content is noticed because the example starts with ``<``
(it's HTML if it starts with ``<html``).  You can also use the
``PARSE_HTML`` and ``PARSE_XML`` flags to force parsing.

Some rough wildcard-like things are allowed.  Whitespace is generally
ignored (except in attributes).  In text (attributes and text in the
body) you can use ``...`` as a wildcard.  In an example it also
matches any trailing tags in the element, though it does not match
leading tags.  You may create a tag ``<any>`` or include an ``any``
attribute in the tag.  An ``any`` tag matches any tag, while the
attribute matches any and all attributes.

When a match fails, the reformatted example and gotten text is
displayed (indented), and a rough diff-like output is given.  Anything
marked with ``+`` is in the output but wasn't supposed to be, and
similarly ``-`` means its in the example but wasn't in the output.

You can disable parsing on one line with ``# doctest:+NOPARSE_MARKUP``
"""
__all__ = ['PARSE_HTML', 'PARSE_XML', 'NOPARSE_MARKUP', 'LXMLOutputChecker', 'LHTMLOutputChecker', 'install', 'temp_install']
_IS_PYTHON_3 = ...
PARSE_HTML = ...
PARSE_XML = ...
NOPARSE_MARKUP = ...
OutputChecker = doctest.OutputChecker
def strip(v): # -> None:
    ...

def norm_whitespace(v): # -> str:
    ...

_html_parser = ...
def html_fromstring(html): # -> Any:
    ...

_repr_re = ...
_norm_whitespace_re = ...
class LXMLOutputChecker(OutputChecker):
    empty_tags = ...
    def get_default_parser(self): # -> (text: Unknown, parser: Unknown) -> Any:
        ...
    
    def check_output(self, want, got, optionflags): # -> bool | Any:
        ...
    
    def get_parser(self, want, got, optionflags):
        ...
    
    def compare_docs(self, want, got):
        ...
    
    def text_compare(self, want, got, strip): # -> bool:
        ...
    
    def tag_compare(self, want, got): # -> bool:
        ...
    
    def output_difference(self, example, got, optionflags):
        ...
    
    def html_empty_tag(self, el, html=...): # -> bool:
        ...
    
    def format_doc(self, doc, html, indent, prefix=...):
        ...
    
    def format_text(self, text, strip=...): # -> Literal['']:
        ...
    
    def format_tag(self, el): # -> str:
        ...
    
    def format_end_tag(self, el): # -> Literal['-->']:
        ...
    
    def collect_diff(self, want, got, html, indent):
        ...
    
    def collect_diff_tag(self, want, got):
        ...
    
    def collect_diff_end_tag(self, want, got): # -> str:
        ...
    
    def collect_diff_text(self, want, got, strip=...): # -> Literal['']:
        ...
    


class LHTMLOutputChecker(LXMLOutputChecker):
    def get_default_parser(self): # -> (html: Unknown) -> Any:
        ...
    


def install(html=...): # -> None:
    """
    Install doctestcompare for all future doctests.

    If html is true, then by default the HTML parser will be used;
    otherwise the XML parser is used.
    """
    ...

def temp_install(html=..., del_module=...): # -> None:
    """
    Use this *inside* a doctest to enable this checker for this
    doctest only.

    If html is true, then by default the HTML parser will be used;
    otherwise the XML parser is used.
    """
    ...

class _RestoreChecker:
    def __init__(self, dt_self, old_checker, new_checker, check_func, clone_func, del_module) -> None:
        ...
    
    def install_clone(self): # -> None:
        ...
    
    def uninstall_clone(self): # -> None:
        ...
    
    def install_dt_self(self): # -> None:
        ...
    
    def uninstall_dt_self(self): # -> None:
        ...
    
    def uninstall_module(self): # -> None:
        ...
    
    def __call__(self, *args, **kw):
        ...
    
    def call_super(self, *args, **kw):
        ...
    


__test__ = ...
if __name__ == '__main__':
    ...
