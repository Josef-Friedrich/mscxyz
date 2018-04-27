# -*- coding: utf-8 -*-

"""Test module “utils.py”."""

from mscxyz.utils import get_mscore_bin
import six
import unittest
if six.PY3:
    from unittest import mock
else:
    import mock


# @unittest.skipIf('rewritten')
class TestFunctionGetMscoreBin(unittest.TestCase):

    @mock.patch('platform.system')
    @mock.patch('os.path.exists')
    @mock.patch('subprocess.check_output')
    def test_output(self, check_output, exists, system):
        system.return_value = 'Linux'
        exists.return_value = True
        path = bytes('/usr/local/bin/mscore\n'.encode('utf-8'))
        check_output.return_value = path
        output = get_mscore_bin()
        self.assertEqual(output, '/usr/local/bin/mscore')


if __name__ == '__main__':
    unittest.main()
