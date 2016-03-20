#! /usr/bin/env python

import lxml.etree as et
import sys
import subprocess
import os

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
    sys.exit()

ms_file = sys.argv[1]

mscx = et.parse(ms_file)

musescore_user_folder = subprocess.check_output(["xdg-user-dir", "DOCUMENTS"])
musescore_user_folder = musescore_user_folder.replace('\n', '') + '/MuseScore2'
defaultstyle = et.parse(musescore_user_folder + '/Stile/default.mss').getroot()

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

output_file = tmp_file.replace('_tmp.mscx', '_cleaned.mscx')
subprocess.call(["mscore", "-o", output_file, tmp_file])

os.remove(tmp_file)
