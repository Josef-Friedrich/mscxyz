#! /usr/bin/env python

import lxml.etree as et
import sys

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx> <lyrics-number_1-x>')
    sys.exit()

ms_file = sys.argv[1]
lyrics_no_display = sys.argv[2]
lyrics_no = str(int(lyrics_no_display) - 1)
new_file = ms_file.replace('.mscx', '_Lyrics-no-' + lyrics_no_display + '.mscx')

print(new_file)

mscx = et.parse(ms_file)

for lyric in mscx.findall('.//Lyrics'):
    number = lyric.find('no')
    if hasattr(number, 'text'):
        no = number.text
    else:
        no = '0'

    if no != lyrics_no:
        lyric.getparent().remove(lyric)
    elif hasattr(number, 'text'):
        number.text = '0'

# To get closing tag use method 'html'
mscx.write(new_file, pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')
