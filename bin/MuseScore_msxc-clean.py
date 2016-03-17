#! /usr/bin/env python

import lxml.etree as et
mscx = et.parse('parse-xml_in.mscx')
defaultstyle = et.parse('_style/default.mss').getroot()

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
mscx.write('parse-xml_out.mscx', pretty_print=True, xml_declaration=True, method='html', encoding='UTF-8')
