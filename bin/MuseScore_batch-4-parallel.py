#! /usr/bin/env python

import os
import sys
import musescore

if len(sys.argv) < 2:
	print('Usage: ' + os.path.basename(sys.argv[0]) + ' <number_1-4>')
	sys.exit()

files = musescore.get_files('mscx')

counter = 0
for score in files:
	counter += 1
	print(str(counter) + ': ' + score)

