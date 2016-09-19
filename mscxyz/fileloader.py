# -*- coding: utf-8 -*-

"""Basic file loading"""

import os
import shutil
import six

from mscxyz.utils import mscore


class File(object):

    def __init__(self, fullpath):
        self.fullpath = fullpath
        self.extension = self.fullpath.split('.')[-1]
        self.fullpath_backup = self.fullpath.replace(
            '.' + self.extension, '_bak.' + self.extension)
        self.dirname = os.path.dirname(fullpath)
        self.filename = os.path.basename(fullpath)
        if six.PY2:
            self.basename = self.filename.replace('.mscx', '').decode('utf-8')
        else:
            self.basename = self.filename.replace('.mscx', '')

    def backup(self):
        """Make a copy of the MuseScore"""
        shutil.copy2(self.fullpath, self.fullpath_backup)

    def export(self, extension='pdf'):
        """Export the score to the specifed file type

        :param str extension: The extension (default: pdf)
        """
        score = self.fullpath
        mscore(['--export-to', score.replace('.mscx', '.' + extension), score])
