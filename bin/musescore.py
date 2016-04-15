import os
import sys
import subprocess
import json
import errno
import shutil
import lxml.etree as et

# Name of the score file
score = ''

def catch_args(number_of_args = 1, usage_text = ' <musescore-fle.mscx>'):
	if len(sys.argv) < number_of_args + 1:
		print('Usage: ' + os.path.basename(sys.argv[0]) + ' ' + usage_text)
		sys.exit()

	global score
	score = sys.argv[1]

def get_style_folder():
	style_folder = 'MuseScore2/Stile'
	home = os.path.expanduser('~')
	if os.path.exists(home + '/Documents/' + style_folder):
		return home + '/Documents/' + style_folder
	elif os.path.exists(home + '/Dokumente/' + style_folder):
		return home + '/Dokumente/' + style_folder

def re_open():
	mac_ms = '/Applications/MuseScore.app/Contents/MacOS/mscore'
	if os.path.exists(mac_ms):
		subprocess.call([mac_ms, "-o", score, score])
	else:
		subprocess.call(["mscore", "-o", score, score])

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

def backup():
	shutil.copy2(score, score.replace('.mscx', '_bak.mscx'))

def get_all_mscx():
	path = os.getcwd()

	mscx_files = []

	for root, dirs, files in os.walk(path):
		for file in files:
			if file.endswith('.mscx'):
				file_path = os.path.join(root, file)
				mscx_files.append(file_path)

	return mscx_files

class Tree:
	def __init__(self, file_name = ''):
		if not file_name:
			self.file_name = score
		else:
			self.file_name = file_name
		self.tree = et.parse(self.file_name)

	def stripTags(self, *tags):
		et.strip_tags(self.tree, tags)

	def removeTagsByXPath(self, *xpath_strings):
		for xpath_string in xpath_strings:
			for rm in self.tree.xpath(xpath_string):
				rm.getparent().remove(rm)

	def getMetaTag(self, name):
		element = self.tree.getroot().xpath("//metaTag[@name='" + name + "']")
		return element[0].text

	def setMetaTag(self, name, text):
		element = self.tree.getroot().xpath("//metaTag[@name='" + name + "']")
		element[0].text =  text

	def write(self):
		self.tree.write(self.file_name, encoding='UTF-8')


	def printFilename(self):
		print(fiile)

