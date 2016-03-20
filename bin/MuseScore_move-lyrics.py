#! /usr/bin/env python

import lxml.etree as et
mscx = et.parse('affen.mscx')

for lyric in mscx.findall('.//Lyrics'):
    number = lyric.find('no')
    if hasattr(number, 'text'):
        no = number.text
    else:
        no = '0'

    if no != '2':
        print('nicht zwei')
        lyric.getparent().remove(lyric)

# To get closing tag use method 'html'
mscx.write('affen_out.mscx', pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')
