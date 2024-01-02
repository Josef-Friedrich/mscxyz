"""Test API interface. The mscxyz module is used in Python code not on the
command line."""


from mscxyz import (
    MscoreFile,
    MscoreLyricsInterface,
    MscoreMetaInterface,
    MscoreStyleInterface,
    MscoreXmlTree,
    exec_mscore_binary,
)


class TestApi:
    def test_api(self):
        assert MscoreFile
        assert MscoreXmlTree
        assert MscoreLyricsInterface
        assert MscoreMetaInterface
        assert MscoreStyleInterface
        assert exec_mscore_binary
