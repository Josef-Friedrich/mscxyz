# -*- coding: utf-8 -*-

from fileloader import File
from mscxyz import re_open, verbose

class Tree(File):

	def __init__(self, fullpath, args):
		super(Tree, self).__init__(fullpath, args)
		import lxml.etree as et
		try:
			self.tree = et.parse(self.fullpath)
		except et.XMLSyntaxError, e:
			print('Error!!! ' + str(e))
			self.error = True
		else:
			self.error = False
			self.root = self.tree.getroot()

	def addSubElement(self, root_tag, tag, text):
		if not self.error:
			import lxml.etree as et
			tag = et.SubElement(root_tag, tag)
			tag.text = text

	def stripTags(self, *tags):
		if not self.error:
			import lxml.etree as et
			et.strip_tags(self.tree, tags)
			verbose(str(tags), 'strip', color='blue', verbosity=2, args=self.args)

	def removeTagsByXPath(self, *xpath_strings):
		if not self.error:
			for xpath_string in xpath_strings:
				for rm in self.tree.xpath(xpath_string):
					verbose(rm.tag, 'remove', verbosity=2, args=self.args)
					rm.getparent().remove(rm)

	def mergeStyle(self):
		import lxml.etree as et
		style = et.parse(self.args.style.name).getroot()

		for score in self.tree.xpath('/museScore/Score'):
			score.insert(0, style[0])

	def clean(self):
		if not self.error:
			self.removeTagsByXPath('/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
			self.stripTags('font', 'b', 'i', 'pos')

	def write(self, new_name=''):
		if new_name:
			filename = new_name
		else:
			filename = self.fullpath
		if not self.error:
			self.tree.write(filename, encoding='UTF-8')
			re_open(filename, self.args)
