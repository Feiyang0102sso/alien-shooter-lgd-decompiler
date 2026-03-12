"""
test/conftest.py
Add the project root
to sys.path so that all test files can
directly import project modules.

!!! no longer used, now use pyproject.toml
"""

# import sys
# import os
#
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# print("PROJECT_ROOT: ", PROJECT_ROOT)
# # sys.path.append(PROJECT_ROOT)
#
# if PROJECT_ROOT not in sys.path:
#     print("Not found, inserting to sys.path... ")
#     sys.path.insert(0, PROJECT_ROOT)
