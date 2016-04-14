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

sys.exit()

mscx = et.parse(ms_file)

# Delete synthesizer tag
for synthesizer in mscx.xpath('/museScore/Score/Synthesizer'):
	synthesizer.getparent().remove(synthesizer)

# Remove old style
for style in mscx.xpath('/museScore/Score/Style'):
	style.getparent().remove(style)

# Add styles from .mss file
for score in mscx.xpath('/museScore/Score'):
	score.insert(0, defaultstyle[0])

# strip tags in lyrics
et.strip_tags(mscx, 'font', 'b', 'i')

# To get closing tag use method 'html'
tmp_file = ms_file.replace('.mscx', '_tmp.mscx')
mscx.write(tmp_file, pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')



musescore.re_open(tmp_file, ms_file)

