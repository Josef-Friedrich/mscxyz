"""Class for metadata maniplation"""

from __future__ import annotations

import json
import re
import typing
from pathlib import Path
from typing import Any

import lxml
import lxml.etree
import tmep
from lxml.etree import _Element

from mscxyz import utils
from mscxyz.settings import get_args

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


class ReadOnlyFieldError(Exception):
    def __init__(self, field: str) -> None:
        self.msg = "The field “{}” is read only!".format(field)
        Exception.__init__(self, self.msg)


class UnkownFieldError(Exception):
    def __init__(self, field: str, valid_fields: typing.Sequence[str]) -> None:
        self.msg = "Unkown field of name “{}”! Valid field names are: {}".format(
            field, ", ".join(valid_fields)
        )
        Exception.__init__(self, self.msg)


class UnmatchedFormatStringError(Exception):
    def __init__(self, format_string: str, input_string: str) -> None:
        self.msg = (
            "Your format string “{}” doesn’t match on this "
            "input string: “{}”".format(format_string, input_string)
        )
        Exception.__init__(self, self.msg)


class FormatStringNoFieldError(Exception):
    def __init__(self, format_string: str) -> None:
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


class Metatag:
    """
    The class provides access to the MuseScore metadata fields.

    The class should not be renamed to ``MetaTag`` because it would conflict with the
    naming scheme of the fields ``metatag_title`` etc.

    :see: `MuseScore Handbook <https://musescore.org/en/handbook/4/project-properties>`_

    The available ``metaTag`` fields are:

    * `arranger`
    * `audioComUrl` (new in v4)
    * `composer`
    * `copyright`
    * `creationDate`
    * `lyricist`
    * `movementNumber`
    * `movementTitle`
    * `mscVersion`
    * `platform`
    * `poet` (not in v4)
    * `source`
    * `sourceRevisionId`
    * `subtitle`
    * `translator`
    * `workNumber`
    * `workTitle`

    version 4

    .. code-block:: xml

            <museScore version="4.20">
                <Score>
                    <metaTag name="arranger"></metaTag>
                    <metaTag name="audioComUrl"></metaTag>
                    <metaTag name="composer">Composer / arranger</metaTag>
                    <metaTag name="copyright"></metaTag>
                    <metaTag name="creationDate">2024-01-05</metaTag>
                    <metaTag name="lyricist"></metaTag>
                    <metaTag name="movementNumber"></metaTag>
                    <metaTag name="movementTitle"></metaTag>
                    <metaTag name="platform">Linux</metaTag>
                    <metaTag name="source"></metaTag>
                    <metaTag name="sourceRevisionId"></metaTag>
                    <metaTag name="subtitle">Subtitle</metaTag>
                    <metaTag name="translator"></metaTag>
                    <metaTag name="workNumber"></metaTag>
                    <metaTag name="workTitle">Untitled score</metaTag>
    """

    fields = (
        "arranger",
        "audio_com_url",
        "composer",
        "copyright",
        "creation_date",
        "lyricist",
        "movement_number",
        "movement_title",
        "msc_version",
        "platform",
        "poet",
        "source",
        "source_revision_id",
        "subtitle",
        "translator",
        "work_number",
        "work_title",
    )

    score: "Score"

    xml_root: _Element

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.xml_root = score.xml_root

    def __get_element(self, field: str) -> _Element:
        score_element: _Element = self.score.xml.find_safe("Score")
        element: _Element | None = self.score.xml.xpath(
            '//metaTag[@name="' + field + '"]'
        )
        if element is None:
            element = self.score.xml.create_sub_element(
                score_element, "metaTag", "", attrib={"name": field}
            )
        return element

    def __get_text(self, field: str) -> str | None:
        element: _Element | None = self.__get_element(field)
        return self.score.xml.get_text(element)

    def __set_text(self, field: str, value: str | None) -> None:
        if value is None:
            return None
        element: _Element = self.__get_element(field)
        element.text = value

    # arranger

    @property
    def arranger(self) -> str | None:
        return self.__get_text("arranger")

    @arranger.setter
    def arranger(self, value: str | None) -> None:
        self.__set_text("arranger", value)

    # audio_com_url -> audioComUrl

    @property
    def audio_com_url(self) -> str | None:
        return self.__get_text("audioComUrl")

    @audio_com_url.setter
    def audio_com_url(self, value: str | None) -> None:
        self.__set_text("audioComUrl", value)

    # composer

    @property
    def composer(self) -> str | None:
        """Same text as "Composer" on the first page of the score"""
        return self.__get_text("composer")

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.__set_text("composer", value)

    # copyright

    @property
    def copyright(self) -> str | None:
        """Same text as "Copyright" on the first page of the score."""
        return self.__get_text("copyright")

    @copyright.setter
    def copyright(self, value: str | None) -> None:
        self.__set_text("copyright", value)

    # creation_date -> creationDate

    @property
    def creation_date(self) -> str | None:
        return self.__get_text("creationDate")

    @creation_date.setter
    def creation_date(self, value: str | None) -> None:
        self.__set_text("creationDate", value)

    # lyricist

    @property
    def lyricist(self) -> str | None:
        """Same text as “Lyricist” on the first page of the score."""
        return self.__get_text("lyricist")

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.__set_text("lyricist", value)

    # movement_number -> movementNumber

    @property
    def movement_number(self) -> str | None:
        return self.__get_text("movementNumber")

    @movement_number.setter
    def movement_number(self, value: str | None) -> None:
        self.__set_text("movementNumber", value)

    # movement_title -> movementTitle

    @property
    def movement_title(self) -> str | None:
        return self.__get_text("movementTitle")

    @movement_title.setter
    def movement_title(self, value: str | None) -> None:
        self.__set_text("movementTitle", value)

    # msc_version -> mscVersion

    @property
    def msc_version(self) -> str | None:
        return self.__get_text("mscVersion")

    @msc_version.setter
    def msc_version(self, value: str | None) -> None:
        self.__set_text("mscVersion", value)

    # platform

    @property
    def platform(self) -> str | None:
        """The computing platform the score was created on. This might be empty if the score was saved in test mode."""
        return self.__get_text("platform")

    @platform.setter
    def platform(self, value: str | None) -> None:
        self.__set_text("platform", value)

    # poet

    @property
    def poet(self) -> str | None:
        return self.__get_text("poet")

    @poet.setter
    def poet(self, value: str | None) -> None:
        self.__set_text("poet", value)

    # source

    @property
    def source(self) -> str | None:
        """May contain a URL if the score was downloaded from or Publish to MuseScore.com."""
        return self.__get_text("source")

    @source.setter
    def source(self, value: str | None) -> None:
        self.__set_text("source", value)

    # source_revision_id -> sourceRevisionId

    @property
    def source_revision_id(self) -> str | None:
        return self.__get_text("sourceRevisionId")

    @source_revision_id.setter
    def source_revision_id(self, value: str | None) -> None:
        self.__set_text("sourceRevisionId", value)

    # subtitle

    @property
    def subtitle(self) -> str | None:
        """
        The Subtitle. It has the same text as “Subtitle” on the first page of the score.
        """
        return self.__get_text("subtitle")

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.__set_text("subtitle", value)

    # translator

    @property
    def translator(self) -> str | None:
        return self.__get_text("translator")

    @translator.setter
    def translator(self, value: str | None) -> None:
        self.__set_text("translator", value)

    # work_number -> workNumber

    @property
    def work_number(self) -> str | None:
        return self.__get_text("workNumber")

    @work_number.setter
    def work_number(self, value: str | None) -> None:
        self.__set_text("workNumber", value)

    # work_title -> workTitle

    @property
    def work_title(self) -> str | None:
        """
        The Work Title. It has the same text as “Title” on the first page of the score.
        """
        return self.__get_text("workTitle")

    @work_title.setter
    def work_title(self, value: str | None) -> None:
        self.__set_text("workTitle", value)

    def clean(self) -> None:
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
    """The first `vertical` box of a score.

    Available fields:

    * `Composer`
    * `Lyricist`
    * `Subtitle`
    * `Title`

    Version 2, 3

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


    Version 4

    .. code-block:: xml

        <Staff id="1">
            <VBox>
                <height>10</height>
                <boxAutoSize>0</boxAutoSize>
                <eid>4294967418</eid>
                <Text>
                    <eid>8589934598</eid>
                    <style>title</style>
                    <text>Title</text>
                </Text>
                <Text>
                    <eid>12884901894</eid>
                    <style>composer</style>
                    <text>Composer</text>
                </Text>
            </VBox>
        </Staff>
    """

    fields = (
        "composer",
        "lyricist",
        "subtitle",
        "title",
    )

    score: "Score"

    xml_root: _Element

    vbox: _Element

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.xml_root = score.xml_root
        xpath = '/museScore/Score/Staff[@id="1"]'

        vbox = self.score.xml.xpath(xpath + "/VBox")
        if vbox is None:
            vbox = lxml.etree.Element("VBox")
            height = lxml.etree.SubElement(vbox, "height")
            height.text = "10"
            self.score.xml.xpath_safe(xpath).insert(0, vbox)
        self.vbox = vbox

    def __normalize_style_name(self, style: str) -> str:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        if self.score.version_major in (2, 3):
            style = style.title()
        elif self.score.version_major == 4:
            style = style.lower()
        return style

    def __get_element(self, style: str) -> _Element | None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        for element in self.vbox:
            s: _Element | None = element.find("style")
            if s is not None and s.text == self.__normalize_style_name(style):
                return element.find("text")
        return None

    def __get_text(self, style: str) -> str | None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer``.
        """
        element: _Element | None = self.__get_element(style)
        if element is not None and hasattr(element, "text"):
            return element.text
        return None

    def __create_text_element(self, style: str, text: str) -> None:
        """
        Version 2, 3

        .. code-block:: xml

            <Text>
                <style>Title</style>
                <text>Title</text>
            </Text>

        Version 4

        .. code-block:: xml

            <Text>
                <eid>8589934598</eid>
                <style>title</style>
                <text>Title</text>
            </Text>


        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        :param text: The string inside the ``<text>`` tags.
        """
        text_element: _Element = self.score.xml.create_element("Text")

        if self.score.version_major in (2, 3):
            style = style.title()
        elif self.score.version_major == 4:
            style = style.lower()

        self.score.xml.create_sub_element(
            text_element, "style", self.__normalize_style_name(style)
        )
        self.score.xml.create_sub_element(text_element, "text", text)
        self.vbox.append(text_element)

    def __set_text(self, style: str, text: str | None) -> None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """

        if text is None:
            self.__remove_text_element(style)
            return None

        element: _Element | None = self.__get_element(style)
        if hasattr(element, "text"):
            if element is not None:
                element.text = text
        else:
            self.__create_text_element(style, text)

    def __remove_text_element(self, style: str) -> None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        self.score.xml.remove(self.__get_element(style))
        return None

    # composer -> Composer

    @property
    def composer(self) -> str | None:
        return self.__get_text("Composer")

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.__set_text("Composer", value)

    # lyricist -> Lyricist

    @property
    def lyricist(self) -> str | None:
        return self.__get_text("Lyricist")

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.__set_text("Lyricist", value)

    # subtitle -> Subtitle

    @property
    def subtitle(self) -> str | None:
        return self.__get_text("Subtitle")

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.__set_text("Subtitle", value)

    # title -> Title

    @property
    def title(self) -> str | None:
        return self.__get_text("Title")

    @title.setter
    def title(self, value: str | None) -> None:
        self.__set_text("Title", value)


