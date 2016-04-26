#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import lxml.etree
from termcolor import colored, cprint

reload(sys)
sys.setdefaultencoding('utf8')

class Parse(object):
	"""Expose the command line interface."""

	def __init__(self):
		self.initParser()
		self.addArguments()
		self.addSubParser()
		self.clean()
		self.meta()
		self.lyrics()
		self.rename()
		self.addPositional()

	def initParser(self):
		import argparse
		self.parser = argparse.ArgumentParser(description='A command \
			line tool to manipulate the XML based *.mscX and *.mscZ \
			files of the notation software MuseScore')

	def addArguments(self):
		parser = self.parser
		parser.add_argument('-b', '--backup', action='store_true',
			help='Create a backup file.')
		parser.add_argument('-g', '--glob', default='*.mscx',
			help='Handle only files which matches against Unix style \
			glob patterns (e. g. "*.mscx", "* - *"). If you omit this \
			option, the standard glob pattern "*.mscx" is used.')
		parser.add_argument('-p', '--pick', type=int, default=0,
			help='The --pick option can be used to run multiple \
			mscxyz.py commands in parallel on multiple consoles. If \
			you like so, using this option a "poor man\'s \
			multithreading" can be accomplished. Multicore CPUs can be \
			used to full capacity. \
			By default every fourth file gets picked up. The option \
			"-p N" begins the picking on the Nth file of a cycle. The \
			corresponding option is named "-c" or "--cycle-length".')
		parser.add_argument('-c', '--cycle-length', type=int, default=4,
			help='This option specifies the distance between the \
			picked files. The option "-c N" picks every Nth file. The \
			corresponding options is named "-p" or "--pick".')
		parser.add_argument('-v', '--verbose', action='count', default=0,
			help='Make commands more verbose. You can specifiy multiple \
			arguments (. g.: -vvv) to make the command more verbose.')

	def addSubParser(self):
		self.sparser = self.parser.add_subparsers(title='Subcommands',
			dest='subcommand', help='Run "subcommand --help" for more \
			informations.')

	def clean(self):
		p = self.sparser.add_parser('clean', help='Clean and reset \
			the formating of the *.mscx file')
		p.add_argument('-s', '--style', nargs=1,
			help='Load a *.mss style file and include the contents of this \
			file.')

	def meta(self):
		p = self.sparser.add_parser('meta', help='Synchronize the \
			values of the first vertical frame (title, composer, lyricist) \
			with the corresponding metadata fields.')
		p.add_argument('-j', '--json', action='store_true',
			help='Additionally write the metadata to a json file.')
		p.add_argument('-s', '--show', action='store_true',
			help='Show all metadata.')

	def lyrics(self):
		p = self.sparser.add_parser('lyrics', help='Extract lyrics.')
		p.add_argument('-n', '--number', nargs=1,
			help='Number of lyric verses.')

	def rename(self):
		p = self.sparser.add_parser('rename', help='Rename the \
			*.mscx files.')
		p.add_argument('-d', '--dry-run', action='store_true',
			help='Do not rename the scores')

	def addPositional(self):
		self.parser.add_argument('path', help='Path to a *.mscx file or a \
			folder which contains *.mscx files.')

	def parse(self):
		return self.parser.parse_args()


def execute():

	batch = Batch(args.path, args.glob)

	if args.pick:
		batch.pick(args.pick, args.cycle_length)

	files = batch.getFiles()
	for score in files:

		if args.backup:
			backup = File(score)
			backup.backup()

		if args.subcommand == 'clean':
			verbose(score, '\nclean', 'yellow')
			clean = Tree(score)
			clean.clean()
			clean.write()

		elif args.subcommand == 'lyrics':
			print(score)

		elif args.subcommand == 'meta':
			meta = Meta(score)
			if args.show:
				meta.show()
			else:
				meta.syncMetaTags()
				meta.write()

		elif args.subcommand == 'rename':
			rename = Rename(score)
			rename.execute()

class Batch(object):

	def __init__(self, path, glob = '*.mscx'):
		self.path = path
		self.files = []

		import fnmatch

		for root, dirs, files in os.walk(path):
			for file in files:
				if fnmatch.fnmatch(file, glob):
					file_path = os.path.join(root, file)
					self.files.append(file_path)

		self.files.sort()

	def pick(self, pick=1, cycle_length=4):
		hit = int(pick)
		counter = 0

		output = []
		for score in self.files:

			counter += 1
			if hit == counter:
				verbose(str(counter), 'pick', 'green')
				output.append(score)
				hit = hit + pick

		self.files = output

	def getFiles(self):
		if os.path.isdir(self.path):
			return self.files
		else:
			return [self.path]

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

