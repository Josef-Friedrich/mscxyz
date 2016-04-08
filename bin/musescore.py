import os
import sys
import subprocess
import json
import errno

def get_style_folder():
	style_folder = 'MuseScore2/Stile'
	home = os.path.expanduser('~')
	if os.path.exists(home + '/Documents/' + style_folder):
		return home + '/Documents/' + style_folder
	elif os.path.exists(home + '/Dokumente/' + style_folder):
		return home + '/Dokumente/' + style_folder

def re_open(input_file, output_file):
	mac_ms = '/Applications/MuseScore 2.app/Contents/MacOS/mscore'
	if os.path.exists(mac_ms):
		subprocess.call([mac_ms, "-o", output_file, input_file])
	else:
		subprocess.call(["mscore", "-o", output_file, input_file])

def create_info(json_file, data):
	out_file = open(json_file, 'w')
	json.dump(data, out_file, indent=4)
	out_file.close()

def create_dir(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def get_lieder_folder():
	return os.path.expanduser('~') + '/git-repositories/content/lieder/songs/'
