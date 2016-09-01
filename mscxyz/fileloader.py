# -*- coding: utf-8 -*-

import os
from mscxyz import mscore

class File(object):
	def __init__(self, fullpath, args):
		self.fullpath = fullpath
		self.args = args
		self.dirname = os.path.dirname(fullpath)
		self.filename = os.path.basename(fullpath)
		self.basename = self.filename.replace('.mscx', '').decode('utf-8')
		self.extension = self.fullpath.split('.')[-1]

	def backup(self):
		import shutil
		score = self.fullpath
		ext = '.' + self.extension
		backup = score.replace(ext, '_bak' + ext)
		shutil.copy2(score, backup)

	def export(self):
		score = self.fullpath
		mscore(['--export-to', score.replace('.mscx', '.' + self.args.extension), score], self.args)
