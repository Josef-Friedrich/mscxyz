#! /usr/bin/env python

import musescore

files = musescore.get_all_mscx()

for file in files:
	meta = musescore.Meta(file)
	print(meta.getMetaTagText('composer'))
t