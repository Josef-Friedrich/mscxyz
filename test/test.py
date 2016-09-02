import os
import unittest
import mscxyz
from cStringIO import StringIO
import sys

class Capturing(list):

	def __init__(self, channel='out'):
		self.channel = channel

	def __enter__(self):
		if self.channel == 'out':
			self._pipe = sys.stdout
			sys.stdout = self._stringio = StringIO()
		elif self.channel == 'err':
			self._pipe = sys.stderr
			sys.stderr = self._stringio = StringIO()
		return self

	def __exit__(self, *args):
		self.extend(self._stringio.getvalue().splitlines())
		if self.channel == 'out':
			sys.stdout = self._pipe
		elif self.channel == 'err':
			sys.stderr = self._pipe

def get_testfile(filename):
	return os.path.join(os.path.dirname(__file__), 'files',  filename + '.mscx')

class TestMeta(unittest.TestCase):
	def setUp(self):
		from mscxyz.meta import Meta
		self.meta = Meta(get_testfile('simple'), args=None)

	def test_get(self):
		self.assertEqual(self.meta.get('title'), 'Title')
		self.assertEqual(self.meta.get('composer'), 'Composer')

class TestFile(unittest.TestCase):

	def setUp(self):
		from mscxyz.fileloader import File
		self.file = File(get_testfile('simple'), args=None)

	def test_file_object_initialisation(self):
		self.assertEqual(self.file.fullpath, get_testfile('simple'))
		self.assertEqual(self.file.dirname, os.path.dirname(get_testfile('simple')))
		self.assertEqual(self.file.filename, 'simple.mscx')
		self.assertEqual(self.file.basename, 'simple')
		self.assertEqual(self.file.extension, 'mscx')

class TestCommandlineInterface(unittest.TestCase):

	def test_help_short(self):
		with self.assertRaises(SystemExit) as cm:
			with Capturing() as output:
				mscxyz.execute(['-h'])
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '0')

	def test_help_long(self):
		with self.assertRaises(SystemExit) as cm:
			with Capturing() as output:
				mscxyz.execute(['--help'])
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '0')

	def test_without_arguments(self):
		with self.assertRaises(SystemExit) as cm:
			with Capturing('err') as output:
				mscxyz.execute()
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '2')

	def test_help_text(self):
		with self.assertRaises(SystemExit) as cm:
			with Capturing() as output:
				mscxyz.execute(['-h'])
		self.assertEqual(output[0], 'usage: test.py [-h] [-b] [-g GLOB] [-p PICK] [-c CYCLE_LENGTH] [-v]')

class TestRename(unittest.TestCase):
	def setUp(self):
		from mscxyz.rename import Rename
		self.simple = Rename(get_testfile('simple'))
		self.unicode = Rename(get_testfile('unicode'))

	def test_option_format_default(self):
		self.simple.applyFormatString()
		self.assertEqual(self.simple.workname, u'Title (Composer)')

	def test_option_format_given(self):
		self.simple.applyFormatString('${composer}_${title}')
		self.assertEqual(self.simple.workname, u'Composer_Title')

	def test_option_asciify(self):
		self.unicode.applyFormatString()
		self.unicode.asciify()
		self.assertEqual(self.unicode.workname, 'Tuetlae (Coempoesser)')

	def test_option_no_whitespace(self):
		self.simple.applyFormatString()
		self.simple.noWhitespace()
		self.assertEqual(self.simple.workname, 'Title_Composer')


if __name__ == '__main__':
	unittest.main()
