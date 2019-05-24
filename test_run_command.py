from nose.tools import eq_, raises

from sysrsync import run_command
#####################################################################
## run_command, subprocess wrapper

def test_rsync_version():
    "run_command(): 'rsync --version' returncode=0"
    expect_returncode = 0
    cmd = ['rsync', '--version']
    result = run_command(cmd)

    eq_(result['returncode'], expect_returncode)


def test_rsync_invalid_option():
    "run_command(): 'rsync --invalid-option' returns 'CalledProcessError', returncode=1"
    expect_returncode = ("CalledProcessError", 1)
    cmd = ['rsync', '--invalid-option']
    result = run_command(cmd)

    eq_((result['result'], result['returncode']), expect_returncode)


def test_run_command_timeout():
    "run_command(): timeout returns 'TimeoutExpired'"
    cmd = ['sleep', 2]
    result = run_command(cmd, timeout=1)
    
    eq_(result['result'], "TimeoutExpired")


def test_run_command_unexpected_error():
    "run_command(): invalid command returns 'UnexpectedError'"
    cmd = ['cmd-does-exist']
    result = run_command(cmd)
    
    eq_(result['result'], "UnexpectedError")


