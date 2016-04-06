#! /usr/bin/env python

import sys
import os
import json

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-file.mscx>')
    sys.exit()

ms_path = os.path.abspath(sys.argv[1])
ms_file = os.path.basename(sys.argv[1])


title = ms_file.replace('.mscx', '')

cleaned_path = ms_path.replace(' ', '-')

data = {}
data['title'] = title

out_file = open(cleaned_path.replace('.mscx', '.json'), 'w')
json.dump(data, out_file, indent=4)                                    
out_file.close()

os.rename(ms_path, cleaned_path)
