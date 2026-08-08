import os
import sys


def get_startup_path() -> str | None:
    if len(sys.argv) > 1:
        candidate = sys.argv[1]
        if os.path.isfile(candidate) and candidate.lower().endswith(".pdf"):
            return candidate
    return None