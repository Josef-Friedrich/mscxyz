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
    """
    Create a directory and any necessary parent directories.

    :param path: The file path whose parent directory should be created

    :raises OSError: If a directory creation error occurs other than the directory already existing
    """
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def _prepare_fields(fields: FieldsExport) -> dict[str, str]:
    """
    Prepare and normalize field values for renaming operations.

    Applies a series of text transformations to field values based on command-line
    arguments. Transformations may include alphanumeric filtering, ASCII conversion,
    whitespace removal, and character substitution.

    :param fields: Dictionary of fields and their values to be processed

    :return: Dictionary with processed field names and normalized values

    :note:
        The following transformations are applied conditionally:

        - If ``rename_alphanum`` is enabled: filters to alphanumeric characters
        - If ``rename_ascii`` is enabled: converts to ASCII representation
        - If ``rename_no_whitespace`` is enabled: removes all whitespace
        - Unconditional: strips leading/trailing whitespace and replaces "/" with "-"

    :return: Only non-empty field values are included in the output dictionary
    """
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
    """
    Display a file rename operation with color-coded output.

    :param old: The original file path or name (displayed in yellow)
    :param new: The new file path or name (displayed in green)
    """
    print(f"{colorize(old, 'yellow')} -> {colorize(new, 'green')}")


def _get_checksum(filename: str) -> str:
    """
    Calculate the SHA1 checksum of a file.

    :param filename: Path to the file for which to compute the checksum
    :return: Hexadecimal representation of the SHA1 checksum
    """
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def rename(score: Score, path_template: str) -> None:
    """
    Rename a MuseScore file based on a path template and metadata fields.

    :param score: A Score object containing the file path and metadata fields
    :param path_template: A template string for generating the target filename

    :example:
        >>> score = Score(path='song.mscx')
        >>> rename(score, '{composer}/{title}')
    """
    args = get_args()

    meta_values = score.fields.export_to_dict()

    fields = _prepare_fields(meta_values)
    target_filename = tmep.parse(path_template, fields)

    if args.rename_skip:
        skips: list[str] = args.rename_skip.split(",")
        for skip in skips:
            if skip not in meta_values:
                print(colorize(f"Field “{skip}” is empty! Skipping", "red"))
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
                        f"The file “{score.path}” with the same checksum (sha1) "
                        f"already exists in the target path “{target}”!",
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
