#! /usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess
import os


def path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(*path_segments):
    file_path = path(*path_segments)
    open(file_path, 'w').close()
    return open(file_path, 'a')


header = open(path('README_header.rst'), 'r')
readme = open_file('README.rst')
sphinx = open_file('doc', 'source', 'cli.rst')

sphinx_header = (
    '**********************\n',
    'Comande line interface\n',
    '**********************\n',
    '\n',
    '.. code-block:: text\n',
    '\n',
)

for line in sphinx_header:
    sphinx.write(str(line))

footer = open(path('README_footer.rst'), 'r')

for line in header:
    readme.write(line)

mscx = subprocess.Popen('mscx-manager help --rst all', shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

readme.write('\n')

for line in mscx.stdout:
    indented_line = line.decode('utf-8')
    readme.write(indented_line)
    sphinx.write(indented_line)
mscx.wait()

for line in footer:
    readme.write(line)

readme.close()
sphinx.close()
