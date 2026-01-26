"""Provide fields ($variable) for the path templates."""

from __future__ import annotations

import json
import re
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence, Union

import tmep

from mscxyz.meta import FormatStringNoFieldError, UnmatchedFormatStringError
from mscxyz.settings import DefaultArguments
from mscxyz.utils import Color, colorize

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


FieldValue = Union[str, int, float]
FieldsExport = Mapping[str, FieldValue]


@dataclass
class Field:
    name: str
    """
    ``name`` will become ``$name`` in the path templates
    """

    description: str
    """
    Some description text for the documentation.
    """

    attr_path: str
    """``meta.title`` accesses ``score.meta.title``"""

    verbosity: int = 1
    """Verbosity level indicating if the field should be displayed in the debug output."""

    color: Color = "white"
    """The color of the field in the debug output."""

    readonly: bool = False


class FieldsManager:
    score: "Score"

    fields = (
        # Combined
        Field(name="title", description="The combined title", attr_path="meta.title"),
        Field(
            name="subtitle",
            description="The combined subtitle",
            attr_path="meta.subtitle",
            color="green",
        ),
        Field(
            name="composer",
            description="The combined composer",
            attr_path="meta.composer",
            color="green",
        ),
        Field(
            name="lyricist",
            description="The combined lyricist",
            attr_path="meta.lyricist",
            color="green",
        ),
        # vbox
        Field(
            name="vbox_title",
            description="The title field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.title",
            color="cyan",
        ),
        Field(
            name="vbox_subtitle",
            description="The subtitle field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.subtitle",
            color="cyan",
        ),
        Field(
            name="vbox_composer",
            description="The composer field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.composer",
            color="cyan",
        ),
        Field(
            name="vbox_lyricist",
            description="The lyricist field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.lyricist",
            color="cyan",
        ),
        # metatag
        Field(
            name="metatag_arranger",
            description="The arranger field stored as project properties.",
            attr_path="meta.metatag.arranger",
            color="blue",
        ),
        Field(
            name="metatag_audio_com_url",
            description="The audio.com URL field stored as project properties.",
            attr_path="meta.metatag.audio_com_url",
            color="blue",
        ),
        Field(
            name="metatag_composer",
            description="The composer field stored as project properties.",
            attr_path="meta.metatag.composer",
            color="blue",
        ),
        Field(
            name="metatag_copyright",
            description="The copyright field stored as project properties.",
            attr_path="meta.metatag.copyright",
            color="blue",
        ),
        Field(
            name="metatag_creation_date",
            description="The creation date field stored as project properties.",
            attr_path="meta.metatag.creation_date",
            color="blue",
        ),
        Field(
            name="metatag_lyricist",
            description="The lyricist field stored as project properties.",
            attr_path="meta.metatag.lyricist",
            color="blue",
        ),
        Field(
            name="metatag_movement_number",
            description="The movement number field stored as project properties.",
            attr_path="meta.metatag.movement_number",
            color="blue",
        ),
        Field(
            name="metatag_movement_title",
            description="The movement title field stored as project properties.",
            attr_path="meta.metatag.movement_title",
            color="blue",
        ),
        Field(
            name="metatag_msc_version",
            description="The MuseScore version field stored as project properties.",
            attr_path="meta.metatag.msc_version",
            color="blue",
        ),
        Field(
            name="metatag_platform",
            description="The platform field stored as project properties.",
            attr_path="meta.metatag.platform",
            color="blue",
        ),
        Field(
            name="metatag_poet",
            description="The poet field stored as project properties.",
            attr_path="meta.metatag.poet",
            color="blue",
        ),
        Field(
            name="metatag_source",
            description="The source field stored as project properties.",
            attr_path="meta.metatag.source",
            color="blue",
        ),
        Field(
            name="metatag_source_revision_id",
            description="The source revision ID field stored as project properties.",
            attr_path="meta.metatag.source_revision_id",
            color="blue",
        ),
        Field(
            name="metatag_subtitle",
            description="The subtitle field stored as project properties.",
            attr_path="meta.metatag.subtitle",
            color="blue",
        ),
        Field(
            name="metatag_translator",
            description="The translator field stored as project properties.",
            attr_path="meta.metatag.translator",
            color="blue",
        ),
        Field(
            name="metatag_work_number",
            description="The work number field stored as project properties.",
            attr_path="meta.metatag.work_number",
            color="blue",
        ),
        Field(
            name="metatag_work_title",
            description="The work title field stored as project properties.",
            attr_path="meta.metatag.work_title",
            color="blue",
        ),
        # Readonly
        Field(
            name="version",
            description="The MuseScore version as a floating point number, "
            "for example ``2.03``, ``3.01`` or ``4.20``.",
            attr_path="version",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="version_major",
            description="The major MuseScore version, for example ``2``, ``3`` or ``4``.",
            attr_path="version_major",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="program_version",
            description="The semantic version number of the MuseScore program, for example: ``4.2.0``.",
            attr_path="program_version",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="program_revision",
            description="The revision number of the MuseScore program, for example: ``eb8d33c``.",
            attr_path="program_revision",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="path",
            description="The absolute path of the MuseScore file, for example ``/home/xyz/score.mscz``.",
            attr_path="path",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="backup_file",
            description="The absolute path of the backup file. "
            "The string ``_bak`` is appended to the file name before the extension.",
            attr_path="backup_file",
            verbosity=3,
            readonly=True,
        ),
        Field(
            name="json_file",
            description="The absolute path of the JSON file in which the metadata can be exported.",
            attr_path="json_file",
            verbosity=3,
            readonly=True,
        ),
        Field(
            name="dirname",
            description="The name of the containing directory of the MuseScore file, for "
            "example: ``/home/xyz/score_files``.",
            attr_path="dirname",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="filename",
            description="The filename of the MuseScore file, for example:"
            "``score.mscz``.",
            attr_path="filename",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="basename",
            description="The basename of the score file, for example: ``score``.",
            attr_path="basename",
            verbosity=2,
            readonly=True,
        ),
        Field(
            name="extension",
            description="The extension (``mscx`` or ``mscz``) of the score file.",
            attr_path="extension",
            verbosity=2,
            readonly=True,
        ),
    )

    __fields_by_name: dict[str, Field]

    pre: dict[str, FieldValue]
    """The state of the field values at initialization, stored as a dictionary."""

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.__fields_by_name = {}
        for field in self.fields:
            if field.name in self.__fields_by_name:
                raise Exception("Duplicate field name")
            self.__fields_by_name[field.name] = field
        self.pre = self.export_to_dict()

    def __iter__(self) -> Iterator[Field]:
        return iter(self.fields)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self.__fields_by_name.keys())

    def get_field(self, name: str) -> Field:
        return self.__fields_by_name[name]

    def get(self, name: str) -> Any | None:
        field = self.get_field(name)
        attrs = field.attr_path.split(".")
        value = self.score
        for attr in attrs:
            value = getattr(value, attr)
            if value is None:
                break
        return value

    def set(self, name: str, value: Any) -> None:
        field = self.get_field(name)
        attrs = field.attr_path.split(".")
        last = attrs.pop()
        obj = self.score
        for attr in attrs:
            obj = getattr(obj, attr)
            if obj is None:
                raise Exception(f"Cannot set attribute {field.attr_path}")
        if value is not None and isinstance(value, str) and "$" in value:
            value = tmep.parse(value, self.export_to_dict())
        setattr(obj, last, value)

    def diff(self, args: DefaultArguments) -> None:
        if args.info_verbose == 0:
            return
        pre = self.pre

        post = self.export_to_dict()
        print("")

        for name in self.names:
            if name in pre and pre[name] or name in post and post[name]:
                field = self.get_field(name)
                if field.verbosity > args.info_verbose:
                    continue

                pre_value = None
                if name in pre:
                    pre_value = pre[name]

                post_value = None
                if name in post:
                    post_value = post[name]

                line: list[str] = []
                if pre_value:
                    line.append(f"“{pre_value}”")

                if pre_value != post_value:
                    line.append("->")
                    if post_value:
                        line.append(colorize(f"“{post_value}”", "yellow"))

                print(f"{colorize(name, field.color)}: {' '.join(line)}")

    def export_to_dict(self) -> dict[str, FieldValue]:
        output: dict[str, FieldValue] = {}
        for field in self.names:
            value = self.get(field)
            if value:
                if isinstance(value, Path):
                    value = str(value)
                output[field] = value
        return output

    def distribute(self, source_fields: str, format_string: str) -> None:
        f: list[str] = source_fields.split(",")
        for source_field in f:
            source = self.get(source_field)
            source = str(source)

            fields = re.findall(r"\$([a-z_]*)", format_string)
            if not fields:
                raise FormatStringNoFieldError(format_string)
            regex = re.sub(r"\$[a-z_]*", "(.*)", format_string)
            match = re.search(regex, source)
            if not match:
                raise UnmatchedFormatStringError(format_string, source)
            values = match.groups()
            results: dict[str, str] = dict(zip(fields, values))
            if results:
                for field, value in results.items():
                    self.set(field, value)
            return

    def clean(self, fields_spec: str) -> None:
        fields: Sequence[str]
        if fields_spec == "all":
            fields = self.names
        else:
            fields = fields_spec.split(",")

        for name in fields:
            field = self.get_field(name)
            if not field.readonly:
                self.set(name, None)

    def export_json(self) -> Path:
        """
        Export the data as a JSON file.

        :return: The path to the exported JSON file.
        """
        result_path: Path = self.score.json_file
        output = open(result_path, "w")
        json.dump(self.export_to_dict(), output, indent=4)
        output.close()
        return result_path

    @staticmethod
    def print() -> None:
        for field in FieldsManager.fields:
            print(f"- ``{field.name}``: {field.description}")
