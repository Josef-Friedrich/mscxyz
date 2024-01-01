import sphinx_rtd_theme

import mscxyz

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]
templates_path = ["_templates"]
source_suffix = ".rst"

master_doc = "index"

project = "mscxyz"
copyright = "2016 - 2023, Josef Friedrich"
author = "Josef Friedrich"
version = mscxyz.__version__
release = mscxyz.__version__
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False
html_static_path = []
htmlhelp_basename = "mscxyzdoc"

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    # "private-members": True,
    # "special-members": True,
    "inherited-members": True,
    "show-inheritance": True,
    "ignore-module-all": True,
    # "imported-members": False,
    "exclude-members": True,
    "class-doc-from": True,
    "no-value": True,
}
