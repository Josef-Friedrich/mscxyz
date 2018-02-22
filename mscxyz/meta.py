# -*- coding: utf-8 -*-

"""Class for metadata maniplation"""

from mscxyz.tree import Tree
from mscxyz.utils import print_desc
from termcolor import colored
import lxml
import six
import json
import re


def copy_field(source, destination):
    fields = re.findall(r'\$([a-z_]*)', destination)
    regex = re.sub(r'\$[a-z_]*', '(.*)', destination)
    match = re.search(regex, source)
    values = match.groups()
    return dict(zip(fields, values))


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

    @staticmethod
    def _to_camel_case(field):
        return re.sub(r'(?!^)_([a-zA-Z])',
                      lambda match: match.group(1).upper(), field)

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
        name = self._to_camel_case(name)
        if name not in self.fields:
            raise AttributeError
        else:
            return self._get_text(name)

    def __setattr__(self, name, value):
        if name == 'xml_root' or name == 'fields':
            self.__dict__[name] = value
        else:
            name = self._to_camel_case(name)
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

    def __getattr__(self, field):
        field = field.title()
        if field not in self.fields:
            raise AttributeError
        else:
            return self._get_text(field)

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

    def __setattr__(self, field, value):
        if field == 'xml_root' or field == 'fields':
            self.__dict__[field] = value
        elif field.title() not in self.fields:
            raise AttributeError
        else:
            self._set_text(field.title(), value)


class Combined(Tree):

    def __init__(self, xml_root):
        self.xml_root = xml_root
        self.metatag = MetaTag(xml_root)
        self.vbox = Vbox(xml_root)

    def _pick_value(self, *values):
        for value in values:
            if value:
                return value

    @property
    def title(self):
        return self._pick_value(self.vbox.Title, self.metatag.workTitle)

    @title.setter
    def title(self, value):
        self.vbox.Title = self.metatag.workTitle = value

    @property
    def subtitle(self):
        return self._pick_value(self.vbox.Subtitle, self.metatag.movementTitle)

    @subtitle.setter
    def subtitle(self, value):
        self.vbox.Subtitle = self.metatag.movementTitle = value

    @property
    def composer(self):
        return self._pick_value(self.vbox.Composer, self.metatag.composer)

    @composer.setter
    def composer(self, value):
        self.vbox.Composer = self.metatag.composer = value

    @property
    def lyricist(self):
        return self._pick_value(self.vbox.Lyricist, self.metatag.lyricist)

    @lyricist.setter
    def lyricist(self, value):
        self.vbox.Lyricist = self.metatag.lyricist = value


class UnifedInterface(object):

    def __init__(self, xml_root):
        self.metatag = MetaTag(xml_root)
        self.vbox = Vbox(xml_root)
        self.combined = Combined(xml_root)

    @staticmethod
    def _split(field):
        match = re.search(r'([^_]*)_(.*)', field)
        if not match:
            raise ValueError('Field “' + field + '” can’t be split!')
        matches = match.groups()

        return {'object': matches[0], 'field': matches[1]}

    def __getattr__(self, field):
        parts = self._split(field)
        obj = getattr(self, parts['object'])
        return getattr(obj, parts['field'])


class Meta(Tree):

    def __init__(self, fullpath):
        super(Meta, self).__init__(fullpath)

        if not self.error:
            self.metatag = MetaTag(self.root)
            self.vbox = Vbox(self.root)

    def get(self, field):
        """Get a value by field.
        This function searches for values in this order: vbox, metatag, filename.
        Possible fields are: title, subtitle, composer, lyricist
        """
        if field == 'title':
            values = [
                self.vbox.Title,
                self.metatag.workTitle,
                self.basename
            ]
        elif field == 'subtitle':
            values = [
                self.vbox.Subtitle,
                self.metatag.movementTitle,
            ]
        else:
            values = [
                getattr(self.vbox, field.title()),
                getattr(self.metatag, field),
            ]

        for value in values:
            if value:
                return value

    def sync(self, field):
        if field == 'title':
            self.vbox.Title = self.metatag.workTitle = self.get(field)
        elif field == 'subtitle':
            self.vbox.Subtitle = self.metatag.movementTitle = self.get(field)
        else:
            setattr(self.vbox, field.title(), self.get(field))
            setattr(self.metatag, field, self.get(field))

    def sync_fields(self):
        if not self.error:
            for field in ['title', 'subtitle', 'composer', 'lyricist']:
                self.sync(field)
            self.metatag.clean()

    def show(self):
        print_desc('\n' + colored(self.filename, 'red'))
        print_desc(self.basename, 'filename', 'blue')
        if not self.error:
            for field in self.metatag.fields:
                text = getattr(self.metatag, field)
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
