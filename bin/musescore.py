import os
import sys
import subprocess
import json
import errno
import shutil

def get_style_folder():
	style_folder = 'MuseScore2/Stile'
	home = os.path.expanduser('~')
	if os.path.exists(home + '/Documents/' + style_folder):
		return home + '/Documents/' + style_folder
	elif os.path.exists(home + '/Dokumente/' + style_folder):
		return home + '/Dokumente/' + style_folder

def re_open(input_file, output_file):
	mac_ms = '/Applications/MuseScore.app/Contents/MacOS/mscore'
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

def backup(backup_file):
	shutil.copy2(backup_file, backup_file.replace('.mscx', '_bak.mscx'))

def remove(ms_et, xpath_string):
	for to_remove in ms_et.xpath(xpath_string):
		to_remove.getparent().remove(to_remove)

def get_metatag(ms_et, name):
	element = ms_et.getroot().xpath("//metaTag[@name='" + name + "']")
	return element[0].text