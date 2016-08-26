#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import lxml.etree
from termcolor import colored, cprint
import meta.Meta as Meta

reload(sys)
sys.setdefaultencoding('utf8')

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

class Parse(object):
	"""Expose the command line interface."""

	def __init__(self):
		self.sub = {}
		self.initParser()
		self.addArguments()
		self.addSubParser()
		self.addPositional()

	def initParser(self):
		import argparse
		self.parser = argparse.ArgumentParser(description='A command \
			line tool to manipulate the XML based *.mscX and *.mscZ \
			files of the notation software MuseScore.')

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
			help='Make commands more verbose. You can specifiy \
			multiple arguments (. g.: -vvv) to make the command more \
			verbose.')

	def addSubParser(self):
		import argparse
		import textwrap

		self.sparser = self.parser.add_subparsers(title='Subcommands',
			dest='subcommand', help='Run "subcommand --help" for more \
			informations.')

	# clean

		self.sub['clean'] = self.sparser.add_parser('clean',
			help='Clean and reset the formating of the *.mscx file')

		self.sub['clean'].add_argument('-s', '--style', type=file,
			help='Load a *.mss style file and include the contents of \
			this file.')

	# meta

		self.sub['meta'] = self.sparser.add_parser('meta',
			help='Synchronize the values of the first vertical frame \
			(title, composer, lyricist) with the corresponding \
			metadata fields.',
			formatter_class=argparse.RawDescriptionHelpFormatter,
			description=textwrap.dedent('''\
			# XML structure of a meta tag:

				<metaTag name="tag"></metaTag>

			# All meta tags:

				- arranger
				- composer
				- copyright
				- creationDate
				- lyricist
				- movementNumber
				- movementTitle
				- originalFormat
				- platform
				- poet
				- source
				- translator
				- workNumber
				- workTitle

			# XML structure of a vbox tag:

				<VBox>
				  <Text>
				    <style>Title</style>
				    <text>Some title text</text>
				    </Text>

			# All vbox tags:

				- Title
				- Subtitle
				- Composer
				- Lyricis
			'''
			)
		)

		self.sub['meta'].add_argument('-j', '--json',
			action='store_true', help='Additionally write the metadata \
			to a json file.')

		self.sub['meta'].add_argument('-s', '--show',
			action='store_true', help='Show all metadata.')

	# lyrics

		self.sub['lyrics'] = self.sparser.add_parser('lyrics',
			help='Extract lyrics. Without any option this subcommand \
			extracts all lyrics verses into separate mscx files. \
			This generated mscx files contain only one verse. The old \
			verse number is appended to the file name, e. g.: \
			score_1.mscx.')

		self.sub['lyrics'].add_argument('-n', '--number',
			help='The lyric verse number to extract.')

		self.sub['lyrics'].add_argument('-r', '--remap',
			help='Remap lyrics. Example: "--remap 3:2,5:3". This \
			example remaps lyrics verse 3 to verse 2 and verse 5 to 3. \
			Use commas to specify multiple remap pairs. One remap pair \
			is separated by a colon in this form: "old:new": "old" \
			stands for the old verse number. "new" stands for the new \
			verse number.')

	# rename

		self.sub['rename'] = self.sparser.add_parser('rename',
			help='Rename the *.mscx files.',
			formatter_class=argparse.RawDescriptionHelpFormatter,
			description=textwrap.dedent('''\
			Tokens you can use in the format string (-f, --format):

				- %title%
				- %title_1char%  The first character of the token 'title'.
				- %title_2char%  The first two characters of the token 'title'
				- %subtitle%
				- %composer%
				- %lyricist%
			'''
			)
		)

		self.sub['rename'].add_argument('-d', '--dry-run',
			action='store_true', help='Do not rename the scores')

		self.sub['rename'].add_argument('-f', '--format',
			help='Format string.')

		self.sub['rename'].add_argument('-a', '--ascii',
			action='store_true', help='Use only ASCII characters.')

		self.sub['rename'].add_argument('-n', '--no-whitespace',
			action='store_true', help='Replace all whitespaces with dashes or \
			sometimes underlines.')

	# export

		self.sub['export'] = self.sparser.add_parser('export',
			help='Export the scores to PDFs or to the specified \
			extension.')

		self.sub['export'].add_argument('-e', '--extension',
			default='pdf', help='Extension to export. If this option \
			is omitted, then the default extension is "pdf".')

	# help

		self.sub['help'] = self.sparser.add_parser('help',
			help='Show help. Use "mscxyz.py help all" to show help \
			messages of all subcommands. Use \
			"mscxyz.py help <subcommand>" to show only help messages \
			for the given subcommand.')

		self.sub['help'].add_argument('-m', '--markdown',
			action='store_true', help='Show help in markdown format. \
			This option enables to generate the README file directly \
			form the command line output.')

		self.sub['help'].add_argument('-r', '--rst',
			action='store_true', help='Show help in reStructuresText \
			format. This option enables to generate the README file \
			directly form the command line output.')

	def addPositional(self):
		self.parser.add_argument('path', help='Path to a *.mscx file \
			or a folder which contains *.mscx files. In conjunction \
			with the subcommand "help" this positional parameter \
			accepts the names of all other subcommands or the word \
			"all".')

	def parse(self):
		return self.parser.parse_args()

	def heading(self, text, level=1):
		length = len(text)
		if args.markdown:
			print('\n' + ('#' * level) + ' ' + text + '\n')
		elif args.rst:
			if level == 1:
				underline = '='
			elif level == 2:
				underline = '-'
			elif level == 2:
				underline = '^'
			elif level == 2:
				underline = '"'
			else:
				underline = '-'
			print('\n' + text + '\n' + (underline * length) + '\n')
		else:
			print(text)

	def codeBlock(self, text):
		if args.markdown:
			print('```' + text + '```')
		elif args.rst:
			print('.. code-block::\n\n  ' + text.replace('\n', '\n  '))
		else:
			print(text)

	def showAllHelp(self):
		if args.path == 'all':
			self.heading('mscxyz.py', 1)
			self.codeBlock(self.parser.format_help())

			self.heading('Subcommands', 1)

			for sub, command in self.sub.iteritems():
				self.heading(command.prog, 2)
				self.codeBlock(command.format_help())

		else:
			self.codeBlock(self.sub[args.path].format_help())

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

	def export(self):
		score = self.fullpath
		mscore(['--export-to', score.replace('.mscx', '.' + args.extension), score])

