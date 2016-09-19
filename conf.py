# -*- coding: utf-8 -*-
extensions = [
    'sphinx.ext.autodoc',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'mscxyz'
copyright = u'2016, Josef Friedrich'
author = u'Josef Friedrich'
version = u'0.0.2'
release = u'0.0.2'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'mscxyzdoc'
latex_elements = {
     'papersize': 'a4pager',
     'pointsize': '11pt',
}
latex_documents = [
    (master_doc, 'mscxyz.tex', u'mscxyz Documentation',
     u'Josef Friedrich', 'manual'),
]
man_pages = [
    (master_doc, 'mscxyz', u'mscxyz Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'mscxyz', u'mscxyz Documentation',
     author, 'mscxyz', 'One line description of project.',
     'Miscellaneous'),
]
