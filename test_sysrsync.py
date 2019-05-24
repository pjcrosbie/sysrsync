# test_sysrsync.py

#####################################################################
## test/directories_helper

# cheat on import renaming sysrsync one-file to directories for test
import sysrsync as directories
from nose.tools import eq_


def test_strip_trailing_slash():
    "test strip trailing slash"
    test_dir = '/a/'
    expect = '/a'
    result = directories.strip_trailing_slash(test_dir)

    eq_(expect, result)


def test_skip_strip_trailing_slash():
    "test skip strip trailing slash when not necessary"
    test_dir = '/a'
    result = directories.strip_trailing_slash(test_dir)

    eq_(result, test_dir)


def test_add_trailing_slash():
    "test add trailing slash"
    test_dir = '/a'
    expect = '/a/'
    result = directories.add_trailing_slash(test_dir)

    eq_(expect, result)


def test_skip_add_trailing_slash():
    "test skip add trailing slash when not necessary"
    test_dir = '/a/'
    result = directories.add_trailing_slash(test_dir)

    eq_(result, test_dir)


def test_sanitize_trailing_slash():
    "test sanitize trailing slash when syncing source contents"
    source, target = '/a', '/b/'
    expect_source, expect_target = '/a/', '/b'
    result_source, result_target = directories.sanitize_trailing_slash(
        source, target)

    eq_(expect_source, result_source)
    eq_(expect_target, result_target)


def test_sanitize_trailing_slash_no_action_needed():
    "test sanitize trailing slash when syncing source contents when already sanitized"
    source, target = '/a/', '/b'
    expect_source, expect_target = '/a/', '/b'
    result_source, result_target = directories.sanitize_trailing_slash(
        source, target)

    eq_(expect_source, result_source)
    eq_(expect_target, result_target)


def test_sanitize_trailing_slash_whole_source():
    "test sanitize trailing slash when syncing whole source"
    source, target = '/a/', '/b/'
    expect_source, expect_target = '/a', '/b'
    result_source, result_target = directories.sanitize_trailing_slash(
        source, target, sync_sourcedir_contents=False)

    eq_(expect_source, result_source)
    eq_(expect_target, result_target)


def test_sanitize_trailing_slash_whole_source_no_action_needed():
    "test sanitize trailing slash when syncing whole source when already sanitized"
    source, target = '/a', '/b/'
    expect_source, expect_target = '/a', '/b'
    result_source, result_target = directories.sanitize_trailing_slash(
        source, target, sync_sourcedir_contents=False)

    eq_(expect_source, result_source)
    eq_(expect_target, result_target)


def test_dir_with_ssh():
    "should compose string with ssh for rsync connection"
    directory = '/a'
    ssh = 'host'
    expect = 'host:/a'
    result = directories.get_directory_with_ssh(directory, ssh)

    eq_(result, expect)


def test_dir_without_ssh():
    "should return directory when ssh is None"
    directory = '/a'
    ssh = None
    result = directories.get_directory_with_ssh(directory, ssh)

    eq_(result, directory)


#####################################################################
## test/iterators_helper

# cheat on import renaming sysrsync one-file to directories for test
# from sysrsync.helpers import iterators
import sysrsync as iterators
from nose.tools import eq_


def test_list_flatten():
    list_input = [1, [2, 3], [4]]
    expect = [1, 2, 3, 4]
    result = iterators.flatten(list_input)

    eq_(expect, result)


def test_tuple_flatten():
    tuple_input = (1, [2, 3], [4])
    expect = [1, 2, 3, 4]
    result = iterators.flatten(tuple_input)

    eq_(expect, result)


def test_tuples_and_lists_list_flatten():
    tuple_input = (1, (2, 3), [4])
    expect = [1, 2, 3, 4]
    result = iterators.flatten(tuple_input)

    eq_(expect, result)

#####################################################################
## tests/sysrsync

# from sysrsync.command_maker import get_exclusions, get_rsync_command
from sysrsync import get_exclusions, get_rsync_command
from sysrsync import RemotesError
from nose.tools import eq_, raises


def test_get_exclusions():
    "should map list of exclusions to a list with each element following a --exclude statement"
    exclusions = ['a', 'b']
    expect = ['--exclude', 'a', '--exclude', 'b']
    result = get_exclusions(exclusions)

    eq_(expect, result)


def test_get_exclusions_already_in_rsync_format():
    "should ignore --exclude in exclusions"
    exclusions = ['--exclude', 'a', '--exclude', 'b']
    expect = ['--exclude', 'a', '--exclude', 'b']
    result = get_exclusions(exclusions)

    eq_(expect, result)


def test_simple_rsync_command():
    source = '/a'
    target = '/b'
    expect = 'rsync /a/ /b'.split()
    result = get_rsync_command(source, target)

    eq_(expect, result)


def test_rsync_options():
    source = '/a'
    target = '/b'
    options = ['-a', '--verbose']
    expect = 'rsync -a --verbose /a/ /b'.split()
    result = get_rsync_command(source, target, options=options)

    eq_(expect, result)


def test_simple_rsync_command_content_false():
    source = '/a'
    target = '/b'
    expect = 'rsync /a /b'.split()
    result = get_rsync_command(source, target, sync_source_contents=False)

    eq_(expect, result)


def test_rsync_exclusions():
    source = '/a'
    target = '/b'
    exclusions = ['file1', 'file2']
    expect = 'rsync /a/ /b --exclude file1 --exclude file2'.split()
    result = get_rsync_command(source, target, exclusions=exclusions)

    eq_(expect, result)


def test_rsync_exclusions_source_ssh():
    source = '/a'
    source_ssh = 'host1'
    target = '/b'
    exclusions = ['file1', 'file2']
    expect = 'rsync host1:/a/ /b --exclude file1 --exclude file2'.split()
    result = get_rsync_command(source, target, exclusions=exclusions, source_ssh=source_ssh)

    eq_(expect, result)


def test_rsync_exclusions_target_ssh():
    source = '/a'
    target_ssh = 'host1'
    target = '/b'
    exclusions = ['file1', 'file2']
    expect = 'rsync /a/ host1:/b --exclude file1 --exclude file2'.split()
    result = get_rsync_command(source, target, exclusions=exclusions, destination_ssh=target_ssh)

    eq_(expect, result)


@raises(RemotesError)
def test_rsync_throws_both_remotes():
    "raises RemotesError when both source and destination are remotes"
    source_ssh = 'host1'
    source = '/a'
    target_ssh = 'host2'
    target = '/b'
    get_rsync_command(source, target, source_ssh=source_ssh, destination_ssh=target_ssh)


