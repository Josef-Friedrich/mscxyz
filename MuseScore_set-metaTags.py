#! /usr/bin/env python

import musescore

musescore.catch_args()

tree = musescore.Tree()
tree.setMetaTag('composer', 'August Hoegn')
tree.write()

