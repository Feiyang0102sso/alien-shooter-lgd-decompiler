"""
/config.py
universal config for the exe and relevant paths
"""
import sys
from pathlib import Path
from logger import logger, add_file_handler, LOGGER_NAME


def get_app_root() -> Path:
    """
    Identify the application root directory.
    Improved to handle subfolder execution.
    """
    if getattr(sys, 'frozen', False):
        # If running as a bundled EXE
        return Path(sys.executable).parent.resolve()

    # If running as a script, we use the directory of the main script being run
    # This ensures config.ini is found even if converter.py is in a subfolder
    import __main__
    if hasattr(__main__, "__file__"):
        return Path(__main__.__file__).parent.resolve()

    return Path(__file__).parent.resolve()

# --- Absolute Path Configuration ---
ROOT_DIR = get_app_root()
LOG_FILE_NAME = "LgdDecompiler.log"

input_dir = ROOT_DIR / 'DATAS' # not used in this project
output_dir = ROOT_DIR / 'OUTPUT' # not used in this project
log_file_path = ROOT_DIR / "LgdDecompiler.log"

# --- Directory Helper Methods ---

def get_input_dir() -> Path:
    """
    Verify and return the source assets directory.
    """
    if not input_dir.exists():
        logger.warning(f"Assets directory not found at: {input_dir}")
    return input_dir

def get_output_dir(create_if_missing: bool = True) -> Path:
    """
    Return the output directory, creating it if required.
    """
    if create_if_missing:
        output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

# intend to accept user input dirs
def update_paths(new_input: str = None, new_output: str = None):
    """
    Update global paths and re-initialize the log file.
    """
    global input_dir, output_dir, log_file_path

    if new_input:
        input_dir = Path(new_input).resolve()
    if new_output:
        output_dir = Path(new_output).resolve()

    log_file_path = ROOT_DIR / LOG_FILE_NAME

    # Ensure output dir exists before adding file handler
    # output_dir.mkdir(parents=True, exist_ok=True)
    add_file_handler(log_file_path)

    # logger.debug(f"Paths updated - Input: {input_dir}, Output: {output_dir}")

def init_app_env():
    """
    Initial bootstrap with default paths.
    """
    update_paths() # Reuses the logic to setup folders and logging

# --- Initialize on Import ---
# to avoid problem, no longer used
# init_app_env()