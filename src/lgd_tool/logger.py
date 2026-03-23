"""
src/lgd_tool/logger.py
universal log config for the project
"""
import logging
import sys
from pathlib import Path

# === config area ===
# e.g.  [ERROR] [Lgd_Decompiler - ast_builder.py:38]
LOGGER_NAME = "Lgd_Decompiler"

class FatalError(BaseException):
    """
    BaseException > Exception
    Raised when an error occurs and stop_on_error is True.
    make sure the error is caught correct and stop pipeline immediately
    """
    pass

class ErrorLogger(logging.Logger):
    """
    inherit normal logger class
    an extended version of current Logger
    generally add stop on error in class
    """

    def __init__(self, name, level=logging.NOTSET):
        """
        initialize logger, NOTSET will handle it to its parent class
        """
        super().__init__(name, level)
        self.stop_on_error = False

    def set_stop_on_error(self, should_stop: bool):
        """
        whether to active stop on error
        """
        self.stop_on_error = should_stop

    def error_and_stop(self, msg: str, *args, **kwargs):
        """
        Log an error, and if stop_on_error is True, raise FatalError to stop pipeline.
        """
        if sys.version_info >= (3, 8):
            # return the error message with its exact file, instead of logger.py
            # not 3 because it will over piercing
            kwargs.setdefault("stacklevel", 2)
        self.error(msg, *args, **kwargs)
        if self.stop_on_error:
            raise FatalError(msg)

# use ErrorLogger instead of Logger
logging.setLoggerClass(ErrorLogger)

class ColoredFormatter(logging.Formatter):
    """
    provide different colors based on log levels.
    """
    # ANSI Color Codes
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red Background
    }
    RESET = "\033[0m"

    def format(self, record):
        # Pick color based on level
        color = self.COLORS.get(record.levelno, "")

        # Build precision timestamp
        log_fmt = f"{color}[%(asctime)s.%(msecs)03d] [%(levelname)s]"

        # Add source info (filename and line) only for ERROR and above
        if record.levelno >= logging.ERROR:
            log_fmt += " [%(name)s - %(filename)s:%(lineno)d]"

        log_fmt += f" %(message)s{self.RESET}"

        # Create a temporary formatter with the defined date format
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logger() -> ErrorLogger:
    """
    Initializes a logger with console handlers for both stdout and stderr.
    """
    # Cast to ErrorLogger so the IDE knows the actual return type
    import typing
    _logger = typing.cast(ErrorLogger, logging.getLogger(LOGGER_NAME))
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False

    if not _logger.handlers:
        # Standard Output, Handler for regular logs (DEBUG, INFO, WARNING)
        stdout_h = logging.StreamHandler(sys.stdout)
        stdout_h.setLevel(logging.DEBUG)
        stdout_h.addFilter(lambda r: r.levelno < logging.ERROR)
        stdout_h.setFormatter(ColoredFormatter())

        # Standard Error, Handler for error logs (ERROR, CRITICAL)
        stderr_h = logging.StreamHandler(sys.stderr)
        stderr_h.setLevel(logging.ERROR)
        stderr_h.setFormatter(ColoredFormatter())

        _logger.addHandler(stdout_h)
        _logger.addHandler(stderr_h)

    return _logger


# Global logger instance for other modules
logger: ErrorLogger = setup_logger()


def add_file_handler(log_path: Path):
    """
    Adds a file handler. If one exists, removes it first to avoid duplicates or
    writing to the wrong location after a path update.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get the global logger
    _logger = logging.getLogger(LOGGER_NAME)

    # 1. Remove existing FileHandlers to avoid duplication or path conflicts
    for h in _logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            h.close()
            _logger.removeHandler(h)

    # 2. Add the new handler
    file_h = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_h.setLevel(logging.DEBUG)
    # no need color format gor .log
    file_fmt = logging.Formatter(
        '[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_h.setFormatter(file_fmt)
    _logger.addHandler(file_h)