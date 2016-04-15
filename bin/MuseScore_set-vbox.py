#! /usr/bin/env python

import musescore

musescore.catch_args()

tree = musescore.Tree()

tree.setVBox('Composer', 'Ludwig van Beethoven')

tree.write()

musescore.re_open()

print(tree.getVBox('Composer'))