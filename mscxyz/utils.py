# -*- coding: utf-8 -*-

"""A collection of useful utility functions"""

import subprocess
import os
import sys
import signal
from termcolor import colored

def mscore(commands):
	mac = '/Applications/MuseScore.app/Contents/MacOS/mscore'
	if os.path.exists(mac):
		executeable = mac
	else:
		executeable = 'mscore'

	commands.insert(0, executeable)

	OUT=None
	#OUT = open(os.devnull, 'wb')
	subprocess.call(commands, stdout=OUT, stderr=OUT)
	#OUT.close()

def re_open(input_file):
	mscore(['-o', input_file, input_file])

def convert_mxl(input_file):
	output_file = input_file.replace('.mxl', '.mscx')
	mscore(['-o', output_file, input_file])
	os.remove(input_file)

def exit_gracefully(signum, frame):
	original_sigint = signal.getsignal(signal.SIGINT)
	signal.signal(signal.SIGINT, exit_gracefully)
	# Restore the original signal handler as otherwise evil things will
	# happen, in raw_input when CTRL+C is pressed, and our signal
	# handler is not re-entrant
	signal.signal(signal.SIGINT, original_sigint)

	try:
		if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
			print('Quitting ...')
			sys.exit(1)

	except KeyboardInterrupt:
		print("Ok ok, quitting")
		sys.exit(1)

	# restore the exit gracefully handler here
	signal.signal(signal.SIGINT, exit_gracefully)

def print_desc(text, description='', color='red'):
	prefix = ''
	if description:
		prefix = colored(description, color) + ': '
	print(prefix + text)

def verbose(text, description='', color='red', verbosity=1):
	if verbose >= 1:
		print_desc(text=text, description=description, color=color)
