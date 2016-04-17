#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import musescore

numbers = ['1', '2', '3', '4', '5']

for number in numbers:
	print(number)
	files = musescore.get_files('mxl.' + number)

	for score in files:
		new_number = int(number) + 1 
		new_score = score.replace('.mxl.' + number, '[' + str(new_number) + '].mxl')
		print(score + ' -> ' + new_score)
		os.rename(score, new_score)

		#musescore.convert_mxl(file)

