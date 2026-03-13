"""
test/test_utils.py
helper function for all testers
"""

import os

def wait_and_cleanup(file_paths: list):
    """全自动静默清理，不再等待用户确认"""
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)
