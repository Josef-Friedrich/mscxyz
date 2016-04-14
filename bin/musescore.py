import os
import sys
import subprocess
import json
import errno
import shutil
import lxml.etree as et

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

class Tree:
	def __init__(self, file_name):
		self.file_name = file_name
		self.tree = et.parse(file_name)

	def stripTags(self, *tags):
		et.strip_tags(self.tree, tags)

	def removeTagsByXPath(self, *xpath_strings):
		for xpath_string in xpath_strings:
			for rm in self.tree.xpath(xpath_string):
				rm.getparent().remove(rm)

	def getMetaTag(self, name):
		element = self.tree.getroot().xpath("//metaTag[@name='" + name + "']")
		return element[0].text

	def write(self):
		self.tree.write(self.file_name, encoding='UTF-8')

