# sysrsync
Simple and safe subprocess rsync wrapper for Python 3

> - pjc fork is simple rollback to allow python 3.5 by removing f-string and squishing original nice project structure into a single file module
> - don't mean to imply any of these changes are an improvement, probably a degradation but add some convenience for my personal use
> - minor change to mutable and func call default args in some functions. this is a potential source of bugs in a lib or other setting where func may be called multiple times but the default arg is eval only once on import

## Requirements

* rsync
* python 3.5+ (original was python 3.6+)

**development**:

* pipenv (be sure to have both pipenv and pip upgraded to the latest version)

## Usage

* Basic file sync

```python
import sysrsync

sysrsync.run(source='/home/user/foo.txt',
             destination='/home/server/bar')
# runs 'rsync /home/users/foo.txt /home/server/files'
```

* ssh with options

```python
import sysrsync

sysrsync.run(source='/home/user/files',
             destination='/home/server/files',
             destination_ssh='myserver',
             options=['-a'])
# runs 'rsync -a /home/users/files/ myserver:/home/server/files'
```

* exclusions

```python
import sysrsync

sysrsync.run(source='/home/user/files',
             destination='/home/server/files',
             destination_ssh='myserver',
             options=['-a'],
             exclusions=['file_to_exclude', 'unwanted_file'])
# runs 'rsync -a /home/users/files/ myserver:/home/server/files --exclude file_to_exclude --exclude unwanted_file'
```

## API

`sysrsync.run`

| argument  | type | default | description |
| --------- | ---- | ------- | ----------- |
| cwd  | str  | `os.getcwd()` | working directory in which subprocess will run the rsync command |
| strict  | bool | `True` | raises `RsyncError` when rsync return code is different than 0  |
| verbose | bool | `False` | verbose mode: currently prints rsync command before executing |
| **kwargs | dict | Not Applicable | arguments that will be forwarded to call to `sysrsync.get_rsync_command` |

**returns**: `subprocess.CompletedProcess`

**raises**: `RsyncError` when `strict = True` and rsync return code is different than 0 ([Success](https://lxadm.com/Rsync_exit_codes#List_of_standard_rsync_exit_codes))

`sysrsync.get_rsync_command`

| argument  | type | default | description |
| --------- | ---- | ------- | ----------- |
| source | str | - | Source folder or file |
| destination | str | - | Destination folder |
| source_ssh | Optional[str] | None | Remote ssh client where source is located |
| destination_ssh | Optional[str] | None | Remote ssh client where destination is located |
| exclusions | Iterable[str] | [] | List of excluded patterns as in rsync's `--exclude` |
| sync_source_contents | bool | True | Abstracts the elusive trailing slash behaviour that `source` normally has when using rsync directly, i.e. when a trailing slash is present in `source`, the folder's content is synchronized with destination. When no trailing slash is present, the folder itself is synchronized with destination. |
| options | Iterable[str] | [] | List of options to be used right after rsync call, e.g. `['-a', '-v']` translates to `rsync -a -v` |

**returns**: `List[str]` -> the compiled list of commands to be used directly in `subprocess.run`

**raises**: `RemotesError` when both `source_ssh` and `target_ssh` are set. Normally linux rsync distribution disallows source and destination to be both remotes.
