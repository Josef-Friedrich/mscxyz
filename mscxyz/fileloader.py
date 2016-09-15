# -*- coding: utf-8 -*-

"""Basic file loading"""

import os
import shutil
from mscxyz.utils import mscore

class File(object):
	def __init__(self, fullpath):
		self.fullpath = fullpath
		self.extension = self.fullpath.split('.')[-1]
		self.fullpath_backup = self.fullpath.replace('.' + self.extension, '_bak.' + self.extension)
		self.dirname = os.path.dirname(fullpath)
		self.filename = os.path.basename(fullpath)
		self.basename = self.filename.replace('.mscx', '').decode('utf-8')

	def backup(self):
		shutil.copy2(self.fullpath, self.fullpath_backup)

	def export(self, extension='pdf'):
		score = self.fullpath
		mscore(['--export-to', score.replace('.mscx', '.' + extension), score])
