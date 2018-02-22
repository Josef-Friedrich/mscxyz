# -*- coding: utf-8 -*-

"""Class for metadata maniplation"""

from mscxyz.tree import Tree
from mscxyz.utils import print_desc
from termcolor import colored
import lxml
import six
import json


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

    fields = (
        'arranger',
        'composer',
        'copyright',
        'creationDate',
        'lyricist',
        'movementNumber',
        'movementTitle',
        'platform',
        'poet',
        'source',
        'translator',
        'workNumber',
        'workTitle',
    )

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
        if name not in self.fields:
            raise AttributeError
        else:
            return self._get_text(name)

    def __setattr__(self, name, value):
        if name == 'xml_root' or name == 'fields':
            self.__dict__[name] = value
        else:
            self._get_element(name).text = value

    def clean(self):
        fields = (
            'arranger',
            'copyright',
            'creationDate',
            'movementNumber',
            'platform',
            'poet',
            'source',
            'translator',
            'workNumber',
        )
        for field in fields:
            setattr(self, field, '')


class Vbox(object):
    """The first vertical box of a score.

    Available fields:

    * `Composer`
    * `Lyricist`
    * `Subtitle`
    * `Title`

    .. code-block:: xml

        <Staff id="1">
          <VBox>
            <height>10</height>
            <Text>
              <style>Title</style>
              <text>Title</text>
              </Text>
            <Text>
              <style>Composer</style>
              <text>Composer</text>
              </Text>
            </VBox>
          </Staff>

    """

    fields = (
        'Composer',
        'Lyricist',
        'Subtitle',
        'Title',
    )

    def __init__(self, xml_root):
        self.xml_root = xml_root
        xpath = '/museScore/Score/Staff[@id="1"]'
        if not xml_root.xpath(xpath + '/VBox'):
            vbox = lxml.etree.Element('VBox')
            height = lxml.etree.SubElement(vbox, 'height')
            height.text = '10'

            for element in xml_root.xpath(xpath):
                element.insert(0, vbox)

    def _get_tag(self, style):
        """
        :param string style: String inside the `<style>` tags
        """
        for element in self.xml_root.xpath('//VBox/Text'):
            if element.find('style').text == style:
                return element.find('text')

    def _get_text(self, style):
        """
        :param string style: String inside the `<style>` tags
        """
        element = self._get_tag(style)
        if hasattr(element, 'text'):
            return element.text

    def __getattr__(self, name):
        if name not in self.fields:
            raise AttributeError
        else:
            return self._get_text(name)

    def _create_text_tag(self, style, text):
        """
        :param string style: String inside the `<style>` tags
        """
        Text_tag = lxml.etree.Element('Text')
        style_tag = lxml.etree.SubElement(Text_tag, 'style')
        style_tag.text = style
        text_tag = lxml.etree.SubElement(Text_tag, 'text')
        text_tag.text = text
        for element in self.xml_root.xpath('//VBox'):
            element.append(Text_tag)

    def _set_text(self, style, text):
        """
        :param string style: String inside the `<style>` tags
        """
        element = self._get_tag(style)
        if hasattr(element, 'text'):
            element.text = text
        else:
            self._create_text_tag(style, text)

    def __setattr__(self, name, value):
        if name == 'xml_root' or name == 'fields':
            self.__dict__[name] = value
        elif name not in self.fields:
            raise AttributeError
        else:
            self._set_text(name, value)


class Combined(Tree):

    def __init__(self, fullpath):
        super(Combined, self).__init__(fullpath)
        if not self.error:
            self.meta = MetaTag(self.root)
            self.vbox = Vbox(self.root)

    def _pick_value(self, *values):
        for value in values:
            if value:
                return value

    @property
    def title(self):
        return self._pick_value(self.vbox.Title, self.meta.workTitle,
                                self.basename)

    @title.setter
    def title(self, value):
        self.vbox.Title = self.meta.workTitle = value

    @property
    def subtitle(self):
        return self._pick_value(self.vbox.Subtitle, self.meta.movementTitle)

    @subtitle.setter
    def subtitle(self, value):
        self.vbox.Subtitle = self.meta.movementTitle = value

    @property
    def composer(self):
        return self._pick_value(self.vbox.Composer, self.meta.composer)

    @composer.setter
    def composer(self, value):
        self.vbox.Composer = self.meta.composer = value

    @property
    def lyricist(self):
        return self._pick_value(self.vbox.Lyricist, self.meta.lyricist)

    @lyricist.setter
    def lyricist(self, value):
        self.vbox.Lyricist = self.meta.lyricist = value


class Meta(Tree):

    def __init__(self, fullpath):
        super(Meta, self).__init__(fullpath)

        if not self.error:
            self.meta = MetaTag(self.root)
            self.vbox = Vbox(self.root)

    def get(self, field):
        """Get a value by field.
        This function searches for values in this order: vbox, meta, filename.
        Possible fields are: title, subtitle, composer, lyricist
        """
        if field == 'title':
            values = [
                self.vbox.Title,
                self.meta.workTitle,
                self.basename
            ]
        elif field == 'subtitle':
            values = [
                self.vbox.Subtitle,
                self.meta.movementTitle,
            ]
        else:
            values = [
                getattr(self.vbox, field.title()),
                getattr(self.meta, field),
            ]

        for value in values:
            if value:
                return value

    def sync(self, field):
        if field == 'title':
            self.vbox.Title = self.meta.workTitle = self.get(field)
        elif field == 'subtitle':
            self.vbox.Subtitle = self.meta.movementTitle = self.get(field)
        else:
            setattr(self.vbox, field.title(), self.get(field))
            setattr(self.meta, field, self.get(field))

    def sync_fields(self):
        if not self.error:
            for field in ['title', 'subtitle', 'composer', 'lyricist']:
                self.sync(field)
            self.meta.clean()

    def show(self):
        print_desc('\n' + colored(self.filename, 'red'))
        print_desc(self.basename, 'filename', 'blue')
        if not self.error:
            for field in self.meta.fields:
                text = getattr(self.meta, field)
                if text:
                    print_desc(text, field, 'yellow')

            for field in self.vbox.fields:
                text = getattr(self.vbox, field)
                if text:
                    print_desc(text, field, 'green')

    def export_json(self):
        data = {}
        data['title'] = self.get('title')

        output = open(self.fullpath.replace(
            '.' + self.extension, '.json'), 'w')
        json.dump(data, output, indent=4)
        output.close()