def mscore(commands):
	import subprocess
	mac = '/Applications/MuseScore.app/Contents/MacOS/mscore'
	if os.path.exists(mac):
		executeable = mac
	else:
		executeable = 'mscore'

	commands.insert(0, executeable)
	if args.verbose > 2:
		OUT=None
	else:
		OUT = open(os.devnull, 'wb')

	subprocess.call(commands, stdout=OUT, stderr=OUT)

def re_open(input_file):
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

def exit_gracefully(signum, frame):
	# Restore the original signal handler as otherwise evil things will
	# happen, in raw_input when CTRL+C is pressed, and our signal
	# handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)

	try:
		if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
			print('Quitting ...')
			sys.exit(1)

	except KeyboardInterrupt:
		print("Ok ok, quitting")
		sys.exit(1)

	# restore the exit gracefully handler here
	signal.signal(signal.SIGINT, exit_gracefully)

def print_desc(text, description='', color='red'):
	prefix = ''
	if description:
		prefix = colored(description, color) + ': '
	print(prefix + text)

def verbose(text, description='', color='red', verbosity=1):
	if args.verbose >= verbosity:
		print_desc(text=text, description=description, color=color)

class File(object):
	def __init__(self, fullpath):
		self.fullpath = fullpath
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

class Rename(File):

	def __init__(self, fullpath):
		super(Rename, self).__init__(fullpath)
		self.workname = self.basename

	def replaceGermanUmlaute(self):
		umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü', 'Ae': u'Ä', 'Oe': u'Ö', 'Ue': u'Ü'}
		for replace, search in umlaute.iteritems():
			self.workname = self.workname.replace(search, replace)

	def transliterate(self):
		import unidecode
		self.workname = unidecode.unidecode(self.workname)

	def replaceToDash(self, *characters):
		for character in characters:
			self.workname = self.workname.replace(character, '-')

	def deleteCharacters(self, *characters):
		for character in characters:
			self.workname = self.workname.replace(character, '')

	def cleanUp(self):
		string = self.workname
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

		self.workname = string

	def debug(self):
		print(self.workname)

	def execute(self):
		self.replaceGermanUmlaute()
		self.transliterate()
		self.replaceToDash(' ', ';', '?', '!', '_', '#', '&', '+')
		self.deleteCharacters(',', '.', '\'', '`', ')')
		self.cleanUp()

		if args.dry_run or args.verbose > 0:
			print(colored(self.basename, 'red') + ' -> ' + colored(self.workname, 'yellow'))

		if not args.dry_run:
			os.rename(self.fullpath, self.dirname + '/' + self.workname + '.' + self.extension)

class Tree(File):

	def __init__(self, fullpath):
		super(Tree, self).__init__(fullpath)
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
			verbose(str(tags), 'strip', color='blue', verbosity=2)

	def removeTagsByXPath(self, *xpath_strings):
		if not self.error:
			for xpath_string in xpath_strings:
				for rm in self.tree.xpath(xpath_string):
					verbose(rm.tag, 'remove', verbosity=2)
					rm.getparent().remove(rm)

	def clean(self):
		if not self.error:
			self.removeTagsByXPath('/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
			self.stripTags('font', 'b', 'i', 'pos')

	def write(self):
		if not self.error:
			self.tree.write(self.fullpath, encoding='UTF-8')
			re_open(self.fullpath)

class Meta(Tree):

	def __init__(self, fullpath):
		super(Meta, self).__init__(fullpath)

		if not self.error:
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
			self.basename
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
		if not self.error:
			self.syncTitle()
			self.syncComposer()
			self.syncLyricist()
			self.cleanMeta()

	def show(self):
		print_desc('\n' + colored(self.filename, 'red'))
		print_desc(self.basename, 'filename', 'blue')
		if not self.error:
			for tag, text in self.meta.iteritems():
				if text:
					print_desc(text, tag, 'yellow')

			for tag, text in self.vbox.iteritems():
				if text:
					print_desc(text, tag, 'green')

if __name__ == '__main__':

	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)

	parse = Parse()
	args = parse.parse()
	execute()
