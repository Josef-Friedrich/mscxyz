# -*- coding: utf-8 -*-

import os
import sys
import signal
import lxml.etree
from termcolor import colored, cprint

reload(sys)
sys.setdefaultencoding('utf8')

def mscore(commands, args=None):
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

def re_open(input_file, args):
	mscore(['-o', input_file, input_file], args)

def convert_mxl(input_file):
	output_file = input_file.replace('.mxl', '.mscx')
	mscore(['-o', output_file, input_file])
	os.remove(input_file)

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

def verbose(text, description='', color='red', verbosity=1, args=None):
	if args.verbose >= verbosity:
		print_desc(text=text, description=description, color=color)

def execute(args=None):
	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)
	from parse import Parse
	from batch import Batch

	parse = Parse()
	args = parse.parse(args)

	if args.subcommand == 'help':
		parse.showAllHelp()
		sys.exit()

	batch = Batch(args.path, args.glob)

	if args.pick:
		batch.pick(args.pick, args.cycle_length)

	files = batch.getFiles()
	for score in files:

		if args.backup:
			backup = File(score, args)
			backup.backup()

		if args.subcommand == 'clean':
			verbose(score, '\nclean', 'yellow', args=args)
			from tree import Tree
			clean = Tree(score, args)
			clean.clean()
			if args.style:
				verbose(args.style.name, 'style file', 'blue', args=args)
				clean.mergeStyle()
			clean.write()

		elif args.subcommand == 'lyrics':
			from lyrics import Lyrics
			lyrics = Lyrics(score, args)
			if args.remap:
				lyrics.remap()
			else:
				lyrics.extractLyrics()

		elif args.subcommand == 'meta':
			from meta import Meta
			meta = Meta(score, args)
			if args.show:
				meta.show()
			else:
				if args.json: meta.exportJson()
				meta.syncMetaTags()
				meta.write()

		elif args.subcommand == 'rename':
			from rename import Rename
			rename = Rename(score, args)
			if args.format:
				rename.applyFormatString(args.format)

			if args.ascii:
				self.asciify()

			if args.no_whitespace:
				self.noWhitespace
			rename.execute()

		elif args.subcommand == 'export':
			verbose(score, '\nexport', 'yellow', args=args)
			verbose(args.extension, 'extension', 'green', args=args)
			from fileloader import File
			export = File(score, args)
			export.export()
