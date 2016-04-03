#! /usr/bin/env python

import lxml.etree as et
import sys
import json

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
    sys.exit()

ms_file = sys.argv[1]

mscx = et.parse(ms_file)

def get_meta_tag(name):
    element = mscx.getroot().xpath("//metaTag[@name='" + name + "']")
    return element[0].text


title = get_meta_tag('workTitle')
composer = get_meta_tag('composer')
lyricist = get_meta_tag('lyricist')

print('Title: ' + str(title) + '; Composer: ' + str(composer) + '; Lyricist: ' + str(lyricist))

data = {}
data['title'] = title

if composer:
    data['composer'] = composer

if lyricist:
    data['lyricist'] = lyricist

out_file = open("test.json","w")
json.dump(data,out_file, indent=4)                                    
out_file.close()