class Combined:
    """Combines the metadata fields of the embedded ``metaTag`` and ``VBox`` elements."""

    fields = (
        "composer",
        "lyricist",
        "subtitle",
        "title",
    )

    score: "Score"

    xml_root: _Element

    metatag: Metatag

    vbox: Vbox

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.xml_root = self.score.xml_root
        self.metatag = Metatag(self.score)
        self.vbox = Vbox(self.score)

    def _pick_value(self, *values: str | None) -> str | None:
        for value in values:
            if value:
                return value
        return None

    @property
    def title(self) -> str | None:
        return self._pick_value(self.vbox.title, self.metatag.work_title)

    @title.setter
    def title(self, value: str | None) -> None:
        self.vbox.title = self.metatag.work_title = value

    @property
    def subtitle(self) -> str | None:
        return self._pick_value(self.vbox.subtitle, self.metatag.movement_title)

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.vbox.subtitle = self.metatag.movement_title = value

    @property
    def composer(self) -> str | None:
        return self._pick_value(self.vbox.composer, self.metatag.composer)

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.vbox.composer = self.metatag.composer = value

    @property
    def lyricist(self) -> str | None:
        return self._pick_value(self.vbox.lyricist, self.metatag.lyricist)

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.vbox.lyricist = self.metatag.lyricist = value


