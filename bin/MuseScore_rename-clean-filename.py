#! /usr/bin/env python
# -*- coding: utf-8 -*-

import musescore

files = musescore.get_all_mscx()

for file in files:
	rename = musescore.Rename(file)
	rename.transliterate()
	rename.clean()
	rename.debug()

