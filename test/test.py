import os
import unittest

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

if __name__ == '__main__':
	unittest.main()
