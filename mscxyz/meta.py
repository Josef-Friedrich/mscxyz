"""Class for metadata maniplation"""

from __future__ import annotations

import json
import re
import typing

import lxml
import lxml.etree
import tmep
from lxml.etree import _Element

from mscxyz.score_file_classes import MscoreXmlTree
from mscxyz.utils import color, get_args

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


class ReadOnlyFieldError(Exception):
    def __init__(self, field: str):
        self.msg = "The field “{}” is read only!".format(field)
        Exception.__init__(self, self.msg)


class UnkownFieldError(Exception):
    def __init__(self, field: str, valid_fields: typing.Sequence[str]):
        self.msg = "Unkown field of name “{}”! Valid field names are: {}".format(
            field, ", ".join(valid_fields)
        )
        Exception.__init__(self, self.msg)


class UnmatchedFormatStringError(Exception):
    def __init__(self, format_string: str, input_string: str):
        self.msg = (
            "Your format string “{}” doesn’t match on this "
            "input string: “{}”".format(format_string, input_string)
        )
        Exception.__init__(self, self.msg)


class FormatStringNoFieldError(Exception):
    def __init__(self, format_string: str):
        self.msg = "No fields found in your format string “{}”!".format(format_string)
        Exception.__init__(self, self.msg)


def distribute_field(source: str, format_string: str) -> dict[str, str]:
    """
    Distributes the values from the source string into a dictionary based on the format string.

    :param source: The source string from which values will be extracted.
    :param format_string: The format string that specifies the pattern of the values to be extracted.
    :return: A dictionary mapping field names to their corresponding values.
    :raises FormatStringNoFieldError: If the format string does not contain any field markers.
    :raises UnmatchedFormatStringError: If the format string does not match the source string.
    """
    fields = re.findall(r"\$([a-z_]*)", format_string)
    if not fields:
        raise FormatStringNoFieldError(format_string)
    regex = re.sub(r"\$[a-z_]*", "(.*)", format_string)
    match = re.search(regex, source)
    if not match:
        raise UnmatchedFormatStringError(format_string, source)
    values = match.groups()
    return dict(zip(fields, values))


def to_underscore(field: str) -> str:
    """
    Convert a camel case string to snake case.

    :param field: The camel case string to be converted.
    :return: The snake case representation of the input string.
    """
    return re.sub("([A-Z]+)", r"_\1", field).lower()


def export_to_dict(obj: object, fields: typing.Iterable[str]) -> dict[str, str]:
    """
    Export the specified fields of an object to a dictionary.

    :param obj: The object to export.
    :param fields: The fields to include in the dictionary.

    :return: A dictionary containing the specified fields and their values.
    """
    out: dict[str, str] = {}
    for field in fields:
        value = getattr(obj, field)
        if not value:
            value = ""
        out[field] = value
    return out


class MetaTag:

    """The available metaTag fields are:

    * `arranger`
    * `composer`
    * `copyright`
    * `creationDate`
    * `lyricist`
    * `movementNumber`
    * `movementTitle`
    * `platform`
    * `poet`
    * `source`
    * `translator`
    * `workNumber`
    * `workTitle`

    """

    fields = (
        "arranger",
        "composer",
        "copyright",
        "creationDate",
        "lyricist",
        "movementNumber",
        "movementTitle",
        "platform",
        "poet",
        "source",
        "translator",
        "workNumber",
        "workTitle",
    )

    xml_root: _Element

    @staticmethod
    def _to_camel_case(field: str) -> str:
        return re.sub(r"(?!^)_([a-zA-Z])", lambda match: match.group(1).upper(), field)

    def __init__(self, xml_root: _Element) -> None:
        self.xml_root = xml_root

    def _get_element(self, field: str) -> _Element | None:
        for element in self.xml_root.xpath('//metaTag[@name="' + field + '"]'):
            return element

    def _get_text(self, field: str) -> str | None:
        element: _Element | None = self._get_element(field)
        if hasattr(element, "text"):
            return element.text

    def __getattr__(self, field: str):
        field = self._to_camel_case(field)
        if field not in self.fields:
            raise UnkownFieldError(field, self.fields)
        else:
            return self._get_text(field)

    def __setattr__(self, field: str, value: str) -> None:
        if field == "xml_root" or field == "fields":
            self.__dict__[field] = value
        else:
            field = self._to_camel_case(field)
            self._get_element(field).text = value

    def clean(self):
        fields = (
            "arranger",
            "copyright",
            "creationDate",
            "movementNumber",
            "platform",
            "poet",
            "source",
            "translator",
            "workNumber",
        )
        for field in fields:
            setattr(self, field, "")


