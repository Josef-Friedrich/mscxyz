#! /usr/bin/env python

import sys
import os
import json
import errno
import shutil

def create_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' <musescore-file.mscx>')
    sys.exit()

ms_path = os.path.abspath(sys.argv[1])
ms_file = os.path.basename(sys.argv[1])


title = ms_file.replace('.mscx', '')

cleaned_path = ms_path.replace(' ', '-')
cleaned_file = os.path.basename(cleaned_path)
folder = cleaned_file.replace('.mscx', '')

data = {}
data['title'] = title

json_file = cleaned_path.replace('.mscx', '.json')
out_file = open(json_file, 'w')
json.dump(data, out_file, indent=4)                                    
out_file.close()

os.rename(ms_path, cleaned_path)

home = os.path.expanduser('~')

lieder_folder = home + '/git-repositories/content/lieder/songs' + '/' + folder
create_dir(lieder_folder)

shutil.copy2(cleaned_path, lieder_folder + '/score.mscx')
shutil.copy2(json_file, lieder_folder + '/info.json')

