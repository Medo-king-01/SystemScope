import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000

def run_silent(cmd, **kwargs):
    kwargs.setdefault('creationflags', CREATE_NO_WINDOW)
    return subprocess.run(cmd, shell=True, **kwargs)