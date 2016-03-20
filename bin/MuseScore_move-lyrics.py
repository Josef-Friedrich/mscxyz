#! /usr/bin/env python

import lxml.etree as et
import sys

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + 'MuseScoreFile.mscx <lyrics-number>')
    sys.exit()
else:
    print('troll')

mscx = et.parse('affen.mscx')

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
mscx.write('affen_out.mscx', pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')
