"""Test API interface. The mscxyz module is used in Python code not on the
command line."""

import unittest

from mscxyz import (
    MscoreFile,
    MscoreLyricsInterface,
    MscoreMetaInterface,
    MscoreStyleInterface,
    MscoreXmlTree,
    exec_mscore_binary,
)


class TestApi(unittest.TestCase):
    def test_api(self):
        self.assertTrue(MscoreFile)
        self.assertTrue(MscoreXmlTree)
        self.assertTrue(MscoreLyricsInterface)
        self.assertTrue(MscoreMetaInterface)
        self.assertTrue(MscoreStyleInterface)
        self.assertTrue(exec_mscore_binary)


if __name__ == "__main__":
    unittest.main()
