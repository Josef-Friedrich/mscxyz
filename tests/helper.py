"""MscoreFile for various tests"""

import os
import shutil
import subprocess
import tempfile

from jflib import Capturing  # noqa: F401

test_dir = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(test_dir, "mscxyz.ini")


def get_file(filename: str, version: int = 2) -> str:
    """
    Returns the path of a temporary file created by copying the original file.

    :param filename: The name of the file to be copied.
    :param version: The version of the file, defaults to 2.
    :return: The path of the temporary file.
    """
    folder: str = f"files_mscore{version}"
    orig: str = os.path.join(test_dir, folder, filename)
    tmp_dir: str = tempfile.mkdtemp()
    tmp: str = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def get_dir(relative_dir: str, version: int = 2) -> str:
    if version == 2:
        folder = "files_mscore2"
    else:
        folder = "files_mscore3"
    orig = os.path.join(test_dir, folder, relative_dir)
    tmp = tempfile.mkdtemp()
    shutil.copytree(orig, tmp, dirs_exist_ok=True)
    return tmp


def read_file(filename: str) -> str:
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


def run(*args):
    args = ["mscx-manager"] + list(args)
    return subprocess.check_output(args).decode("utf-8")
