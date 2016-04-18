#! /usr/bin/env python
# -*- coding: utf-8 -*-

import musescore

files = musescore.get_files('mxl')
for score in files:
	musescore.convert_mxl(score)
