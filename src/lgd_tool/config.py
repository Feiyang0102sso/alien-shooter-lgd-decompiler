"""
/config.py
universal config for the exe and relevant paths
"""
import sys
from pathlib import Path
from .logger import logger, add_file_handler, LOGGER_NAME


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
        main_file = Path(__main__.__file__)
        # Fix: PIP-installed entry wrappers act like `.exe/__main__.py`.
        # Check if the parent is an actual directory to prevent FileExistsError!
        if main_file.parent.is_dir():
            return main_file.parent.resolve()

    # Default fallback to current working directory when running globally via shim
    return Path.cwd().resolve()


def get_resource_root() -> Path:
    """
        获取资源文件的根目录 (Resource Root)。

        兼容 PyInstaller 打包后的运行环境：
        - 单 exe 运行时，内置的静态资源
          自动解压到一个临时目录 ( sys._MEIPASS), 此时获取这个路径
        - Python 源码环境下直接运行时，sys._MEIPASS 不存在，
          回退并返回当前项目的实际根目录。

        Returns:
            Path: 静态资源所在的根目录绝对路径。
        """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass).resolve()
    return get_app_root()


def resolve_refiner_data_dir() -> Path:
    """
        解析并定位反编译器优化模块 (Decompiler Refiner) 的数据文件目录。

        为了实现“既支持内置默认数据，又允许外部数据覆盖（热更新）”的需求，
        该方法实现了一个按优先级的路径查找机制 (Fallback)：

        优先级顺序：
        1. 外部目录 (external_dir)：位于生成的 .exe 文件同级的 `data/decompiler_refiner`。
           （优先级最高，允许用户通过放置外部文件来覆盖程序自带的内置数据）
        2. 内置目录 (bundled_dir)：位于源码工程中，或被打包进 .exe 临时解压目录下的路径。
           （作为程序的保底基础数据，确保开箱即用）
        3. 内部目录 (internal_dir)：兼容 PyInstaller 单目录 (--onedir) 打包模式的路径。

        如果所有路径都不存在，默认返回外部目录路径

        Returns:
            Path: 最终确定的 refiner 数据库目录的绝对路径。
        """
    external_dir = ROOT_DIR / 'data' / 'decompiler_refiner'
    bundled_dir = RESOURCE_ROOT / 'data' / 'decompiler_refiner'
    internal_dir = ROOT_DIR / '_internal' / 'data' / 'decompiler_refiner'

    if external_dir.exists():
        return external_dir
    if bundled_dir.exists():
        return bundled_dir
    if internal_dir.exists():
        return internal_dir
    return external_dir

# --- Absolute Path Configuration ---
ROOT_DIR = get_app_root()
RESOURCE_ROOT = get_resource_root()
LOG_FILE_NAME = "LgdDecompiler.log"

# Refiner 数据目录（存放 extern_database.json 和 constants_database.json）
REFINER_DATA_DIR = resolve_refiner_data_dir()

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
    logger.debug(f"Root Path: {ROOT_DIR}")
    logger.debug(f"Log File Path: {log_file_path}")

def init_app_env():
    """
    Initial bootstrap with default paths.
    """
    update_paths() # Reuses the logic to setup folders and logging

# --- Initialize on Import ---
# to avoid problem, no longer used
# init_app_env()
