"""Test API interface. The mscxyz module is used in Python code not on the
command line."""


from mscxyz import (
    MscoreLyricsInterface,
    MscoreMetaInterface,
    MscoreStyleInterface,
    MuseScoreFile,
    exec_mscore_binary,
)


class TestApi:
    def test_api(self):
        assert MuseScoreFile
        assert MuseScoreFile
        assert MscoreLyricsInterface
        assert MscoreMetaInterface
        assert MscoreStyleInterface
        assert exec_mscore_binary
