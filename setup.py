from setuptools import setup

setup(
	name = 'mscxyz',
	version = '0.0.2',
	author = 'Josef Friedrich',
	author_email = 'josef@friedrich.rocks',
	description = ('A command line tool to manipulate the XML based *.mscX and *.mscZ files of the notation software MuseScore.'),
	license = 'MIT',
	packages = ['mscxyz'],
	keywords = 'audio',
	url = 'https://github.com/Josef-Friedrich/mscxyz',
	install_requires = [
		'lxml',
	],
	scripts = ['bin/mscx-manager'],
	classifiers = [
		'Development Status :: 3 - Alpha',
	],
	zip_safe=False,
)
