# -*- coding: utf-8 -*-

"""XML tree manipulation"""

import lxml.etree as et

from mscxyz.utils import re_open
from mscxyz.fileloader import File


class Tree(File):

    def __init__(self, fullpath):
        super(Tree, self).__init__(fullpath)
        try:
            self.tree = et.parse(self.fullpath)
        except et.XMLSyntaxError as e:
            print('Error!!! ' + str(e))
            self.error = True
        else:
            self.error = False
            self.root = self.tree.getroot()

    def addSubElement(self, root_tag, tag, text):
        if not self.error:
            tag = et.SubElement(root_tag, tag)
            tag.text = text

    def stripTags(self, *tags):
        if not self.error:
            et.strip_tags(self.tree, tags)

    def removeTagsByXPath(self, *xpath_strings):
        if not self.error:
            for xpath_string in xpath_strings:
                for rm in self.tree.xpath(xpath_string):
                    rm.getparent().remove(rm)

    def mergeStyle(self, style_file):
        style = et.parse(style_file).getroot()

        for score in self.tree.xpath('/museScore/Score'):
            score.insert(0, style[0])

    def clean(self):
        if not self.error:
            self.removeTagsByXPath(
                '/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
            self.stripTags('font', 'b', 'i', 'pos')

    def write(self, new_name=''):
        if new_name:
            filename = new_name
        else:
            filename = self.fullpath
        if not self.error:
            self.tree.write(filename, encoding='UTF-8')
            re_open(filename)
