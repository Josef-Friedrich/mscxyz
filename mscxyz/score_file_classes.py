# -*- coding: utf-8 -*-

"""A collection of classes intended to represent one MuseScore file.

The classes build on each other hierarchically. The class hierarchy:

.. code ::

    ScoreScoreFile
        XMLXMLTree
            Meta
            Lyrics
            Rename

Depending on the subcommand


"""


from mscxyz.utils import mscore, re_open
import fnmatch
import lxml
import os
import shutil
import six
import string


def list_scores(path, extension='both'):
    if extension == 'both':
        glob='*.msc[xz]'
    elif extension in ('mscx', 'mscy'):
        glob='*.{}'.format(extension)
    else:
        raise ValueError('Possible values for the argument “extension” are: '
                         '“both”, “mscx”, “mscz”')
    if os.path.isfile(path):
        return [path]
    out = []
    for root, dirs, scores in os.walk(path):
        for score in scores:
            if fnmatch.fnmatch(score, glob):
                scores_path = os.path.join(root, score)
                out.append(scores_path)
    out.sort()
    return out


def list_scores_grouped_by_alphabet():
    score_dirs = ['0']
    for char in string.lowercase:
        score_dirs.append(char)
    return score_dirs


class Batch(object):
    """Load multiple MuseScore files"""
    def __init__(self, path, glob='*.mscx'):
        self.path = path
        self.files = []

        for root, dirs, files in os.walk(path):
            for file in files:
                if fnmatch.fnmatch(file, glob):
                    file_path = os.path.join(root, file)
                    self.files.append(file_path)

        self.files.sort()

    def get_files(self):
        if os.path.isdir(self.path):
            return self.files
        else:
            return [self.path]


###############################################################################
# Class hierarchy level 1
###############################################################################


class ScoreFile(object):
    """Basic file loading"""

    def __init__(self, relpath):
        self.errors = []
        self.relpath = relpath
        self.abspath = os.path.abspath(relpath)
        self.extension = relpath.split('.')[-1]
        self.relpath_backup = relpath.replace(
            '.' + self.extension, '_bak.' + self.extension)
        self.dirname = os.path.dirname(relpath)
        self.filename = os.path.basename(relpath)
        if six.PY2:
            self.basename = self.filename.replace('.mscx', '').decode('utf-8')
        else:
            self.basename = self.filename.replace('.mscx', '')

    def backup(self):
        """Make a copy of the MuseScore"""
        shutil.copy2(self.relpath, self.relpath_backup)

    def export(self, extension='pdf'):
        """Export the score to the specifed file type

        :param str extension: The extension (default: pdf)
        """
        score = self.relpath
        mscore(['--export-to', score.replace('.mscx', '.' + extension), score])


###############################################################################
# Class hierarchy level 2
###############################################################################


class XMLTree(ScoreFile):
    """XML tree manipulation"""

    def __init__(self, relpath):
        super(XMLTree, self).__init__(relpath)
        try:
            self.xml_tree = lxml.etree.parse(self.relpath)
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.xml_root = self.xml_tree.getroot()

    def add_sub_element(self, root_tag, tag, text):
        tag = lxml.etree.SubElement(root_tag, tag)
        tag.text = text

    def strip_tags(self, *tags):
        lxml.etree.strip_tags(self.xml_tree, tags)

    def remove_tags_by_xpath(self, *xpath_strings):
        for xpath_string in xpath_strings:
            for rm in self.xml_tree.xpath(xpath_string):
                rm.getparent().remove(rm)

    def merge_style(self, style_file):
        style = lxml.etree.parse(style_file).getroot()

        for score in self.xml_tree.xpath('/museScore/Score'):
            score.insert(0, style[0])

    def clean(self):
        self.remove_tags_by_xpath(
            '/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
        self.strip_tags('font', 'b', 'i', 'pos')

    def save(self, new_name='', mscore=False):
        if new_name:
            filename = new_name
        else:
            filename = self.relpath
        if not self.errors:
            self.xml_tree.write(filename, encoding='UTF-8')
            if mscore:
                re_open(filename)


###############################################################################
# Class hierarchy level 3
###############################################################################
