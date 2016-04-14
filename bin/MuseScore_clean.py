#! /usr/bin/env python

import lxml.etree as et
import sys
import shutil
import musescore

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
    sys.exit()

ms_file = sys.argv[1]

musescore.backup(ms_file)

# To upgrade to newest MuseScore version.
musescore.re_open(ms_file, ms_file)

ms_et = et.parse(ms_file)

musescore.remove(ms_et, '//LayoutBreak')
musescore.remove(ms_et, '/museScore/Score/Style')
musescore.remove(ms_et, '//StemDirection')

# strip tags in lyrics
et.strip_tags(ms_et, 'font', 'b', 'i')

ms_et.write(ms_file, encoding='UTF-8')

# To fix xml format
musescore.re_open(ms_file, ms_file)