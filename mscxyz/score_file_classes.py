# -*- coding: utf-8 -*-

"""A collection of classes intended to represent one MuseScore file."""


from mscxyz.utils import mscore, re_open
import lxml
import os
import shutil
import six


class File(object):
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


class Tree(File):
    """XML tree manipulation"""

    def __init__(self, relpath):
        super(Tree, self).__init__(relpath)
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
