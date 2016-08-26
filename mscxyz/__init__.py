# -*- coding: utf-8 -*-

import os
import sys
import signal
import lxml.etree
from termcolor import colored, cprint
import meta.Meta as Meta
import parse.Parse as Parse

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
