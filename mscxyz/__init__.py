# -*- coding: utf-8 -*-

"""A command line tool to manipulate the XML based *.mscX and *.mscZ
files of the notation software MuseScore
"""

import sys

from mscxyz.tree import Tree
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.rename import Rename
from mscxyz.parse import Parse
from mscxyz.batch import Batch

reload(sys)
sys.setdefaultencoding('utf8')

def execute(args=None):
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
				score.mergeStyle()
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
				if args.json: score.exportJson()
				score.syncMetaTags()
				score.write()

		elif args.subcommand == 'rename':
			score = Rename(file)
			if args.format:
				score.applyFormatString(args.format)

			if args.ascii:
				score.asciify()

			if args.no_whitespace:
				score.noWhitespace()
			score.execute()

		elif args.subcommand == 'export':
			from fileloader import File
			score = File(file)
			score.export(args.extension)

		output.append(score)

	return output

if __name__ == '__main__':
	execute()
