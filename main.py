import os
import argparse
import config  # ini app
from version import __version__, __app_name__
from core.pipeline import LgdPipeline
from logger import logger
import sys
from logger import FatalError


def scan_lgd_files(target_dir: str) -> list:
    """
    scan all .lgd
    """
    lgd_files = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith('.lgd'):
                full_path = os.path.join(root, file)
                lgd_files.append(full_path)
    return lgd_files


def process_single_file(file_path: str, keep_files: bool) -> bool:
    """
    process single file
    :return True - successful
            or False - failed
    """
    try:
        pipeline = LgdPipeline(file_path)
        pipeline.run(keep_intermediate=keep_files)
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

    args = parser.parse_args()
    config.init_app_env()

    target_path = args.target_path
    keep_files = not args.clean
    stop_on_error = args.stop_on_error

    try:
        logger.set_stop_on_error(stop_on_error)

        if os.path.isfile(target_path):
            # single mode
            if not target_path.lower().endswith('.lgd'):
                logger.error_and_stop(f"[PROCESSING] The specified file '{target_path}' is not a .lgd file.")
                return

            logger.info(f"[PROCESSING] Starting Single File Mode: {target_path}")
            is_success = process_single_file(target_path, keep_files)
            if is_success:
                logger.info(f"[PROCESSING] Task Finished Successfully: {target_path}")
            else:
                logger.error(f"[PROCESSING] Task Failed: {target_path}")

        elif os.path.isdir(target_path):
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

                if process_single_file(file_path, keep_files):
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