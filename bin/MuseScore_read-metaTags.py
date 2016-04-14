#! /usr/bin/env python

import lxml.etree as et
import sys
import musescore

if len(sys.argv) < 2:
	print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
	sys.exit()

ms_file = sys.argv[1]

tree = musescore.Tree(ms_file)


musescore.score = sys.argv[1]

# arranger
# composer
# copyright
# creationDate
# lyricist
# movementNumber
# movementTitle
# platform
# poet
# source
# translator
# workNumber
# workTitle

composer = tree.getMetaTag('composer')
print(composer)
platform = tree.getMetaTag('platform')
print(platform)

tree.printFilename()