class Rename(File):

	def __init__(self, fullpath):
		super(Rename, self).__init__(fullpath)
		self.score = Meta(self.fullpath)
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

	def prepareTokenSubstring(self, value, length):
		import unidecode
		import re
		value = value.lower()
		value = unidecode.unidecode(value)
		value = re.sub('[^A-Za-z]', '', value)
		return value[0:length]

	def getToken(self, token):
		title = self.score.get('title')
		if token == 'title_1char':
			return self.prepareTokenSubstring(title, 1)
		elif token == 'title_2char':
			return self.prepareTokenSubstring(title, 2)
		else:
			return self.score.get(token)

	def applyFormatString(self):
		import re
		output = args.format
		for token in re.findall('%(.*?)%', output):
			output = output.replace('%' + token + '%', self.getToken(token))

		self.workname = output

	def execute(self):
		if args.format:
			self.applyFormatString()

		if args.ascii:
			self.replaceGermanUmlaute()
			self.transliterate()

		if args.no_whitespace:
			self.replaceToDash(' ', ';', '?', '!', '_', '#', '&', '+', '/', ':')
			self.deleteCharacters(',', '.', '\'', '`', ')')
			self.cleanUp()

		if args.dry_run or args.verbose > 0:
			print(colored(self.basename, 'red') + ' -> ' + colored(self.workname, 'yellow'))

		if not args.dry_run:
			newpath = self.workname + '.' + self.extension
			create_dir(os.path.dirname(newpath))
			os.rename(self.fullpath, newpath)

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

	def mergeStyle(self):
		import lxml.etree as et
		style = et.parse(args.style.name).getroot()

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
			re_open(filename)

class Lyrics(Tree):

	def __init__(self, fullpath):
		super(Lyrics, self).__init__(fullpath)
		self.lyrics = self.normalizeLyrics()
		self.max = self.getMax()

	def normalizeLyrics(self):
		lyrics = []
		for lyric in self.tree.findall('.//Lyrics'):
			safe = {}
			safe['element'] = lyric
			number = lyric.find('no')

			if hasattr(number, 'text'):
				no = int(number.text) + 1
			else:
				no = 1
			safe['number'] = no

			lyrics.append(safe)

		return lyrics

	def getMax(self):
		max_lyric = 0
		for element in self.lyrics:
			if element['number'] > max_lyric:
				max_lyric = element['number']

		return max_lyric

	def remap(self):
		for pair in args.remap.split(','):
			old = pair.split(':')[0]
			new = pair.split(':')[1]
			for element in self.lyrics:
				if element['number'] == int(old):
					element['element'].find('no').text = str(int(new) - 1)

		self.write()

	def extractOneLyricVerse(self, number):
		score = Lyrics(self.fullpath)

		for element in score.lyrics:
			tag = element['element']

			if element['number'] != number:
				tag.getparent().remove(tag)
			elif number != 1:
				tag.find('no').text = '0'

		ext = '.' + self.extension
		new_name = score.fullpath.replace(ext, '_' + str(number) + ext)
		score.write(new_name)

	def extractLyrics(self):
		if args.number:
			self.extractOneLyricVerse(int(args.number))
		else:
			for number in range(1, self.max + 1):
				self.extractOneLyricVerse(number)

if __name__ == '__main__':

	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)

	parse = Parse()
	args = parse.parse()

	if args.subcommand == 'help':
		parse.showAllHelp()
		sys.exit()

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
			if args.style:
				verbose(args.style.name, 'style file', 'blue')
				clean.mergeStyle()
			clean.write()

		elif args.subcommand == 'lyrics':
			lyrics = Lyrics(score)
			if args.remap:
				lyrics.remap()
			else:
				lyrics.extractLyrics()

		elif args.subcommand == 'meta':
			meta = Meta(score)
			if args.show:
				meta.show()
			else:
				if args.json: meta.exportJson()
				meta.syncMetaTags()
				meta.write()

		elif args.subcommand == 'rename':
			rename = Rename(score)
			rename.execute()

		elif args.subcommand == 'export':
			verbose(score, '\nexport', 'yellow')
			verbose(args.extension, 'extension', 'green')
			export = File(score)
			export.export()
