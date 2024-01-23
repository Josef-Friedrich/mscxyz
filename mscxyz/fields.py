"""Provide fields ($variable) for the path templates."""

from __future__ import annotations

import json
import re
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Union

from mscxyz.meta import FormatStringNoFieldError, UnmatchedFormatStringError

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


class FieldsManager:
    score: "Score"

    fields = (
        # Combined
        Field(name="title", description="The combined title", attr_path="meta.title"),
        Field(
            name="subtitle",
            description="The combined subtitle",
            attr_path="meta.subtitle",
        ),
        Field(
            name="composer",
            description="The combined composer",
            attr_path="meta.composer",
        ),
        Field(
            name="lyricist",
            description="The combined lyricist",
            attr_path="meta.lyricist",
        ),
        # vbox
        Field(
            name="vbox_title",
            description="The title field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.title",
        ),
        Field(
            name="vbox_subtitle",
            description="The subtitle field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.subtitle",
        ),
        Field(
            name="vbox_composer",
            description="The composer field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.composer",
        ),
        Field(
            name="vbox_lyricist",
            description="The lyricist field of the score as it appears in the center of the first vertical frame (VBox).",
            attr_path="meta.vbox.lyricist",
        ),
        # metatag
        Field(
            name="metatag_arranger",
            description="The arranger field stored as project properties.",
            attr_path="meta.metatag.arranger",
        ),
        Field(
            name="metatag_audio_com_url",
            description="The audio.com URL field stored as project properties.",
            attr_path="meta.metatag.audio_com_url",
        ),
        Field(
            name="metatag_composer",
            description="The composer field stored as project properties.",
            attr_path="meta.metatag.composer",
        ),
        Field(
            name="metatag_copyright",
            description="The copyright field stored as project properties.",
            attr_path="meta.metatag.copyright",
        ),
        Field(
            name="metatag_creation_date",
            description="The creation date field stored as project properties.",
            attr_path="meta.metatag.creation_date",
        ),
        Field(
            name="metatag_lyricist",
            description="The lyricist field stored as project properties.",
            attr_path="meta.metatag.lyricist",
        ),
        Field(
            name="metatag_movement_number",
            description="The movement number field stored as project properties.",
            attr_path="meta.metatag.movement_number",
        ),
        Field(
            name="metatag_movement_title",
            description="The movement title field stored as project properties.",
            attr_path="meta.metatag.movement_title",
        ),
        Field(
            name="metatag_msc_version",
            description="The MuseScore version field stored as project properties.",
            attr_path="meta.metatag.msc_version",
        ),
        Field(
            name="metatag_platform",
            description="The platform field stored as project properties.",
            attr_path="meta.metatag.platform",
        ),
        Field(
            name="metatag_poet",
            description="The poet field stored as project properties.",
            attr_path="meta.metatag.poet",
        ),
        Field(
            name="metatag_source",
            description="The source field stored as project properties.",
            attr_path="meta.metatag.source",
        ),
        Field(
            name="metatag_source_revision_id",
            description="The source revision ID field stored as project properties.",
            attr_path="meta.metatag.source_revision_id",
        ),
        Field(
            name="metatag_subtitle",
            description="The subtitle field stored as project properties.",
            attr_path="meta.metatag.subtitle",
        ),
        Field(
            name="metatag_translator",
            description="The translator field stored as project properties.",
            attr_path="meta.metatag.translator",
        ),
        Field(
            name="metatag_work_number",
            description="The work number field stored as project properties.",
            attr_path="meta.metatag.work_number",
        ),
        Field(
            name="metatag_work_title",
            description="The work title field stored as project properties.",
            attr_path="meta.metatag.work_title",
        ),
        # Readonly
        Field(
            name="version",
            description="The MuseScore version as a floating point number, "
            "for example ``2.03``, ``3.01`` or ``4.20``.",
            attr_path="version",
        ),
        Field(
            name="version_major",
            description="The major MuseScore version, for example ``2``, ``3`` or ``4``.",
            attr_path="version_major",
        ),
        Field(
            name="path",
            description="The absolute path of the MuseScore file, for example ``/home/xyz/score.mscz``.",
            attr_path="path",
        ),
        Field(
            name="backup_file",
            description="The absolute path of the backup file. "
            "The string ``_bak`` is appended to the file name before the extension.",
            attr_path="backup_file",
        ),
        Field(
            name="json_file",
            description="The absolute path of the JSON file in which the metadata can be exported.",
            attr_path="json_file",
        ),
        Field(
            name="dirname",
            description="The name of the containing directory of the MuseScore file, for "
            "example: ``/home/xyz/score_files``.",
            attr_path="dirname",
        ),
        Field(
            name="filename",
            description="The filename of the MuseScore file, for example:"
            "``score.mscz``.",
            attr_path="filename",
        ),
        Field(
            name="basename",
            description="The basename of the score file, for example: ``score``.",
            attr_path="basename",
        ),
        Field(
            name="extension",
            description="The extension (``mscx`` or ``mscz``) of the score file.",
            attr_path="extension",
        ),
    )

    __fields_by_name: dict[str, Field]

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.__fields_by_name = {}
        for field in self.fields:
            if field.name in self.__fields_by_name:
                raise Exception("Duplicate field name")
            self.__fields_by_name[field.name] = field

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

    def set(self, name: str, value: Any) -> Any | None:
        field = self.get_field(name)
        attrs = field.attr_path.split(".")

        last = attrs.pop()

        obj = self.score
        for attr in attrs:
            obj = getattr(obj, attr)
            if obj is None:
                raise Exception(f"Cannot set attribute {field.attr_path}")

        setattr(obj, last, value)

    def show(self, pre: dict[str, str], post: dict[str, str]) -> None:
        pass
        # args = get_args()

        # fields = list(self.interface.fields)

        # if args.general_verbose < 1:
        #     fields.remove("readonly_abspath")
        #     fields.remove("readonly_dirname")
        #     fields.remove("readonly_extension")
        #     fields.remove("readonly_filename")
        #     fields.remove("readonly_relpath")

        # if args.general_verbose < 2:
        #     fields.remove("readonly_relpath_backup")

        # for field in fields:
        #     field_color: utils.Color
        #     if (
        #         args.general_verbose == 0
        #         and (field in pre and pre[field] or field in post and post[field])
        #     ) or args.general_verbose > 0:
        #         if re.match(r"^combined_", field):
        #             field_color = "green"
        #         elif re.match(r"^metatag_", field):
        #             field_color = "blue"
        #         elif re.match(r"^readonly_", field):
        #             field_color = "red"
        #         elif re.match(r"^vbox_", field):
        #             field_color = "cyan"
        #         else:
        #             field_color = "white"

        #         line: list[str] = []
        #         if pre[field]:
        #             line.append("“{}”".format(pre[field]))

        #         if pre[field] != post[field]:
        #             line.append("->")
        #             line.append(utils.color("“{}”".format(post[field]), "yellow"))

        #         print("{}: {}".format(utils.color(field, field_color), " ".join(line)))

    def export_to_dict(self) -> dict[str, FieldValue]:
        output: FieldsExport = {}
        for field in self.names:
            value = self.get(field)
            if value is not None:
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
