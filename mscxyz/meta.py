# -*- coding: utf-8 -*-

"""Class for metadata maniplation"""

from mscxyz.tree import Tree
from mscxyz.utils import print_desc
from termcolor import colored
import lxml
import six


class MetaTag(object):

    """The available metaTag fields are:

        * `arranger`
        * `composer`
        * `copyright`
        * `creationDate`
        * `lyricist`
        * `movementNumber`
        * `movementTitle`
        * `originalFormat`
        * `platform`
        * `poet`
        * `source`
        * `translator`
        * `workNumber`
        * `workTitle`

        """

    def __init__(self, xml_root):
        self.xml_root = xml_root

    def _get_element(self, name):
        for element in self.xml_root.xpath('//metaTag[@name="' + name + '"]'):
            return element

    def _get_text(self, name):
        element = self._get_element(name)
        if hasattr(element, 'text'):
            return element.text

    def __getattr__(self, name):
        if name == 'xml_root':
            return getattr(self, name)
        else:
            return self._get_text(name)

    def __setattr__(self, name, value):
        if name == 'xml_root':
            self.__dict__[name] = value
        else:
            self._get_element(name).text = value


class Vbox(object):
    """The first vertical box of a score.

    Available fields:

    * `Title`
    * `Subtitle`
    * `Composer`
    * `Lyricist`

    """

    def __init__(self, xml_root):
        xpath = '/museScore/Score/Staff[@id="1"]'
        if not xml_root.xpath(xpath + '/VBox'):
            vbox = lxml.etree.Element('VBox')
            height = lxml.etree.SubElement(vbox, 'height')
            height.text = '10'

            for element in xml_root.xpath(xpath):
                element.insert(0, vbox)

    def get_vbox_tag(self, style):
        for element in self.root.xpath('//VBox/Text'):
            if element.find('style').text == style:
                return element.find('text')

    def insert_in_vbox(self, style, text):
        tag = lxml.etree.Element('Text')
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
            tag = lxml.etree.Element('VBox')
            self.add_sub_element(tag, 'height', '10')
            for element in self.root.xpath(xpath):
                element.insert(0, tag)

    def get_vbox_tag(self, style):
        for element in self.root.xpath('//VBox/Text'):
            if element.find('style').text == style:
                return element.find('text')

    def insert_in_vbox(self, style, text):
        tag = lxml.etree.Element('Text')
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
