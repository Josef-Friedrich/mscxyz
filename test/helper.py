"""File for various tests"""


import os
import sys
import shutil
import tempfile
from distutils.dir_util import copy_tree
import six
if six.PY2:
    from cStringIO import StringIO
else:
    from io import StringIO


if sys.prefix == '/usr':
    mscore = True
else:
    mscore = False


def tmp_file(test_file):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files',
        test_file)
    tmp_dir = tempfile.mkdtemp()
    tmp = os.path.join(tmp_dir, test_file)
    shutil.copyfile(orig, tmp)
    return tmp


def tmp_dir(relative_dir):
    orig = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'files', relative_dir)
    tmp = tempfile.mkdtemp()
    copy_tree(orig, tmp)
    return tmp


def read_file(test_file):
    tmp = open(test_file)
    output = tmp.read()
    tmp.close()
    return output


class Capturing(list):
    def __init__(self, channel='out'):
        self.channel = channel

    def __enter__(self):
        if self.channel == 'out':
            self._pipe = sys.stdout
            sys.stdout = self._stringio = StringIO()
        elif self.channel == 'err':
            self._pipe = sys.stderr
            sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        if self.channel == 'out':
            sys.stdout = self._pipe
        elif self.channel == 'err':
            sys.stderr = self._pipe


def get_file(filename):
    return os.path.join(os.path.dirname(__file__), 'files', filename + '.mscx')
