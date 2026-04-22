"""
tests/utils/cleanup.py
remove all products after testing
"""

from pathlib import Path


def wait_and_cleanup(file_paths: list):
    """removing silently"""
    for path in file_paths:
        p = Path(path)
        if p.exists():
            p.unlink()