class InterfaceReadWrite:
    objects = ("metatag", "vbox", "combined")

    score: "Score"

    metatag: Metatag

    vbox: Vbox

    combined: Combined

    fields: list[str]

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.metatag = Metatag(self.score)
        self.vbox = Vbox(self.score)
        self.combined = Combined(self.score)
        self.fields = self.get_all_fields()

    @staticmethod
    def get_all_fields() -> list[str]:
        fields: list[str] = []
        for field in Metatag.fields:
            fields.append("metatag_" + field)
        for field in Vbox.fields:
            fields.append("vbox_" + field)
        for field in Combined.fields:
            fields.append("combined_" + field)
        return sorted(fields)

    @staticmethod
    def __split(field: str) -> dict[str, str | Any]:
        match = re.search(r"([^_]*)_(.*)", field)
        if not match:
            raise ValueError("Field “" + field + "” can’t be splitted!")
        matches = match.groups()

        if matches[0] not in InterfaceReadWrite.objects:
            raise ValueError(matches[0] + ": Not a supported object!")
        return {"object": matches[0], "field": matches[1]}

    def export_to_dict(self) -> dict[str, str]:
        return export_to_dict(self, self.fields)

    def __getattr__(self, field: str) -> Any:
        parts = self.__split(field)
        obj = getattr(self, parts["object"])
        return getattr(obj, parts["field"])

    def __setattr__(self, field: str, value: str) -> None:
        if field in ("fields", "metatag", "objects", "vbox", "combined", "score"):
            self.__dict__[field] = value
        else:
            parts = self.__split(field)
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

    score: Score

    def __init__(self, score: Score) -> None:
        self.score = score

    @property
    def readonly_abspath(self) -> str:
        return str(self.score.path)

    @property
    def readonly_basename(self) -> str:
        return self.score.basename

    @property
    def readonly_dirname(self) -> str:
        return self.score.dirname

    @property
    def readonly_extension(self) -> str:
        return self.score.extension

    @property
    def readonly_filename(self) -> str:
        return self.score.filename

    @property
    def readonly_relpath(self) -> str:
        return str(self.score.path)

    @property
    def readonly_relpath_backup(self) -> str:
        return str(self.score.backup_file)


