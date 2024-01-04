"""Rename MuseScore files"""

from __future__ import annotations

import errno
import hashlib
import os
import shutil

import tmep
from tmep.format import alphanum, asciify, nowhitespace

from mscxyz.meta import Meta
from mscxyz.utils import color, get_args


def create_dir(path: str) -> None:
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def prepare_fields(fields: dict[str, str]) -> dict[str, str]:
    args = get_args()
    out: dict[str, str] = {}
    for field, value in fields.items():
        if value:
            if args.rename_alphanum:
                value = alphanum(value)
                value = value.strip()
            if args.rename_ascii:
                value = asciify(value)
            if args.rename_no_whitespace:
                value = nowhitespace(value)
            value = value.strip()
            value = value.replace("/", "-")
        out[field] = value
    return out


def apply_format_string(fields: dict[str, str]) -> str:
    args = get_args()
    fields = prepare_fields(fields)
    name = tmep.parse(args.rename_format, fields)
    return name


def show(old: str, new: str) -> None:
    print("{} -> {}".format(color(old, "yellow"), color(new, "green")))


def get_checksum(filename: str) -> str:
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def rename_filename(source: str) -> Meta:
    args = get_args()

    meta = Meta(source)
    meta_values: dict[str, str] = meta.interface.export_to_dict()
    target_filename: str = apply_format_string(meta_values)

    if args.rename_skip:
        skips: list[str] = args.rename_skip.split(",")
        for skip in skips:
            if not meta_values[skip]:
                print(color("Field “{}” is empty! Skipping".format(skip), "red"))
                return meta

    if args.rename_target:
        target_base: str = os.path.abspath(args.rename_target)
    else:
        target_base = os.getcwd()

    target: str = os.path.join(target_base, target_filename + "." + meta.extension)

    if os.path.exists(target):
        target_format: str = target.replace(".mscx", "{}.mscx")
        i = 1
        counter_format: str = ""
        while os.path.exists(target_format.format(counter_format)):
            target = target_format.format(counter_format)
            if get_checksum(source) == get_checksum(target):
                print(
                    color(
                        "The file “{}” with the same checksum (sha1) "
                        "already exists in the target path “{}”!".format(
                            source, target
                        ),
                        "red",
                    )
                )
                return meta
            if i == 1:
                counter_format = ""
            else:
                counter_format = str(i)
            i += 1

        target = target_format.format(counter_format)

    show(source, target)

    if not args.general_dry_run:
        create_dir(target)
        # Invalid cross-device link:
        # os.rename(source, target)
        shutil.move(source, target)

    return meta
