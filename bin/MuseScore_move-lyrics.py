#! /usr/bin/env python

import lxml.etree as et
import sys

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + 'MuseScoreFile.mscx <lyrics-number>')
    sys.exit()

ms_file = sys.argv[1]
lyrics_number = sys.arv[2]
new_file = ms_file.replace('.mscx', '_lyrics-no-' + lyrics_number + '.mscx')

print(new_file)

mscx = et.parse(ms_file)

for lyric in mscx.findall('.//Lyrics'):
    number = lyric.find('no')
    if hasattr(number, 'text'):
        no = number.text
    else:
        no = '0'

    if no != '2':
        lyric.getparent().remove(lyric)
    else:
        number.text = '0'

# To get closing tag use method 'html'
mscx.write(new_file, pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')
