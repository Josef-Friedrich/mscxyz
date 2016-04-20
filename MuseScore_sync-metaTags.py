#! /usr/bin/env python

import argparse
import musescore

parser = argparse.ArgumentParser(description='Synchronize the values of\
	the first vertical frame (title, composer, lyricist) with the \
	corresponding metadata fields.')
parser.add_argument('path', help='Path to a *.mscx file or a folder\
	which contains *.mscx files.')
parser.add_argument('-j', '--json', action='store_true',
	help='Additionally write the metadata to a json file.')


subparsers = parser.add_subparsers(help='Extract lyrics')
parser_lyrics = subparsers.add_parser('lyrics', help='Extract lyrics')
parser_lyrics.add_argument('-n', '--number', action='store_true', help='Number of lyrics verse.')

args = parser.parse_args()

files = musescore.get_mscx(args.path)
for score in files:
	print(score)
