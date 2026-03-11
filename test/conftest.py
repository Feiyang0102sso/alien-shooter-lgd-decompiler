"""
test/conftest.py
将项目根目录加入 sys.path，使所有测试文件可以直接 import 项目模块。
"""
import sys
import os

# 项目根目录 = test/ 的上一级
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
