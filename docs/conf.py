from __future__ import annotations

import sphinx_rtd_theme  # type: ignore

import mscxyz

html_theme = "sphinx_rtd_theme"
html_theme_path: list[str] = [sphinx_rtd_theme.get_html_theme_path()]

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
]
templates_path: list[str] = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "mscxyz"
copyright = "2016 - 2023, Josef Friedrich"
author = "Josef Friedrich"
version: str = mscxyz.__version__
release: str = mscxyz.__version__
language = "en"
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False
html_static_path: list[str] = []
htmlhelp_basename = "mscxyzdoc"

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "private-members": False,
    "special-members": False,
    "inherited-members": False,
    "show-inheritance": True,
    "ignore-module-all": True,
    # "imported-members": False,
    "exclude-members": True,
    "class-doc-from": "both",
    "no-value": True,
}
