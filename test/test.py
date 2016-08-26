import unittest

import mscxyz.mscxyz as m
meta = m.Meta('./test.mscx')

class TestMeta(unittest.TestCase):

    def test_get(self):
        self.assertEqual(meta.get('title'), 'Title')
        self.assertEqual(meta.get('composer'), 'Composer')

if __name__ == '__main__':
    unittest.main()
