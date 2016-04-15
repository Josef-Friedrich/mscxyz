#! /usr/bin/env python

import musescore

musescore.catch_args()


tree = musescore.Tree()

print(tree.getVBox('Composer'))

#0           <style>Title</style>
# 121           <text>Lady</text>
# 122           </Text>

# 123         <Text>
# 124           <style>Composer</style>                                                125           <text>Lionel Richie</text>


