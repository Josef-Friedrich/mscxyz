"""Rename MuseScore files"""

from __future__ import annotations

import errno
import hashlib
import os
import re
import shutil
from pathlib import Path

import tmep
from tmep.format import alphanum, asciify, nowhitespace

from mscxyz.fields import FieldsExport
from mscxyz.score import Score
from mscxyz.settings import get_args
from mscxyz.utils import colorize


def _create_dir(path: str) -> None:
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def _prepare_fields(fields: FieldsExport) -> dict[str, str]:
    args = get_args()
    output: dict[str, str] = {}
    for field, value in fields.items():
        if value:
            value = str(value)
            if args.rename_alphanum:
                value = alphanum(value)
                value = value.strip()
            if args.rename_ascii:
                value = asciify(value)
            if args.rename_no_whitespace:
                value = nowhitespace(value)
            value = value.strip()
            value = value.replace("/", "-")
            output[field] = value
    return output


def _show(old: str, new: str) -> None:
    print("{} -> {}".format(colorize(old, "yellow"), colorize(new, "green")))


def _get_checksum(filename: str) -> str:
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def rename(score: Score, path_template: str) -> None:
    args = get_args()

    meta_values = score.fields.export_to_dict()

    fields = _prepare_fields(meta_values)
    target_filename = tmep.parse(path_template, fields)

    if args.rename_skip:
        skips: list[str] = args.rename_skip.split(",")
        for skip in skips:
            if skip not in meta_values:
                print(colorize("Field “{}” is empty! Skipping".format(skip), "red"))
                return

    if args.rename_target:
        target_base: str = os.path.abspath(args.rename_target)
    elif args.rename_only_filename:
        target_base = str(score.path.parent)
    else:
        target_base = os.getcwd()

    target: str = os.path.join(target_base, target_filename + "." + score.extension)

    if os.path.exists(target):
        target_format: str = re.sub(r".msc(x|z)$", r"{}.msc\1", target)
        i = 1
        counter_format: str = ""
        while os.path.exists(target_format.format(counter_format)):
            target = target_format.format(counter_format)
            if _get_checksum(str(score.path)) == _get_checksum(target):
                print(
                    colorize(
                        "The file “{}” with the same checksum (sha1) "
                        "already exists in the target path “{}”!".format(
                            str(score.path), target
                        ),
                        "red",
                    )
                )
                return
            if i == 1:
                counter_format = ""
            else:
                counter_format = str(i)
            i += 1

        target = target_format.format(counter_format)

    _show(str(score.path), target)

    if not args.general_dry_run:
        _create_dir(target)
        # Invalid cross-device link:
        # os.rename(source, target)
        shutil.move(score.path, target)
        score.path = Path(target)
