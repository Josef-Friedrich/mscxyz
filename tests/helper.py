"""Score for various tests"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Sequence, Union

from lxml.etree import _Element

from mscxyz import Score
from mscxyz.cli import execute
from mscxyz.cli_legacy import execute as execute_legacy
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.style import Style

test_dir = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(test_dir, "mscxyz.ini")


def get_path(filename: str, version: int = 2) -> Path:
    """
    Returns the path of a file based on the given filename and version.

    :param filename: The name of the file.
    :param version: The version of the file (default is 2).
    :return: The path of the file.
    """

    if version > 3 and filename.endswith(".mscx"):
        base = filename[:-5]
        filename = str(Path(base) / filename)
    return Path(test_dir) / "files" / "by_version" / str(version) / filename


def get_dir(dirname: str, version: int = 2) -> str:
    """
    Get a temporary directory containing a copy of the specified directory.

    :param dirname: The name of the directory to copy.
    :param version: The version of the directory to copy (default is 2).
    :return: The path of the temporary directory.
    """
    orig: Path = get_path(dirname, version)
    tmp: str = tempfile.mkdtemp()
    shutil.copytree(orig, tmp, dirs_exist_ok=True)
    return tmp


def get_file(filename: str, version: int = 2) -> str:
    """
    Returns the path of a temporary file created by copying the original file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file, defaults to 2.
    :return: The path of the temporary file.
    """
    orig: Path = get_path(filename, version)
    tmp_dir: str = tempfile.mkdtemp()
    tmp: str = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def get_score(filename: str, version: int = 2) -> Score:
    return Score(get_file(filename, version))


def get_meta(filename: str, version: int = 2) -> Meta:
    return get_score(filename, version).meta


def get_lyrics(filename: str, version: int = 2) -> Lyrics:
    return get_score(filename, version).lyrics


def get_style(filename: str, version: int = 2) -> Style:
    return get_score(filename, version).style


def get_xml_root(filename: str, version: int = 2) -> _Element:
    """
    Get the XML tree from the specified file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file (default is 2).
    :return: The XML tree.
    """
    return get_score(filename, version).xml_root


def reload(src: Score | str | Path) -> Score:
    if isinstance(src, str) or isinstance(src, Path):
        return Score(src)
    return Score(src.path)


def read_file(filename: str | Path) -> str:
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


CliArg = Union[str, Path, Score]


def __stringify_args(args: Sequence[CliArg]) -> list[str]:
    result: list[str] = []
    for arg in args:
        if isinstance(arg, Path):
            result.append(str(arg))
        elif isinstance(arg, Score):
            result.append(str(arg.path))
        else:
            result.append(arg)
    return result


def __simluate_cli(*args: CliArg) -> None:
    execute(__stringify_args(args))


def cli_legacy(*args: CliArg) -> None:
    execute_legacy(__stringify_args(args))


def stderr(*cli_args: CliArg) -> str:
    f = StringIO()
    with redirect_stderr(f):
        __simluate_cli(*cli_args)
    return f.getvalue()


def stdout(*cli_args: CliArg) -> str:
    f = StringIO()
    with redirect_stdout(f):
        __simluate_cli(*cli_args)
    return f.getvalue()


def cli(*cli_args: CliArg) -> None:
    __simluate_cli(*cli_args)


def run(*args: str) -> str:
    """
    Run the mscx-manager command on the command line with the given arguments
    and return the output as a string.

    :param args: The arguments to pass to the mscx-manager command.
    :return: The output of the mscx-manager command as a string.
    """
    return subprocess.check_output(["mscx-manager"] + list(args)).decode("utf-8")


def open_in_gui(file: str | Path) -> None:
    """Open a file wiht xdg-open in the background"""
    subprocess.Popen(("/usr/local/bin/mscore", str(file)))
