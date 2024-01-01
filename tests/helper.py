"""MscoreFile for various tests"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from jflib import Capturing  # noqa: F401
from lxml.etree import _ElementTree

from mscxyz import MscoreXmlTree

# if typing.TYPE_CHECKING:

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


def get_xml_tree(filename: str, version: int = 2) -> _ElementTree:
    """
    Get the XML tree from the specified file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file (default is 2).
    :return: The XML tree.
    """
    return MscoreXmlTree(get_file(filename, version)).xml_tree


def read_file(filename: str) -> str:
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


def run(*args):
    args: list[str] = ["mscx-manager"] + list(args)
    return subprocess.check_output(args).decode("utf-8")
