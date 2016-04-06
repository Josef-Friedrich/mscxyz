#! /usr/bin/env python

import sys
import os
import json

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-file.mscx>')
    sys.exit()


ms_file = os.path.basename(sys.argv[1])

ms_file = ms_file.replace('.mscx', '')

print(ms_file)

sys.exit()


data = {}
data['title'] = ms_file

out_file = open(ms_file + '.json','w')
json.dump(data, out_file, indent=4)                                    
out_file.close()
