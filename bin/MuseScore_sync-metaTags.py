#! /usr/bin/env python

import musescore

musescore.catch_args()

tree = musescore.Tree()
print(tree.getVBox('Title'))
tree.setVBox('Title', '5. Symphonie')
#print(tree.getVBox('Title'))
print(tree.getVBox('Title'))
tree.write()
