#! /usr/bin/env python

import os
import sys
import musescore

def execute(score, counter):
	print('File number ' + str(counter) + ': ' + score)
	ms = musescore.Meta(score)
	ms.clean()
	ms.syncMetaTags()
	ms.write()
	musescore.re_open(score)


if len(sys.argv) < 2:
	print('Usage: ' + os.path.basename(sys.argv[0]) + ' <start-number> <cycle-number>')
	sys.exit()

start_number = int(sys.argv[1])

if len(sys.argv) > 2:
	cycle_number = int(sys.argv[2])
else:
	cycle_number = 4

files = musescore.get_files('mscx')
hit = start_number
counter = 0
for score in files:
	counter += 1
	if hit == counter:
		execute(score, counter)
		hit = hit + cycle_number
