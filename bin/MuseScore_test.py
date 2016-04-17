#! /usr/bin/env python
# -*- coding: utf-8 -*-

import musescore

files = musescore.get_files('mxl')

for file in files:
	print('\n' + file)
	musescore.convert_mxl(file)

