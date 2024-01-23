"""Provide fields ($variable) for the path templates."""

from __future__ import annotations

import json
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


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
        Field(name="title", description="The combined title", attr_path="meta.title"),
        Field(name="abspath", description="", attr_path="abspath"),
        Field(name="basename", description="", attr_path="basename"),
        Field(name="dirname", description="", attr_path="dirname"),
        Field(name="extension", description="", attr_path="extension"),
        Field(name="filename", description="", attr_path="filename"),
        Field(name="relpath", description="", attr_path="relpath"),
        Field(name="relpath_backup", description="", attr_path="relpath_backup"),
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

    def __access_attr(self, attr_path: str) -> Any | None:
        attrs = attr_path.split(".")
        value = self.score
        for attr in attrs:
            value = getattr(value, attr)
            if value is None:
                break

        return value

    def get(self, name: str) -> Any | None:
        field = self.__fields_by_name[name]
        return self.__access_attr(field.attr_path)

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

    def export_json(self) -> Path:
        """
        Export the data as a JSON file.

        :return: The path to the exported JSON file.
        """
        data: dict[str, str] = {}
        result_path: Path = self.score.json_file
        # for field in self.interface.fields:
        #     data[field] = self.interface.__getattr__(field)
        output = open(result_path, "w")
        json.dump(data, output, indent=4)
        output.close()
        return result_path

    pass
