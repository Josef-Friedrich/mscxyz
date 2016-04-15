#! /usr/bin/env python

import musescore

mscx_files = musescore.get_all_mscx()

for mscx_file in mscx_files:
	print('Musescore: ' + mscx_file)
	tree = musescore.Tree(mscx_file)
	print(tree.getMetaTag('workTitle'))