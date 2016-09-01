import os
import unittest
import mscxyz

def get_testfile(filename):
	return os.path.join(os.path.dirname(__file__), './' + filename)

class TestMeta(unittest.TestCase):
	def setUp(self):
		from mscxyz.meta import Meta
		self.meta = Meta(get_testfile('test.mscx'), args=None)

	def test_get(self):
		self.assertEqual(self.meta.get('title'), 'Title')
		self.assertEqual(self.meta.get('composer'), 'Composer')

class TestFile(unittest.TestCase):

	def setUp(self):
		from mscxyz.fileloader import File
		self.file = File(get_testfile('test.mscx'), args=None)

	def test_file_object_initialisation(self):
		self.assertEqual(self.file.fullpath, get_testfile('test.mscx'))
		self.assertEqual(self.file.dirname, os.path.dirname(get_testfile('test.mscx')))
		self.assertEqual(self.file.filename, 'test.mscx')
		self.assertEqual(self.file.basename, 'test')
		self.assertEqual(self.file.extension, 'mscx')

class TestCommandlineInterface(unittest.TestCase):

	def test_help_short(self):
		with self.assertRaises(SystemExit) as cm:
			mscxyz.execute(['-h'])
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '0')

	def test_help_long(self):
		with self.assertRaises(SystemExit) as cm:
			mscxyz.execute(['--help'])
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '0')

	def test_without_arguments(self):
		with self.assertRaises(SystemExit) as cm:
			mscxyz.execute()
		the_exception = cm.exception
		self.assertEqual(str(the_exception), '2')

if __name__ == '__main__':
	unittest.main()
