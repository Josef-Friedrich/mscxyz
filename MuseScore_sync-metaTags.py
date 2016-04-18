#! /usr/bin/env python

import musescore

files = musescore.get_files('mxl')

for file in files:
	print('\n' + file)
	# meta = musescore.Meta(file)
	# meta.clean()
	# meta.syncMetaTags()
	# meta.write()
	# #meta.clean()
	# #meta.setVBox('Title', 'Test')
	# #meta.write()
	# musescore.score = file
	# musescore.re_open()

