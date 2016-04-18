#! /usr/bin/env python

import musescore

musescore.catch_args()

tree = musescore.Tree()

print(tree.getVBox('Composer'))
