"""ScoreFile for various tests"""

from distutils.dir_util import copy_tree
import os
import shutil
import subprocess
import tempfile
from jflib import Capturing  # noqa: F401

test_dir = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(test_dir, 'mscxyz.ini')


def get_tmpfile_path(filename, version=2):
    if version == 2:
        folder = 'files_mscore2'
    else:
        folder = 'files_mscore3'
    orig = os.path.join(test_dir, folder, filename)
    tmp_dir = tempfile.mkdtemp()
    tmp = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def get_tmpdir_path(relative_dir, version=2):
    if version == 2:
        folder = 'files_mscore2'
    else:
        folder = 'files_mscore3'
    orig = os.path.join(test_dir, folder, relative_dir)
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
