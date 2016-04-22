#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from termcolor import colored, cprint

reload(sys)
sys.setdefaultencoding('utf8')

def main():
	"""Expose the command line interface."""
	import argparse
	import musescore

	def clean(args):
		for score in musescore.get_mscx(args.path):
			print(score)

	def lyrics(args):
		for score in musescore.get_mscx(args.path):
			print(score)

	def meta(args):
		for score in musescore.get_mscx(args.path):
			meta = musescore.Meta(score)
			rename = musescore.Rename(score)
			if args.show:
				meta.show()
			else:
				meta.syncMetaTags()
				meta.write()

	def rename(args):
		for score in musescore.get_mscx(args.path):
			print(score)

	parser = argparse.ArgumentParser(description='Muggle the *.mscx files \
		of the notation software MuseScore.')

	parser.add_argument('-b', '--backup', action='store_true',
		help='Create a backup file.')
	parser.add_argument('-n', '--start-number', nargs=1,
		help='')
	parser.add_argument('-c', '--cycle-number', nargs=1, default=4,
		help='')

	##
	# subcommand
	##

	subparsers = parser.add_subparsers(title='Subcommands', help='Run \
		"subcommand --help" for more informations.')

	# clean
	parser_clean = subparsers.add_parser('clean', help='Clean and reset \
		the formating of the *.mscx file')
	parser_clean.add_argument('-s', '--style', nargs=1,
		help='Load a *.mss style file and include the contents of this \
		file.')
	parser_clean.set_defaults(func=clean)

	# meta
	parser_meta = subparsers.add_parser('meta', help='Synchronize the \
		values of the first vertical frame (title, composer, lyricist) \
		with the corresponding metadata fields.')
	parser_meta.add_argument('-j', '--json', action='store_true',
		help='Additionally write the metadata to a json file.')
	parser_meta.add_argument('-s', '--show', action='store_true',
		help='Show all metadata.')
	parser_meta.set_defaults(func=meta)

	# lyrics
	parser_lyrics = subparsers.add_parser('lyrics', help='Extract lyrics.')
	parser_lyrics.add_argument('-n', '--number', nargs=1,
		help='Number of lyric verses.')
	parser_lyrics.set_defaults(func=lyrics)

	# rename
	parser_rename = subparsers.add_parser('rename', help='Rename the \
		*.mscx files.')
	parser_rename.set_defaults(func=rename)

	##
	# suffix positional parameters
	##

	parser.add_argument('path', help='Path to a *.mscx file or a \
		folder which contains *.mscx files.')

	args = parser.parse_args()
	args.func(args)

def batch():
	start_number = int(sys.argv[1])

	if len(sys.argv) > 2:
		cycle_number = int(sys.argv[2])
	else:
		cycle_number = 4

	files = musescore.get_files('mscx')
	hit = start_number
	counter = 0
	for score in files:
		counter += 1
		if hit == counter:
			execute(score, counter)
			hit = hit + cycle_number