class Vbox:
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
        "Composer",
        "Lyricist",
        "Subtitle",
        "Title",
    )

    xml_root: _Element

    def __init__(self, xml_root: _Element):
        self.xml_root = xml_root
        xpath = '/museScore/Score/Staff[@id="1"]'
        if not xml_root.xpath(xpath + "/VBox"):
            vbox = lxml.etree.Element("VBox")
            height = lxml.etree.SubElement(vbox, "height")
            height.text = "10"

            for element in xml_root.xpath(xpath):
                element.insert(0, vbox)

    def _get_tag(self, style: str) -> _Element | None:
        """
        :param style: String inside the `<style>` tags
        """
        x: _XPathObject = self.xml_root.xpath("//VBox/Text")
        if isinstance(x, list):
            for element in x:
                if isinstance(element, _Element):
                    s: _Element | None = element.find("style")
                    if s is not None and s.text == style:
                        return element.find("text")

    def _get_text(self, style: str) -> str | None:
        """
        :param style: String inside the `<style>` tags
        """
        element: _Element | None = self._get_tag(style)
        if element is not None and hasattr(element, "text"):
            return element.text

    def __getattr__(self, field: str) -> str | None:
        field = field.title()
        if field not in self.fields:
            raise UnkownFieldError(field, self.fields)
        else:
            return self._get_text(field)

    def _create_text_tag(self, style: str, text: str):
        """
        :param style: String inside the `<style>` tags
        """
        Text_tag: _Element = lxml.etree.Element("Text")
        style_tag: _Element = lxml.etree.SubElement(Text_tag, "style")
        style_tag.text = style
        text_tag: _Element = lxml.etree.SubElement(Text_tag, "text")
        text_tag.text = text
        for element in self.xml_root.xpath("//VBox"):
            element.append(Text_tag)

    def _set_text(self, style, text):
        """
        :param string style: String inside the `<style>` tags
        """
        element = self._get_tag(style)
        if hasattr(element, "text"):
            element.text = text
        else:
            self._create_text_tag(style, text)

    def __setattr__(self, field, value):
        if field == "xml_root" or field == "fields":
            self.__dict__[field] = value
        elif field.title() not in self.fields:
            raise UnkownFieldError(field, self.fields)
        else:
            self._set_text(field.title(), value)


class Combined(MscoreXmlTree):
    fields = (
        "composer",
        "lyricist",
        "subtitle",
        "title",
    )

    xml_root: _Element

    def __init__(self, xml_root: _Element):
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


class InterfaceReadWrite:
    objects = ("metatag", "vbox", "combined")

    def __init__(self, xml_root: _Element) -> None:
        self.metatag = MetaTag(xml_root)
        self.vbox = Vbox(xml_root)
        self.combined = Combined(xml_root)
        self.fields = self.get_all_fields()

    @staticmethod
    def get_all_fields() -> list[str]:
        fields: list[str] = []
        for field in MetaTag.fields:
            fields.append("metatag_" + to_underscore(field))
        for field in Vbox.fields:
            fields.append("vbox_" + field.lower())
        for field in Combined.fields:
            fields.append("combined_" + field)
        return sorted(fields)

    @staticmethod
    def _split(field: str):
        match = re.search(r"([^_]*)_(.*)", field)
        if not match:
            raise ValueError("Field “" + field + "” can’t be splitted!")
        matches = match.groups()

        if matches[0] not in InterfaceReadWrite.objects:
            raise ValueError(matches[0] + ": Not a supported object!")
        return {"object": matches[0], "field": matches[1]}

    def export_to_dict(self):
        return export_to_dict(self, self.fields)

    def __getattr__(self, field):
        parts = self._split(field)
        obj = getattr(self, parts["object"])
        return getattr(obj, parts["field"])

    def __setattr__(self, field, value):
        if field in ("fields", "metatag", "objects", "vbox", "combined"):
            self.__dict__[field] = value
        else:
            parts = self._split(field)
            obj = getattr(self, parts["object"])
            return setattr(obj, parts["field"], value)


class InterfaceReadOnly:
    fields = [
        "readonly_abspath",
        "readonly_basename",
        "readonly_dirname",
        "readonly_extension",
        "readonly_filename",
        "readonly_relpath",
        "readonly_relpath_backup",
    ]

    xml_tree: MscoreXmlTree

    def __init__(self, tree: MscoreXmlTree):
        self.xml_tree = tree

    @property
    def readonly_abspath(self) -> str:
        return self.xml_tree.abspath

    @property
    def readonly_basename(self) -> str:
        return self.xml_tree.basename

    @property
    def readonly_dirname(self) -> str:
        return self.xml_tree.dirname

    @property
    def readonly_extension(self) -> str:
        return self.xml_tree.extension

    @property
    def readonly_filename(self) -> str:
        return self.xml_tree.filename

    @property
    def readonly_relpath(self) -> str:
        return self.xml_tree.relpath

    @property
    def readonly_relpath_backup(self) -> str:
        return self.xml_tree.relpath_backup


