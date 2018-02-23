# -*- coding: utf-8 -*-

"""Class for metadata maniplation"""

from mscxyz.tree import Tree
from mscxyz.utils import print_desc
from termcolor import colored
import lxml
import six
import json
import re


def distribute_field(source, format_string):
    fields = re.findall(r'\$([a-z_]*)', format_string)
    regex = re.sub(r'\$[a-z_]*', '(.*)', format_string)
    match = re.search(regex, source)
    values = match.groups()
    return dict(zip(fields, values))


def to_underscore(field):
    return re.sub('([A-Z]+)', r'_\1', field).lower()


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

    def _get_element(self, field):
        for element in self.xml_root.xpath('//metaTag[@name="' + field + '"]'):
            return element

    def _get_text(self, field):
        element = self._get_element(field)
        if hasattr(element, 'text'):
            return element.text

    def __getattr__(self, field):
        field = self._to_camel_case(field)
        if field not in self.fields:
            raise AttributeError('No field named: “' + field + '”!')
        else:
            return self._get_text(field)

    def __setattr__(self, field, value):
        if field == 'xml_root' or field == 'fields':
            self.__dict__[field] = value
        else:
            field = self._to_camel_case(field)
            self._get_element(field).text = value

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
            raise AttributeError('No field named: “' + field + '”!')
        else:
            self._set_text(field.title(), value)


class Combined(Tree):

    fields = (
        'composer',
        'lyricist',
        'subtitle',
        'title',
    )

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

    objects = ('metatag', 'vbox', 'combined')

    def __init__(self, xml_root):
        self.metatag = MetaTag(xml_root)
        self.vbox = Vbox(xml_root)
        self.combined = Combined(xml_root)
        self.fields = self.get_all_fields()

    @staticmethod
    def get_all_fields():
        fields = []
        for field in MetaTag.fields:
            fields.append('metatag_' + to_underscore(field))
        for field in Vbox.fields:
            fields.append('vbox_' + field.lower())
        for field in Combined.fields:
            fields.append('combined_' + field)
        return sorted(fields)

    @staticmethod
    def _split(field):
        match = re.search(r'([^_]*)_(.*)', field)
        if not match:
            raise ValueError('Field “' + field + '” can’t be splitted!')
        matches = match.groups()

        if not matches[0] in UnifedInterface.objects:
            raise ValueError(matches[0] + ': Not a supported object!')
        return {'object': matches[0], 'field': matches[1]}

    def export_to_dict(self):
        out = {}
        for field in self.fields:
            value = getattr(self, field)
            if not value:
                value = ''
            out[field] = value
        return out

    def __getattr__(self, field):
        parts = self._split(field)
        obj = getattr(self, parts['object'])
        return getattr(obj, parts['field'])

    def __setattr__(self, field, value):
        if field in ('fields', 'metatag', 'objects', 'vbox', 'combined'):
            self.__dict__[field] = value
        else:
            parts = self._split(field)
            obj = getattr(self, parts['object'])
            return setattr(obj, parts['field'], value)


class InterfaceReadOnly(object):

    fields = (
        'readonly_basename',
        'readonly_dirname',
        'readonly_extension',
        'readonly_filename',
        'readonly_fullpath',
        'readonly_fullpath_backup',
    )

    def __init__(self, tree):
        self.tree = tree

    @property
    def readonly_fullpath(self):
        return self.tree.fullpath

    @property
    def readonly_extension(self):
        return self.tree.extension

    @property
    def readonly_fullpath_backup(self):
        return self.tree.fullpath_backup

    @property
    def readonly_dirname(self):
        return self.tree.dirname

    @property
    def readonly_filename(self):
        return self.tree.filename

    @property
    def readonly_basename(self):
        return self.tree.basename


class Meta(Tree):

    def __init__(self, fullpath):
        super(Meta, self).__init__(fullpath)

        if not self.error:
            self.metatag = MetaTag(self.root)
            self.vbox = Vbox(self.root)
            self.combined = Combined(self.root)
            self.interface = UnifedInterface(self.root)

    def sync_fields(self):
        if not self.error:
            self.combined.title = self.combined.title
            self.combined.subtitle = self.combined.subtitle
            self.combined.composer = self.combined.composer
            self.combined.lyricist = self.combined.lyricist

    def distribute_field(self, source_field, format_string):
        source = getattr(self.interface, source_field)
        results = distribute_field(source, format_string)
        for field, value in results.items():
            setattr(self.interface, field, value)

    def clean(self, fields):
        fields = fields[0]
        if fields == 'all':
            fields = self.interface.fields
        else:
            fields = fields.split(',')
        for field in fields:
            setattr(self.interface, field, '')

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
