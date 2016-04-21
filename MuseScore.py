#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
			meta.getAllMetaTags()
			#rename.debug()
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
