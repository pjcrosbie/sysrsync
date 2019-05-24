# sysrsync.py

import os
import sys
import pipes
import subprocess
import collections

from functools import reduce
from operator import iconcat

from typing import Any, Iterable, List, Tuple, Optional

import pprint as pprint_lib 
pprint = pprint_lib.PrettyPrinter(indent=1).pprint 

__version__ = '0.2.0-alpha'



def run(cwd=None, strict=True, verbose=False, timeout=60*3, **kwargs):
    rsync_command = get_rsync_command(**kwargs)
    rsync_string = ' '.join(rsync_command)

    if cwd is None:
        cwd = os.getcwd()

    if verbose is True:
        print('[sysrsync runner] running command (timeout={} secs):'.format())
        print(rsync_string)

    subprocess_result = run_command.run(rsync_command, cwd=cwd, timeout=timeout)

    if strict is True:
        code = subprocess_result["returncode"]
        _check_return_code(code, rsync_string, subprocess_result)

    return subprocess_result


def _check_return_code(return_code: int, action: str, subprocess_result: dict):
    if return_code != 0:
        pprint(subprocess_result)
        msg = "[sysrsync runner] {action} exited with code {return_code}".format(action=action, return_code=return_code)
        raise RsyncError(msg)



#####################################################################
## command_maker

def get_rsync_command(source: str,
                      destination: str,
                      source_ssh: Optional[str] = None,
                      destination_ssh: Optional[str] = None,
                      exclusions: Iterable[str] = None,
                      sync_source_contents: bool = True,
                      options: Iterable[str] = None) -> List[str]:
    if (source_ssh is not None and destination_ssh is not None):
        raise RemotesError()

    if exclusions is None:
        exclusions = []
    if options is None:
        options = []

    source = get_directory_with_ssh(source, source_ssh)
    destination = get_directory_with_ssh(destination, destination_ssh)

    if is_path_to_file(source, (source_ssh is not None)):
        sync_source_contents = False

    source, destination = sanitize_trailing_slash(
        source, destination, sync_source_contents)

    exclusions = get_exclusions(exclusions)

    return ['rsync',
            *options,
            source,
            destination,
            *exclusions]


def get_exclusions(exclusions: Iterable[str]) -> Iterable[str]:
    return flatten((('--exclude', exclusion) for exclusion in exclusions if exclusion != '--exclude'))


#####################################################################
## exceptions

class RemotesError(Exception):
    def __init__(self):
        message = 'source and destination cannot both be remote'
        super().__init__(message)


class RsyncError(Exception):
    pass


#####################################################################
## helpers: directory


def get_directory_with_ssh(directory: str, ssh: Optional[str]) -> str:
    if ssh is None:
        return directory

    return '{ssh}:{directory}'.format(ssh=ssh, directory=directory)


def sanitize_trailing_slash(source_dir: str, target_dir: str, sync_sourcedir_contents: bool = True) -> Tuple[str, str]:
    target_dir = strip_trailing_slash(target_dir)

    if sync_sourcedir_contents is True:
        source_dir = add_trailing_slash(source_dir)
    else:
        source_dir = strip_trailing_slash(source_dir)

    return source_dir, target_dir


def strip_trailing_slash(directory: str) -> str:
    return (directory[:-1]
            if directory.endswith('/')
            else directory)


def add_trailing_slash(directory: str) -> str:
    return (directory
            if directory.endswith('/')
            else '{directory}/'.format(directory=directory))


#####################################################################
## helpers: files


def is_path_to_file(path, is_remote) -> bool:
    if is_remote is True:
        return exists_remote(path)

    return os.path.isfile(path)


def exists_remote(host_with_path):
    "Test if a file exists at path on a host accessible with SSH."
    host, path = host_with_path.split(':', 1)
    return subprocess.call(['ssh', host, 'test -f {}'.format(pipes.quote(path))]) == 0


#####################################################################
## helpers: iterators


def flatten(input_iter: Iterable[Any]) -> List[Any]:
    list_of_lists = (element if isinstance(element, collections.Iterable)
                     else [element]
                     for element in input_iter)

    return reduce(iconcat, list_of_lists, [])


#####################################################################
## subprocess.run() wrapper with nice return and timeout option

def run_command(command_list, timeout=3, cwd=None):
    '''
    wrapper on subprocess.run()
    returns results in dict along with many diagnostics for failure cases
    '''
    assert isinstance(command_list, list)

    # explicit conversion of num to str
    command_list = [str(elem) for elem in command_list]

    try:
        completed_process = subprocess.run(
            command_list, 
            check=True,             # exception on non-zero error code
            timeout=timeout,        # exception on timeout secs
            # capture both stderr and stdout
            # decode() byte strings to normal utf strings, not necessary
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd
            )
    except subprocess.CalledProcessError as error:
        result = {
            "result"     : "CalledProcessError",
            "cmd"        : error.cmd,
            "returncode" : error.returncode,
            "stdout"     : error.stdout,
            "stderr"     : error.stderr
        }
    except subprocess.TimeoutExpired as error:
        result = {
            "result"      : "TimeoutExpired",
            "cmd"         : error.cmd,
            "timeout"     : error.timeout,
            "stdout"      : error.stdout,
            "stderr"      : error.stderr,
            "returncode"  : 1,
        }
    except:
        err_type, err_value, traceback = sys.exc_info()
        result = {
            "result"            : "UnexpectedError",
            "type"              : err_type,
            "value"             : err_value,
            "traceback"         : traceback,
            "returncode"        : 1,
        }
        # HACK: for testing, uncomment this to get crash here
        # raise    
    else:
        # all okay
        result = {
            "result"      : "OK",
            "cmd"         : completed_process.args,
            "stdout"      : completed_process.stdout,
            "stderr"      : completed_process.stderr,
            "returncode"  : completed_process.returncode
        }
         
    # these function inputs
    # note, 
    #   cmd is a return item from subprocess.run()
    #   cmd_list is what we pass to subprocess.run()
    #   cmd_line should be cut and pasteable but 
    #      not always, watch quoting args with spaces
    command_line = ' '.join([str(elem) for elem in command_list])
    result["inputs"] = {
        "cmd_list" : command_list,
        "cmd_line" : command_line,
        "cwd"      : cwd,
        "timeout"  : timeout,
    }

    return result