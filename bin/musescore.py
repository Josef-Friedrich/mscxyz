# -*- coding: utf-8 -*-

import os
import sys

# Name of the score file
score = ''

def catch_args(number_of_args = 1, usage_text = ' <musescore-fle.mscx>'):
	if len(sys.argv) < number_of_args + 1:
		print('Usage: ' + os.path.basename(sys.argv[0]) + ' ' + usage_text)
		sys.exit()

	global score
	score = sys.argv[1]

def get_style_folder():
	style_folder = 'MuseScore2/Stile'
	home = os.path.expanduser('~')
	if os.path.exists(home + '/Documents/' + style_folder):
		return home + '/Documents/' + style_folder
	elif os.path.exists(home + '/Dokumente/' + style_folder):
		return home + '/Dokumente/' + style_folder

def re_open():
	import subprocess
	mac_ms = '/Applications/MuseScore.app/Contents/MacOS/mscore'
	if os.path.exists(mac_ms):
		subprocess.call([mac_ms, "-o", score, score])
	else:
		subprocess.call(["mscore", "-o", score, score])

def create_info(json_file, data):
	import json
	out_file = open(json_file, 'w')
	json.dump(data, out_file, indent=4)
	out_file.close()

def create_dir(path):
	import errno
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def get_lieder_folder():
	return os.path.expanduser('~') + '/git-repositories/content/lieder/songs/'

def backup():
	import shutil
	shutil.copy2(score, score.replace('.mscx', '_bak.mscx'))

def get_all_mscx():
	path = os.getcwd()

	mscx_files = []

	for root, dirs, files in os.walk(path):
		for file in files:
			if file.endswith('.mscx'):
				file_path = os.path.join(root, file)
				mscx_files.append(file_path)

	return mscx_files

class Rename:

	def __init__(self, full_path):
		self.dirname = os.path.dirname(full_path)
		self.basename = os.path.basename(full_path).replace('.mscx', '')

	def debug(self):
		print(self.basename)

	def transliterate(self):
		import unidecode
		string = self.basename.decode('utf-8')
		string = string.replace(u'ö', 'oe')
		string = string.replace(u'ü', 'ue')
		string = string.replace(u'ä', 'ae')
		string = string.replace(u'Ö', 'Oe')
		string = string.replace(u'Ü', 'Ue')
		string = string.replace(u'Ä', 'Ae')
		string = unidecode.unidecode(string)
		self.basename = string
		return string

	def clean(self):
		string = self.basename

		to_dashs = [' ', ',', ';', '?', '!', '_']
		for to_dash in to_dashs:
			string = string.replace(to_dash, '-')

		to_deletes = ['.', '\'', '`', ')']
		for to_delete in to_deletes:
			string = string.replace(to_delete, '')

		string = string.replace('(', '_')
		string = string.replace('-_', '_')

		import re
		# Replace two or more dashes with one.
		string = re.sub('-{2,}', '_', string)
		# Remove dash at the begining
		string = re.sub('^-', '', string)
		# Remove the dash from the end
		string = re.sub('-$', '', string)

		self.basename = string
		return string

class Tree:

	def __init__(self, file_name = ''):
		import lxml.etree as et
		if not file_name:
			self.file_name = score
		else:
			self.file_name = file_name
		self.tree = et.parse(self.file_name)
		self.root = self.tree.getroot()

	def stripTags(self, *tags):
		import lxml.etree as et
		et.strip_tags(self.tree, tags)

	def removeTagsByXPath(self, *xpath_strings):
		for xpath_string in xpath_strings:
			for rm in self.tree.xpath(xpath_string):
				rm.getparent().remove(rm)

	def getMetaTag(self, name):
		element = self.root.xpath("//metaTag[@name='" + name + "']")
		return element[0].text

	def getVBox(self, name):
		for element in self.root.xpath('//VBox/Text'):
			if element.find('style').text == name:
				return element.find('text').text

	def insertInVBox(self, style, text):
		import lxml.etree as et
		tag_root = et.Element('Text')
		tag_text = et.SubElement(tag_root, 'text')
		tag_text.text = text
		tag_style = et.SubElement(tag_root, 'style')
		tag_style.text = style

		for element in self.root.xpath('//VBox'):
			element.append(tag_root)


	def setMetaTag(self, name, text):
		element = self.root.xpath("//metaTag[@name='" + name + "']")
		element[0].text = text

	def write(self):
		self.tree.write(self.file_name, encoding='UTF-8')


	def printFilename(self):
		print(fiile)

