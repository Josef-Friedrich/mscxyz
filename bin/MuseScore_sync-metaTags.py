#! /usr/bin/env python

import musescore

musescore.catch_args()

meta = musescore.Meta()
meta.createVBox()
meta.write()
