
import argparse
from pathlib import Path
from . import config  # ini app
from .version import __version__, __app_name__
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from .logger import logger
import sys
from .logger import FatalError


def scan_lgd_files(target_dir: str) -> list:
    """
    scan all .lgd
    Uses pathlib for recursive globbing
    """
    target = Path(target_dir)
    result = []

    for p in target.rglob("*"):
        if p.is_file() and p.suffix.lower() == '.lgd':
            result.append(str(p))

    return result


def process_single_file(file_path: str, keep_files: bool, refine: bool = False) -> bool:
    """
    process single file
    :return True - successful
            or False - failed
    """
    try:
        pipeline = LgdPipeline(file_path)
        pipeline.run(keep_intermediate=keep_files, refine=refine)
        return True
    except Exception as e:
        logger.error_and_stop(f"[!] Critical Error processing '{file_path}': {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description=f"{__app_name__} Pipeline - V {__version__}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "target_path",
        help="Path to a single .lgd file OR a directory containing .lgd files."
    )

    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="Clean up intermediate files (.asm, .csv, .c) after compilation."
    )

    parser.add_argument(
        "--stop_on_error",
        action="store_true",
        help="Stop program execution immediately upon encountering an unresolvable error."
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print the full exception traceback when an error occurs."
    )

    parser.add_argument(
        "--refine",
        action="store_true",
        help="Apply LGC refinement (extern and constant symbol replacement) after decompilation."
    )

    args = parser.parse_args()
    config.init_app_env()

    target_path = args.target_path
    keep_files = not args.clean
    stop_on_error = args.stop_on_error
    refine = args.refine

    try:
        logger.set_stop_on_error(stop_on_error)
        
        target_p = Path(target_path)

        if target_p.is_file():
            # single mode
            if target_p.suffix.lower() != '.lgd':
                logger.error_and_stop(f"[PROCESSING] The specified file '{target_path}' is not a .lgd file.")
                return

            logger.info(f"[PROCESSING] Starting Single File Mode: {target_path}")
            is_success = process_single_file(target_path, keep_files, refine)
            if is_success:
                logger.info(f"[PROCESSING] Task Finished Successfully: {target_path}")
            else:
                logger.error(f"[PROCESSING] Task Failed: {target_path}")

        elif target_p.is_dir():
            # batch mode
            logger.info(f"[PROCESSING] Scanning directory for .lgd files: {target_path}")
            lgd_files = scan_lgd_files(target_path)

            if not lgd_files:
                logger.warning(f"[PROCESSING] No .lgd files found in '{target_path}' or its subdirectories.")
                return

            total_files = len(lgd_files)
            logger.info(f"[PROCESSING] Batch Mode Initialized. Found {total_files} .lgd files.")

            # print all files
            for idx, f in enumerate(lgd_files, start=1):
                logger.info(f"    {idx}. {f}")

            print("\n" + "=" * 50)

            # for processing track
            success_list = []
            failed_list = []

            for idx, file_path in enumerate(lgd_files, start=1):
                logger.info(f"\n[BATCH PROGRESS] Processing file {idx}/{total_files}: {file_path}")
                print("-" * 50)

                if process_single_file(file_path, keep_files, refine):
                    success_list.append(file_path)
                else:
                    failed_list.append(file_path)

            # summary
            print("\n" + "=" * 50)
            logger.info("[PROCESSING] BATCH PROCESSING REPORT")
            print("=" * 50)
            logger.info(f"    Total files scanned : {total_files}")
            logger.info(f"    Successfully parsed : {len(success_list)}")
            logger.info(f"    Failed to parse     : {len(failed_list)}")

            if failed_list:
                print("-" * 50)
                logger.warning("[PROCESSING] The following files FAILED to process:")
                for idx, failed_file in enumerate(failed_list, start=1):
                    logger.warning(f"    {idx}. {failed_file}")

            print("=" * 50 + "\n")

        else:
            logger.error_and_stop(f"[PROCESSING] Target path does not exist: {target_path}")

    except FatalError:
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
