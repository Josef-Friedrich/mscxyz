#! /usr/bin/env python

import musescore

files = musescore.get_all_mscx()

for file in files:
	print(file)
	meta = musescore.Meta(file)
	print(meta.getVBox('Title'))