class Interface:
    score: "Score"

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.read_only = InterfaceReadOnly(self.score)
        self.read_write = InterfaceReadWrite(self.score)
        self.fields: list[str] = self.get_all_fields()

    @staticmethod
    def get_all_fields() -> list[str]:
        return sorted(InterfaceReadOnly.fields + InterfaceReadWrite.get_all_fields())

    def export_to_dict(self) -> dict[str, str]:
        return export_to_dict(self, self.fields)

    def __getattr__(self, field: str) -> Any:
        if re.match(r"^readonly_", field):
            return getattr(self.read_only, field)
        else:
            return getattr(self.read_write, field)

    def __setattr__(self, field: str, value: str) -> None:
        if field in ("score", "read_only", "read_write", "fields"):
            self.__dict__[field] = value
        elif not re.match(r"^readonly_", field):
            return setattr(self.read_write, field, value)
        else:
            raise ReadOnlyFieldError(field)


class Meta:
    score: "Score"

    metatag: Metatag

    vbox: Vbox

    combined: Combined

    interface_read_write: InterfaceReadWrite

    interface: Interface

    def __init__(self, score: "Score") -> None:
        self.score = score

        if not self.score.errors:
            self.metatag = Metatag(self.score)
            self.vbox = Vbox(self.score)
            self.combined = Combined(self.score)
            self.interface_read_write = InterfaceReadWrite(self.score)
            self.interface = Interface(self.score)

    def sync_fields(self) -> None:
        if not self.score.errors:
            self.combined.title = self.combined.title
            self.combined.subtitle = self.combined.subtitle
            self.combined.composer = self.combined.composer
            self.combined.lyricist = self.combined.lyricist

    def distribute_field(self, source_fields: str, format_string: str) -> None:
        f: list[str] = source_fields.split(",")
        for source_field in f:
            try:
                source = getattr(self.interface, source_field)
                results: dict[str, str] = distribute_field(source, format_string)
                if results:
                    for field, value in results.items():
                        setattr(self.interface, field, value)
                return
            except UnmatchedFormatStringError as error:
                self.score.errors.append(error)

    def write_to_log_file(self, log_file: str, format_string: str) -> None:
        log = open(log_file, "w")
        log.write(tmep.parse(format_string, self.interface.export_to_dict()) + "\n")
        log.close()

    def set_field(self, destination_field: str, format_string: str) -> None:
        field_value = tmep.parse(format_string, self.interface.export_to_dict())
        setattr(self.interface, destination_field, field_value)

    def clean_metadata(self, fields_spec: typing.Literal["all"] | str) -> None:
        """
        Clean the metadata fields of the object.

        :param fields_spec: Specification of the fields to clean. It can be either
            ``all`` to clean all fields, or a comma-separated string specifying
            individual fields.
        """
        fields: list[str]
        if fields_spec == "all":
            fields = self.interface_read_write.fields
        else:
            fields = fields_spec.split(",")
        for field in fields:
            setattr(self.interface_read_write, field, "")

    def delete_duplicates(self) -> None:
        """
        Delete duplicates in the metadata.

        This method checks if the ``combined_lyricist`` and ``combined_composer`` are the same,
        and if so, it sets ``combined_lyricist`` to an empty string.

        It also checks if ``combined_title`` is empty but ``combined_subtitle`` is not,
        and if so, it sets ``combined_title`` to ``combined_subtitle``.

        Finally, it checks if ``combined_subtitle`` is the same as ``combined_title``,
        and if so, it sets ``combined_subtitle`` to an empty string.
        """
        iface: Interface = self.interface
        if iface.combined_lyricist == iface.combined_composer:
            iface.combined_lyricist = ""

        if not iface.combined_title and iface.combined_subtitle:
            iface.combined_title = iface.combined_subtitle

        if iface.combined_subtitle == iface.combined_title:
            iface.combined_subtitle = ""

    def show(self, pre: dict[str, str], post: dict[str, str]) -> None:
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
            field_color: utils.Color
            if (
                args.general_verbose == 0
                and (field in pre and pre[field] or field in post and post[field])
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

                line: list[str] = []
                if pre[field]:
                    line.append("“{}”".format(pre[field]))

                if pre[field] != post[field]:
                    line.append("->")
                    line.append(utils.color("“{}”".format(post[field]), "yellow"))

                print("{}: {}".format(utils.color(field, field_color), " ".join(line)))

    def export_json(self) -> Path:
        """
        Export the data as a JSON file.

        :return: The path to the exported JSON file.
        """
        data: dict[str, str] = {}
        result_path: Path = self.score.json_file
        for field in self.interface.fields:
            data[field] = self.interface.__getattr__(field)
        output = open(result_path, "w")
        json.dump(data, output, indent=4)
        output.close()
        return result_path

    def reload(self, save: bool = False) -> Meta:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Meta object.

        :see: :meth:`mscxyz.score.Score.reload`
        """
        return self.score.reload(save).meta
