"""
Optional pytest launcher for local development.

Prefer plain pytest with flags (suite paths live in tests/conftest.py):

  pytest
  pytest --unit
  pytest --regression

Or run this module from the repo root:

  python -m tests.pytest_cli
  python -m tests.pytest_cli unit
  python -m tests.pytest_cli regression
"""

import sys

import pytest

# Keep in sync with [tool.pytest.ini_options] addopts in pyproject.toml
_DEFAULT_ADDOPTS = ["-v", "--tb=short", "--show-capture=no"]


def _run(extra_args: list[str]) -> None:
    """Invoke pytest and exit with the same status code."""
    argv = []
    argv.extend(_DEFAULT_ADDOPTS)
    argv.extend(extra_args)
    exit_code = pytest.main(argv)
    raise SystemExit(exit_code)


def run_all() -> None:
    """Run the full test suite under ``tests/``."""
    _run([])


def run_unit() -> None:
    """Run unit suite (same as ``pytest --unit``)."""
    _run(["--unit"])


def run_regression() -> None:
    """Run regression suite (same as ``pytest --regression``)."""
    _run(["--regression"])


def main() -> None:
    """CLI: all (default) | unit | regression."""
    if len(sys.argv) > 1:
        command = sys.argv[1].strip().lower()
    else:
        command = "all"

    if command == "all":
        run_all()
    elif command == "unit":
        run_unit()
    elif command == "regression":
        run_regression()
    else:
        msg = "Usage: python -m tests.pytest_cli [all|unit|regression]"
        print(msg, file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
