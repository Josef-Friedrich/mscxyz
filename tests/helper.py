"""Score for various tests"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from lxml.etree import _Element

from mscxyz import Score
from mscxyz.meta import Meta
from mscxyz.style import MscoreStyleInterface

test_dir = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(test_dir, "mscxyz.ini")


def get_path(filename: str, version: int = 2) -> Path:
    """
    Returns the path of a file based on the given filename and version.

    :param filename: The name of the file.
    :param version: The version of the file (default is 2).
    :return: The path of the file.
    """
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
    return Meta(get_file(filename, version))


def get_style(filename: str, version: int = 2) -> MscoreStyleInterface:
    return get_score(filename, version).style


def get_xml_root(filename: str, version: int = 2) -> _Element:
    """
    Get the XML tree from the specified file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file (default is 2).
    :return: The XML tree.
    """
    return get_score(filename, version).xml_root


def read_file(filename: str | Path) -> str:
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


def run(*args: str) -> str:
    """
    Run the mscx-manager command on the command line with the given arguments
    and return the output as a string.

    :param args: The arguments to pass to the mscx-manager command.
    :return: The output of the mscx-manager command as a string.
    """
    return subprocess.check_output(["mscx-manager"] + list(args)).decode("utf-8")