def extract_lyrics():
	ms_file = sys.argv[1]
	lyrics_no_display = sys.argv[2]
	lyrics_no = str(int(lyrics_no_display) - 1)
	new_file = ms_file.replace('.mscx', '_Lyrics-no-' + lyrics_no_display + '.mscx')

	print(new_file)

	mscx = et.parse(ms_file)

	for lyric in mscx.findall('.//Lyrics'):
		number = lyric.find('no')
		if hasattr(number, 'text'):
			no = number.text
		else:
			no = '0'

		if no != lyrics_no:
			lyric.getparent().remove(lyric)
		elif hasattr(number, 'text'):
			number.text = '0'

	# To get closing tag use method 'html'
	mscx.write(new_file, pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')


def get_style_folder():
	style_folder = 'MuseScore2/Stile'
	home = os.path.expanduser('~')
	if os.path.exists(home + '/Documents/' + style_folder):
		return home + '/Documents/' + style_folder
	elif os.path.exists(home + '/Dokumente/' + style_folder):
		return home + '/Dokumente/' + style_folder

def mscore(args):
	import subprocess
	mac = '/Applications/MuseScore.app/Contents/MacOS/mscore'
	if os.path.exists(mac):
		executeable = mac
	else:
		executeable = 'mscore'

	args.insert(0, executeable)
	subprocess.call(args)

def re_open(input_file):
	if not input_file:
		input_file = score
	mscore(['-o', input_file, input_file])

def convert_mxl(input_file):
	output_file = input_file.replace('.mxl', '.mscx')
	mscore(['-o', output_file, input_file])
	os.remove(input_file)

def metadata_to_json():
	title = get_meta_tag('workTitle')
	composer = get_meta_tag('composer')
	lyricist = get_meta_tag('lyricist')

	print('Title: ' + str(title) + '; Composer: ' + str(composer) + '; Lyricist: ' + str(lyricist))

	data = {}
	data['title'] = title

	if composer:
		data['composer'] = composer

	if lyricist:
		data['lyricist'] = lyricist

	out_file = open("test.json","w")
	json.dump(data,out_file, indent=4)
	out_file.close()

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

def get_mscx(path):
	if os.path.isdir(path):
		return get_files(path, 'mscx')
	else:
		return [path]

def get_files(path, extension = 'mscx'):
	output = []
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.endswith('.' + extension):
				file_path = os.path.join(root, file)
				output.append(file_path)
	return output

def rename_bad_musicxml_extensions():
	numbers = ['1', '2', '3', '4', '5']

	for number in numbers:
		files = musescore.get_files('mxl.' + number)

		for score in files:
			new_number = int(number) + 1
			new_score = score.replace('.mxl.' + number, '[' + str(new_number) + '].mxl')
			os.rename(score, new_score)

class File(object):
	def __init__(self, fullpath):
		self.fullpath = fullpath
		self.dirname = os.path.dirname(fullpath)
		self.basename = os.path.basename(fullpath)
		self.filename = self.basename.replace('.mscx', '').decode('utf-8')

class Rename(File):

	def prepareBasename(self):
		self.basename = self.basename.replace('.mscx', '').decode('utf-8')

	def replaceGermanUmlaute(self):
		umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü', 'Ae': u'Ä', 'Oe': u'Ö', 'Ue': u'Ü'}
		for replace, search in umlaute.iteritems():
			self.basename = self.basename.replace(search, replace)

	def transliterate(self):
		import unidecode
		self.basename = unidecode.unidecode(self.basename)

	def replaceToDash(self, *characters):
		for character in characters:
			self.basename = self.basename.replace(character, '-')

	def deleteCharacters(self, *characters):
		for character in characters:
			self.basename = self.basename.replace(character, '')

	def cleanUp(self):
		string = self.basename
		string = string.replace('(', '_')
		string = string.replace('-_', '_')

		import re
		# Replace two or more dashes with one.
		string = re.sub('-{2,}', '_', string)
		string = re.sub('_{2,}', '_', string)
		# Remove dash at the begining
		string = re.sub('^-', '', string)
		# Remove the dash from the end
		string = re.sub('-$', '', string)

		self.basename = string

	def debug(self):
		print(self.basename)

	def execute(self):
		self.prepareBasename()
		self.replaceGermanUmlaute()
		self.transliterate()
		self.replaceToDash(' ', ';', '?', '!', '_', '#', '&', '+')
		self.deleteCharacters(',', '.', '\'', '`', ')')
		self.cleanUp()

class Tree(File):

	def __init__(self, fullpath):
		super(Tree, self).__init__(fullpath)
		import lxml.etree as et
		self.tree = et.parse(self.fullpath)
		self.root = self.tree.getroot()

	def addSubElement(self, root_tag, tag, text):
		import lxml.etree as et
		tag = et.SubElement(root_tag, tag)
		tag.text = text

	def stripTags(self, *tags):
		import lxml.etree as et
		et.strip_tags(self.tree, tags)

	def removeTagsByXPath(self, *xpath_strings):
		for xpath_string in xpath_strings:
			for rm in self.tree.xpath(xpath_string):
				rm.getparent().remove(rm)

	def clean(self):
		self.removeTagsByXPath('/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
		self.stripTags('font', 'b', 'i', 'pos')

	def write(self):
		self.tree.write(self.fullpath, encoding='UTF-8')
		re_open(self.fullpath)

class Meta(Tree):

	def __init__(self, fullpath):
		super(Meta, self).__init__(fullpath)

		tags = [
			"arranger",
			"composer",
			"copyright",
			"creationDate",
			"lyricist",
			"movementNumber",
			"movementTitle",
			"originalFormat",
			"platform",
			"poet",
			"source",
			"translator",
			"workNumber",
			"workTitle"
		]

		self.meta = {}
		for tag in tags:
			text = self.getMetaText(tag)
			if text:
				self.meta[tag] = text.decode('utf-8')
			else:
				self.meta[tag] = ''

		tags = [
			"Title",
			"Subtitle",
			"Composer",
			"Lyricist"
		]

		self.vbox = {}
		for tag in tags:
			text = self.getVBoxText(tag)
			if text:
				self.vbox[tag] = text.decode('utf-8')
			else:
				self.vbox[tag] = ''

	def getMetaTag(self, name):
		for element in self.root.xpath('//metaTag[@name="' + name + '"]'):
			return element

	def getMetaText(self, name):
		element = self.getMetaTag(name)
		if hasattr(element, 'text'):
			return element.text

	def setMeta(self, name, text):
		self.getMetaTag(name).text = text

	def createVBox(self):
		import lxml.etree as et
		xpath = '/museScore/Score/Staff[@id="1"]'
		if not self.root.xpath(xpath + '/VBox'):
			tag = et.Element('VBox')
			self.addSubElement(tag, 'height', '10')
			for element in self.root.xpath(xpath):
				element.insert(0, tag)

	def getVBoxTag(self, style):
		for element in self.root.xpath('//VBox/Text'):
			if element.find('style').text == style:
				return element.find('text')

	def insertInVBox(self, style, text):
		import lxml.etree as et
		tag = et.Element('Text')
		self.addSubElement(tag, 'text', text)
		self.addSubElement(tag, 'style', style)
		for element in self.root.xpath('//VBox'):
			element.append(tag)

	def getVBoxText(self, style):
		element = self.getVBoxTag(style)
		if hasattr(element, 'text'):
			return element.text

	def setVBox(self, style, text):
		self.createVBox()
		element = self.getVBoxTag(style)
		if hasattr(element, 'text'):
			element.text = text
		else:
			self.insertInVBox(style, text)

	def syncTitle(self):
		values = [
			self.vbox['Title'],
			self.meta['workTitle'],
			self.meta['movementTitle'],
			self.filename
		]

		for value in values:
			if value:
				break

		self.setVBox('Title', value)
		self.setMeta('workTitle', value)
		self.setMeta('movementTitle', '')

	def syncComposer(self):
		values = [
			self.vbox['Composer'],
			self.meta['composer']
		]

		for value in values:
			if value:
				self.setVBox('Composer', value)
				self.setMeta('composer', value)
				break

	def syncLyricist(self):
		values = [
			self.vbox['Lyricist'],
			self.meta['lyricist']
		]

		for value in values:
			if value:
				self.setVBox('Lyricist', value)
				self.setMeta('lyricist', value)
				break

	def cleanMeta(self):
		tags = [
			"arranger",
			"copyright",
			"movementNumber",
			"movementTitle",
			"poet",
			"translator",
			"workNumber"
			]
		for tag in tags:
			self.setMeta(tag, '')

	def syncMetaTags(self):
		self.syncTitle()
		self.syncComposer()
		self.syncLyricist()
		self.cleanMeta()

	def show(self):
		cprint('\n' + self.basename, 'red')

		print(colored('filename', 'blue') + ': ' + self.filename)

		for tag, text in self.meta.iteritems():
			if text:
				print(colored(tag, 'yellow') + ': ' + text)

		for tag, text in self.vbox.iteritems():
			if text:
				print(colored(tag, 'green') + ': ' + text)

if __name__ == '__main__':
	main()
