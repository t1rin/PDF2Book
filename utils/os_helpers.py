import os
import sys
import platform
import subprocess


def os_type():
    return platform.system()

def get_startup_path() -> str | None:
    if len(sys.argv) > 1:
        candidate = sys.argv[1]
        if os.path.isfile(candidate) and candidate.lower().endswith(".pdf"):
            return candidate
    return None

def start_path(path):
    if os_type() == "Windows":
        subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
        return True
        
    elif os_type() == "Darwin":
        subprocess.Popen(['open', '-R', path])
        return True
        
    else:
        folder = os.path.dirname(path)
        if folder:
            subprocess.Popen(['xdg-open', folder])
            return True