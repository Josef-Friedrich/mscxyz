# -*- coding: utf-8 -*-

"""A command line tool to manipulate the XML based *.mscX and *.mscZ
files of the notation software MuseScore
"""

import sys
import signal

from mscxyz.tree import Tree
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.rename import Rename
from mscxyz.parse import Parse
from mscxyz.batch import Batch
from mscxyz.utils import exit_gracefully

reload(sys)
sys.setdefaultencoding('utf8')

def execute(args=None):
	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)

	parse = Parse()
	args = parse.parse(args)

	if args.subcommand == 'help':
		parse.showAllHelp()
		sys.exit()

	batch = Batch(args.path, args.glob)

	if args.pick:
		batch.pick(args.pick, args.cycle_length)

	files = batch.getFiles()

	output = []
	for file in files:

		if args.backup:
			from mscxyz.fileloader import File
			score = File(file)
			score.backup()

		if args.subcommand == 'clean':
			score = Tree(file)
			score.clean()
			if args.style:
				verbose(args.style.name, 'style file', 'blue')
				clean.mergeStyle()
			score.write()

		elif args.subcommand == 'lyrics':
			score = Lyrics(file)
			if args.remap:
				score.remap()
			elif args.fix:
				score.fixLyrics()
			else:
				score.extractLyrics(args.number)

		elif args.subcommand == 'meta':
			score = Meta(file)
			if args.show:
				score.show()
			else:
				if args.json: meta.exportJson()
				score.syncMetaTags()
				score.write()

		elif args.subcommand == 'rename':
			score = Rename(file, args)
			if args.format:
				score.applyFormatString(args.format)

			if args.ascii:
				self.asciify()

			if args.no_whitespace:
				self.noWhitespace
			score.execute()

		elif args.subcommand == 'export':
			verbose(file, '\nexport', 'yellow')
			verbose(args.extension, 'extension', 'green')
			from fileloader import File
			score = File(file, args)
			score.export()

		output.append(score)

	return output

if __name__ == '__main__':
	execute()
