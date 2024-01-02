"""Test submodule “utils.py”."""

from unittest import mock

from mscxyz.utils import get_args, get_mscore_bin, mscore

args = get_args()
args.general_executable = None


class TestFunctionGetMscoreBin:
    @mock.patch("mscxyz.utils.get_args")
    @mock.patch("platform.system")
    @mock.patch("os.path.exists")
    @mock.patch("subprocess.check_output")
    def test_output(
        self,
        check_output: mock.Mock,
        exists: mock.Mock,
        system: mock.Mock,
        get_args: mock.Mock,
    ) -> None:
        get_args.return_value = args
        system.return_value = "Linux"
        exists.return_value = True
        path = bytes("/usr/local/bin/mscore\n".encode("utf-8"))
        check_output.return_value = path
        output = get_mscore_bin()
        assert output == "/usr/local/bin/mscore"


class TestFunctionMscore:
    @mock.patch("mscxyz.utils.get_mscore_bin")
    @mock.patch("subprocess.Popen")
    def test_function(self, popen: mock.Mock, get_mscore_bin: mock.Mock) -> None:
        get_mscore_bin.return_value = "/bin/mscore"
        popen.return_value = mock.MagicMock(returncode=0)
        result = mscore(["--export-to", "troll.mscz", "lol.mscx"])
        assert result.returncode == 0
