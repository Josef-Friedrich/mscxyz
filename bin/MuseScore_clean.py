#! /usr/bin/env python

import musescore

musescore.catch_args(1, '<MuseScore-file.mscx>')
musescore.backup()

# To upgrade to newest MuseScore version.
musescore.re_open()

tree = musescore.Tree()
tree.removeTagsByXPath('/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
tree.stripTags('font', 'b', 'i')
tree.write()

# To fix xml format
musescore.re_open()