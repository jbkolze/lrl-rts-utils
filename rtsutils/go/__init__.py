"""Go package allowing initialization for python to know where
and which Go exe to use.
"""

import json
import subprocess
import os
import platform
import sys
import re

from rtsutils import null


_PLATFORM_SYS = platform.system().lower()
if not _PLATFORM_SYS:
    print("Platform not recognized")
    print("Program exiting")
    sys.exit(1)

_BINDING = "cavi"


# assuming Jython is running on windows
if platform.python_implementation() == "Jython":
    _PLATFORM_SYS = "windows"
    _BINDING += ".exe"

CAVI_GO = "{}/{}/{}".format(os.path.dirname(__file__), _PLATFORM_SYS, _BINDING)


def get(go_flags=None, out_err=True, is_shell=False, realtime=False, publish=None):
    """Method to initiate the Go binding as a subprocess

    Parameters
    ----------
    go_flags : dict
        dictionary defining Go binding flag requirements
    sh : bool, optional
        execute through a shell, by default True

    Returns
    -------
    tuple[bytes, bytes]
        returns a tuple (stdout, stderr)
    """
    subprocess_popen = subprocess.Popen(
        CAVI_GO,
        shell=is_shell,
        bufsize=1,
        cwd=os.path.dirname(__file__),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if out_err:
        if realtime:
            stderr = b''
            subprocess_popen.stdin.write(json.dumps(go_flags))
            subprocess_popen.stdin.flush()
            subprocess_popen.stdin.close()
            for line in subprocess_popen.stderr:
                if publish:
                    __parse_go_output(line.strip().decode(), publish)
                else:
                    print(line.strip().decode())
                stderr += line
            return subprocess_popen.stdout.read(), stderr
        std_in_out = subprocess_popen.communicate(input=json.dumps(go_flags))
        return std_in_out

    return subprocess_popen


def __parse_go_output(go_str, publish):
    """Updates GUI appropriately based on Go subroutine output.

    Parameters
    ----------
    go_str : str
        The decoded str produced by the Go subroutine.
    publish : callable
        A callback function that takes a single string (for log messages) or a
        single integer (for progress bar updates) as an argument.  Passes
        updates to an external GUI.
    """
    if 'Progress:' in go_str:
        prog_re = re.compile(r'\w*Progress: (?P<progress>\d+)\w*').search(go_str)
        publish(int(prog_re.group('progress')))
    if 'Status: INITIATED' in go_str:
        return
    publish(go_str)
