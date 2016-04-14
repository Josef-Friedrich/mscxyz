#! /usr/bin/env python

import sys
import musescore

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-fle.mscx>')
    sys.exit()

ms_file = sys.argv[1]

musescore.backup(ms_file)

# To upgrade to newest MuseScore version.
musescore.re_open(ms_file, ms_file)

tree = musescore.Tree(ms_file)
tree.removeTagsByXPath('/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
tree.stripTags('font', 'b', 'i')
tree.write()

# To fix xml format
musescore.re_open(ms_file, ms_file)