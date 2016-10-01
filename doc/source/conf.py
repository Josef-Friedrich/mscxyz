import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'mscxyz'
copyright = u'2016, Josef Friedrich'
author = u'Josef Friedrich'
version = u'0.0.5'
release = u'0.0.5'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False
html_static_path = []
htmlhelp_basename = 'mscxyzdoc'

latex_elements = {
     'papersize': 'a4paper',
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
     author, 'mscxyz',
     u'Manipulate the XML based *.mscx files of the notation software \
     MuseScore.',
     'Miscellaneous'),
]
