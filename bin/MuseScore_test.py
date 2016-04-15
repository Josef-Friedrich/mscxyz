#! /usr/bin/env python
# -*- coding: utf-8 -*-

import musescore

filename = u',Lasst, uns heute fröhlich springen!'

print(musescore.clean_filename(filename))