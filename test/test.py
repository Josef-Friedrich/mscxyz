import os
import unittest

import mscxyz.meta as m

def get_testfile(filename):
    return os.path.join(os.path.dirname(__file__), './' + filename)

meta = m.Meta(get_testfile('test.mscx'))

class TestMeta(unittest.TestCase):

    def test_get(self):
        self.assertEqual(meta.get('title'), 'Title')
        self.assertEqual(meta.get('composer'), 'Composer')

if __name__ == '__main__':
    unittest.main()