class Interface:
    xml_tree: MscoreXmlTree

    def __init__(self, tree: MscoreXmlTree):
        self.xml_tree = tree
        self.read_only = InterfaceReadOnly(tree)
        self.read_write = InterfaceReadWrite(tree.xml_root)
        self.fields = self.get_all_fields()

    @staticmethod
    def get_all_fields():
        return sorted(InterfaceReadOnly.fields + InterfaceReadWrite.get_all_fields())

    def export_to_dict(self):
        return export_to_dict(self, self.fields)

    def __getattr__(self, field: str):
        if re.match(r"^readonly_", field):
            return getattr(self.read_only, field)
        else:
            return getattr(self.read_write, field)

    def __setattr__(self, field: str, value):
        if field in ("xml_tree", "read_only", "read_write", "fields"):
            self.__dict__[field] = value
        elif not re.match(r"^readonly_", field):
            return setattr(self.read_write, field, value)
        else:
            raise ReadOnlyFieldError(field)


class Meta(MscoreXmlTree):
    def __init__(self, relpath: str):
        super(Meta, self).__init__(relpath)

        if not self.errors:
            self.metatag = MetaTag(self.xml_root)
            self.vbox = Vbox(self.xml_root)
            self.combined = Combined(self.xml_root)
            self.interface_read_write = InterfaceReadWrite(self.xml_root)
            self.interface = Interface(self)

    def sync_fields(self):
        if not self.errors:
            self.combined.title = self.combined.title
            self.combined.subtitle = self.combined.subtitle
            self.combined.composer = self.combined.composer
            self.combined.lyricist = self.combined.lyricist

    def distribute_field(self, source_fields, format_string):
        source_fields = source_fields.split(",")
        for source_field in source_fields:
            try:
                source = getattr(self.interface, source_field)
                results = distribute_field(source, format_string)
                if results:
                    for field, value in results.items():
                        setattr(self.interface, field, value)
                return
            except UnmatchedFormatStringError as error:
                self.errors.append(error)

    def write_to_log_file(self, log_file, format_string):
        log = open(log_file, "w")
        log.write(tmep.parse(format_string, self.interface.export_to_dict()) + "\n")
        log.close()

    def set_field(self, destination_field, format_string):
        field_value = tmep.parse(format_string, self.interface.export_to_dict())
        setattr(self.interface, destination_field, field_value)

    def clean(self, fields):
        fields = fields[0]
        if fields == "all":
            fields = self.interface_read_write.fields
        else:
            fields = fields.split(",")
        for field in fields:
            setattr(self.interface_read_write, field, "")

    def delete_duplicates(self):
        iface = self.interface
        if iface.combined_lyricist == iface.combined_composer:
            iface.combined_lyricist = ""

        if not iface.combined_title and iface.combined_subtitle:
            iface.combined_title = iface.combined_subtitle

        if iface.combined_subtitle == iface.combined_title:
            iface.combined_subtitle = ""

    def show(self, pre, post):
        args = get_args()

        fields = list(self.interface.fields)

        if args.general_verbose < 1:
            fields.remove("readonly_abspath")
            fields.remove("readonly_dirname")
            fields.remove("readonly_extension")
            fields.remove("readonly_filename")
            fields.remove("readonly_relpath")

        if args.general_verbose < 2:
            fields.remove("readonly_relpath_backup")

        for field in fields:
            if (
                args.general_verbose == 0 and (pre[field] or post[field])
            ) or args.general_verbose > 0:
                if re.match(r"^combined_", field):
                    field_color = "green"
                elif re.match(r"^metatag_", field):
                    field_color = "blue"
                elif re.match(r"^readonly_", field):
                    field_color = "red"
                elif re.match(r"^vbox_", field):
                    field_color = "cyan"
                else:
                    field_color = "white"

                line = []
                if pre[field]:
                    line.append("“{}”".format(pre[field]))

                if pre[field] != post[field]:
                    line.append("->")
                    line.append(color("“{}”".format(post[field]), "yellow"))

                print("{}: {}".format(color(field, field_color), " ".join(line)))

    def export_json(self):
        data = {}
        data["title"] = self.get("title")

        output = open(self.relpath.replace("." + self.extension, ".json"), "w")
        json.dump(data, output, indent=4)
        output.close()
