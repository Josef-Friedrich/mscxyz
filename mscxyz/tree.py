# -*- coding: utf-8 -*-

"""XML tree manipulation"""

from mscxyz.fileloader import File
from mscxyz.utils import re_open
import lxml

class Tree(File):

    def __init__(self, fullpath):
        super(Tree, self).__init__(fullpath)
        try:
            self.tree = lxml.etree.parse(self.fullpath)
        except lxml.etree.XMLSyntaxError as e:
            print('Error!!! ' + str(e))
            self.error = True
        else:
            self.error = False
            self.root = self.tree.getroot()

    def add_sub_element(self, root_tag, tag, text):
        if not self.error:
            tag = lxml.etree.SubElement(root_tag, tag)
            tag.text = text

    def strip_tags(self, *tags):
        if not self.error:
            lxml.etree.strip_tags(self.tree, tags)

    def remove_tags_by_xpath(self, *xpath_strings):
        if not self.error:
            for xpath_string in xpath_strings:
                for rm in self.tree.xpath(xpath_string):
                    rm.getparent().remove(rm)

    def merge_style(self, style_file):
        style = lxml.etree.parse(style_file).getroot()

        for score in self.tree.xpath('/museScore/Score'):
            score.insert(0, style[0])

    def clean(self):
        if not self.error:
            self.remove_tags_by_xpath(
                '/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
            self.strip_tags('font', 'b', 'i', 'pos')

    def save(self, new_name=''):
        if new_name:
            filename = new_name
        else:
            filename = self.fullpath
        if not self.error:
            self.tree.write(filename, encoding='UTF-8')
            re_open(filename)
