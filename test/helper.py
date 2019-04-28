"""ScoreFile for various tests"""

from distutils.dir_util import copy_tree
import os
import shutil
import subprocess
import tempfile
from jflib import Capturing  # noqa: F401


def get_tmpfile_path(filename):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files',
        filename)
    tmp_dir = tempfile.mkdtemp()
    tmp = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def get_tmpdir_path(relative_dir):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files', relative_dir)
    tmp = tempfile.mkdtemp()
    copy_tree(orig, tmp)
    return tmp


def read_file(filename):
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


def run(*args):
    args = ['mscx-manager'] + list(args)
    return subprocess.check_output(args).decode('utf-8')
