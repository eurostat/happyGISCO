# -*- coding: utf-8 -*-

"""
.. _mod_tests_test_main_

Unit test of module :mod:`happygisco`.
"""

from pytest import raises

# The parametrize function is generated, so this doesn't work:
#     from pytest.mark import parametrize
import pytest
parametrize = pytest.mark.parametrize

import happygisco

class TestMain(object):
    @parametrize('helparg', ['-h', '--help'])
    def test_help(self, helparg, capsys):
        with raises(SystemExit) as exc_info:
            happygisco.main(['progname', helparg])
        out, err = capsys.readouterr()
        # should have printed some sort of usage message. We don't
        # need to explicitly test the content of the message.
        assert 'usage' in out
        # should have used the program name from the argument
        # vector.
        assert 'progname' in out
        # should exit with zero return code.
        assert exc_info.value.code == 0

    @parametrize('versionarg', ['-V', '--version'])
    def test_version(self, versionarg, capsys):
        with raises(SystemExit) as exc_info:
            happygisco.main(['progname', versionarg])
        out, err = capsys.readouterr()
        # should print out version.
        assert err == '{0} {1}\n'.format(happygisco.metadata.project, happygisco.metadata.version)
        # should exit with zero return code.
        assert exc_info.value.code == 0
