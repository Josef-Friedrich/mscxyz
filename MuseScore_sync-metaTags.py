#! /usr/bin/env python

import musescore

musescore.catch_args()

files = musescore.get_mscx(musescore.score)
for score in files:
	print(score)
