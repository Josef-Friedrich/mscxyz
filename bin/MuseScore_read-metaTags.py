#! /usr/bin/env python

import lxml.etree as et
import sys
import musescore

if len(sys.argv) < 2:
	print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
	sys.exit()

ms_file = sys.argv[1]

ms_et = et.parse(ms_file)

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

composer = musescore.get_metatag(ms_et, 'composer')
composer = musescore.get_metatag(ms_et, 'platform')
print(composer)