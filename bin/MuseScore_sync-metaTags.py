#! /usr/bin/env python

import musescore

files = musescore.get_all_mscx()

for file in files:
	print('\n\n' + file)
	meta = musescore.Meta(file)
	meta.syncMetaTags()
	meta.write()
	#meta.clean()
	#meta.setVBox('Title', 'Test')
	#meta.write()

