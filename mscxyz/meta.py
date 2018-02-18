# -*- coding: utf-8 -*-

"""Class for metadata maniplation"""

import lxml.etree as et
from termcolor import colored
import six

from mscxyz.tree import Tree
from mscxyz.utils import print_desc


class Meta(Tree):

    def __init__(self, fullpath):
        super(Meta, self).__init__(fullpath)

        if not self.error:
            tags = [
                "arranger",
                "composer",
                "copyright",
                "creationDate",
                "lyricist",
                "movementNumber",
                "movementTitle",
                "originalFormat",
                "platform",
                "poet",
                "source",
                "translator",
                "workNumber",
                "workTitle"
            ]

            self.meta = {}
            for tag in tags:
                text = self.get_meta_text(tag)
                if text:
                    if six.PY2:
                        self.meta[tag] = text.decode('utf-8')
                    else:
                        self.meta[tag] = text
                else:
                    self.meta[tag] = ''

            tags = [
                "Title",
                "Subtitle",
                "Composer",
                "Lyricist"
            ]

            self.vbox = {}
            for tag in tags:
                text = self.get_vbox_text(tag)
                if text:
                    if six.PY2:
                        self.vbox[tag] = text.decode('utf-8')
                    else:
                        self.vbox[tag] = text
                else:
                    self.vbox[tag] = ''

    def get_meta_tag(self, name):
        for element in self.root.xpath('//metaTag[@name="' + name + '"]'):
            return element

    def get_meta_text(self, name):
        element = self.get_meta_tag(name)
        if hasattr(element, 'text'):
            return element.text

    def set_meta(self, name, text):
        self.get_meta_tag(name).text = text

    def create_vbox(self):
        xpath = '/museScore/Score/Staff[@id="1"]'
        if not self.root.xpath(xpath + '/VBox'):
            tag = et.Element('VBox')
            self.add_sub_element(tag, 'height', '10')
            for element in self.root.xpath(xpath):
                element.insert(0, tag)

    def get_vbox_tag(self, style):
        for element in self.root.xpath('//VBox/Text'):
            if element.find('style').text == style:
                return element.find('text')

    def insert_in_vbox(self, style, text):
        tag = et.Element('Text')
        self.add_sub_element(tag, 'text', text)
        self.add_sub_element(tag, 'style', style)
        for element in self.root.xpath('//VBox'):
            element.append(tag)

    def get_vbox_text(self, style):
        element = self.get_vbox_tag(style)
        if hasattr(element, 'text'):
            return element.text

    def set_vbox(self, style, text):
        self.create_vbox()
        element = self.get_vbox_tag(style)
        if hasattr(element, 'text'):
            element.text = text
        else:
            self.insert_in_vbox(style, text)

    # Get a value by key.
    #
    # This function searches for values in this order: vbox, meta, filename.
    # Possible "key"s are: title, subtitle, composer, lyricist
    def get(self, key):
        if key == 'title':
            values = [
                self.vbox['Title'],
                self.meta['workTitle'],
                self.meta['movementTitle'],
                self.basename
            ]
        elif key == 'subtitle':
            values = [
                self.vbox['Subtitle'],
                self.meta['movementTitle'],
            ]
        else:
            values = [
                self.vbox[key.title()],
                self.meta[key],
            ]

        for value in values:
            if value:
                break

        return value

    def sync(self, key):
        if key == 'title':
            self.set_vbox('Title', self.get(key))
            self.set_meta('workTitle', self.get(key))
        elif key == 'subtitle':
            self.set_vbox('Subtitle', self.get(key))
            self.set_meta('workTitle', self.get(key))
        else:
            self.set_vbox(key.title(), self.get(key))
            self.set_meta(key, self.get(key))

    def clean_meta(self):
        tags = [
            "arranger",
            "copyright",
            "movementNumber",
            "movementTitle",
            "poet",
            "translator",
            "workNumber"
        ]
        for tag in tags:
            self.set_meta(tag, '')

    def sync_meta_tags(self):
        if not self.error:
            for key in ['title', 'subtitle', 'composer', 'lyricist']:
                self.sync(key)
            self.clean_meta()

    def show(self):
        print_desc('\n' + colored(self.filename, 'red'))
        print_desc(self.basename, 'filename', 'blue')
        if not self.error:
            for tag, text in self.meta.items():
                if text:
                    print_desc(text, tag, 'yellow')

            for tag, text in self.vbox.items():
                if text:
                    print_desc(text, tag, 'green')

    def export_json(self):
        import json
        data = {}
        data['title'] = self.get('title')

        output = open(self.fullpath.replace(
            '.' + self.extension, '.json'), 'w')
        json.dump(data, output, indent=4)
        output.close()
