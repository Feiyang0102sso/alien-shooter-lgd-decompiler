import argparse
from pathlib import Path
from . import config  # ini app
from .version import __version__, __app_name__
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from .logger import logger
import sys
from .logger import FatalError
from lgd_tool.lgd_decompiler.LGC_reorganizer import run_splitter_pipeline
from lgd_tool.lgd_decompiler.LGC_refiner.refiner import LgcRefiner
from lgd_tool.config import REFINER_DATA_DIR



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


def refine_reorganized_files(output_dir: Path) -> None:
    """
    递归遍历并获取指定输出目录下生成的全部小 LGC 文件，
    对它们分别应用 LgcRefiner 进行就地常量与 extern 符号精炼替换。

    :param output_dir: 重组分割落盘后的小文件工程目录 Path
    """

    logger.info("=== Post-Reorganize Phase: Refining Final Reorganized LGCs ===")
    refiner = LgcRefiner(REFINER_DATA_DIR)
    
    # 递归查找目录下所有的 .lgc 文件，平铺直叙
    lgc_files = []
    for p in output_dir.rglob("*.lgc"):
        if p.is_file():
            lgc_files.append(p)
            
    # 逐一执行就地精炼
    refine_count = 0
    for lgc_file in lgc_files:
        try:
            raw_code = lgc_file.read_text(encoding='utf-8')
            refined_code = refiner.refine(raw_code, file_name=lgc_file.name)
            lgc_file.write_text(refined_code, encoding='utf-8')
            refine_count = refine_count + 1
            logger.debug(f"[Refiner] Refined file successfully: {lgc_file.name}")

        except Exception as e:
            logger.error(f"[Refiner] Failed to refine file {lgc_file.name}: {e}")
            
    logger.info(f"[Refiner SUMMARY] Post-Reorganize refinement completed! Successfully refined {refine_count} LGC files.")


def cleanup_existing_lgc_files(target_dir: Path) -> bool:
    """
    delete all .lgc in directory to avoid problems
    a prompt will be shown to user

    :param target_dir: input path
    :return: True user confirm cleaning or no lgc need to be cleaned
             False user refuse to clean
    """
    # find all lgc
    lgc_files = []
    for p in target_dir.rglob("*.lgc"):
        if p.is_file():
            lgc_files.append(p)

    # if no lgc need to be cleaned
    if not lgc_files:
        return True

    # purple
    purple_start = "\033[1;35m"
    color_reset = "\033[0m"

    print("\n" + purple_start + "!" * 80)
    print("[WARNING] This program will clean up all existing .lgc files in the target folder to avoid conflicts.")
    print(f"Target Directory: {target_dir}")
    print(f"Found {len(lgc_files)} existing .lgc files that will be deleted.")
    print("!" * 80 + color_reset)

    try:
        prompt_text = purple_start + "Are you sure you want to delete these files and continue? (y/n): " + color_reset
        user_input = input(prompt_text)
    except (KeyboardInterrupt, EOFError):
        print("\n" + purple_start + "[ABORT] Operation cancelled." + color_reset)
        return False

    # y / yes
    user_input_clean = user_input.strip().lower()
    if user_input_clean != "y" and user_input_clean != "yes":
        print(purple_start + "[ABORT] Operation cancelled by user." + color_reset)
        return False

    # delete
    deleted_count = 0
    for file_path in lgc_files:
        try:
            file_path.unlink()
            deleted_count = deleted_count + 1
        except Exception as e:
            logger.warning(f"[CLEANUP] Failed to delete file {file_path.name}: {e}")

    logger.info(f"[CLEANUP] Cleaned up {deleted_count} existing .lgc files successfully to prevent decompilation conflicts.")
    return True


def process_crypt_file(file_path: Path, decrypt: bool, encrypt: bool) -> bool:
    """
    处理单个 LGD 文件的加密或解密转换。

    :param file_path: 输入文件的 Path 对象
    :param decrypt: 是否执行解密
    :param encrypt: 是否执行加密
    :return: 转换成功返回 True，失败返回 False
    """
    try:
        from lgd_tool.crypt import LgdCryptor
        cryptor = LgdCryptor()

        # 确定输出路径，保持一致的路径转换规则
        if decrypt:
            if file_path.suffix.lower() == '.lgd':
                output_path = file_path.with_suffix(file_path.suffix + '.bak')
            else:
                output_path = file_path.with_name(file_path.name + '.bak')
            action_name = "Decrypt"
        else:
            if file_path.suffix.lower() == '.bak':
                output_path = file_path.with_suffix('')
            else:
                output_path = file_path
            action_name = "Encrypt"

        logger.info(f"[CRYPT] {action_name}ing file: {file_path.name} -> {output_path.name}")

        data = file_path.read_bytes()
        transformed = cryptor.transform(data)
        output_path.write_bytes(transformed)

        logger.info(f"[CRYPT] {action_name} success! Saved to {output_path.name}")
        return True
    except Exception as e:
        logger.error(f"[CRYPT] Failed to process file {file_path.name}: {e}")
        return False


def process_crypt_dir(dir_path: Path, decrypt: bool, encrypt: bool) -> None:
    """
    递归批量处理目录下的所有加密/解密文件。

    :param dir_path: 输入目录的 Path 对象
    :param decrypt: 是否执行解密
    :param encrypt: 是否执行加密
    """
    files_to_process = []

    if decrypt:
        for p in dir_path.rglob("*"):
            if p.is_file() and p.suffix.lower() == '.lgd':
                files_to_process.append(p)
        action_name = "Decryption"
    else:
        for p in dir_path.rglob("*"):
            if p.is_file() and p.suffix.lower() == '.bak':
                files_to_process.append(p)
        action_name = "Encryption"

    if not files_to_process:
        logger.warning(f"[CRYPT] No files found for {action_name} in '{dir_path}'")
        return

    total = len(files_to_process)
    logger.info(f"[CRYPT] Found {total} files to process. Starting batch {action_name}...")

    success_count = 0
    failed_list = []

    for idx, file_path in enumerate(files_to_process, start=1):
        logger.info(f"[CRYPT PROGRESS] Processing file {idx}/{total}: {file_path.name}")
        if process_crypt_file(file_path, decrypt=decrypt, encrypt=encrypt):
            success_count = success_count + 1
        else:
            failed_list.append(file_path)

    print("\n" + "=" * 50)
    logger.info(f"[CRYPT SUMMARY] BATCH {action_name.upper()} REPORT")
    print("=" * 50)
    logger.info(f"    Total files found  : {total}")
    logger.info(f"    Successfully done  : {success_count}")
    logger.info(f"    Failed             : {len(failed_list)}")
    if failed_list:
        print("-" * 50)
        logger.warning("[CRYPT] The following files failed:")
        for idx, f in enumerate(failed_list, start=1):
            logger.warning(f"    {idx}. {f.name}")
    print("=" * 50 + "\n")


def run_crypt_workflow(target_path: str, decrypt: bool, encrypt: bool) -> None:
    """
    运行加密解密工作流，分流处理单文件与目录路径。

    :param target_path: 输入路径字符串
    :param decrypt: 是否执行解密
    :param encrypt: 是否执行加密
    """
    target_p = Path(target_path)
    if not target_p.exists():
        logger.error_and_stop(f"[CRYPT] Target path does not exist: {target_path}")
        return

    if target_p.is_file():
        process_crypt_file(target_p, decrypt=decrypt, encrypt=encrypt)
    elif target_p.is_dir():
        process_crypt_dir(target_p, decrypt=decrypt, encrypt=encrypt)
    else:
        logger.error_and_stop(f"[CRYPT] Invalid target path: {target_path}")


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
        help="Apply LGC refinement (extern and constant symbol replacement) after decompilation and reorganize."
    )

    parser.add_argument(
        "--reorganize",
        action="store_true",
        help="Split LGC into multiple core/segment files and merge identical segments."
    )

    parser.add_argument(
        "-d", "--decrypt",
        action="store_true",
        help="Decrypt .lgd file(s) to .lgd.bak"
    )

    parser.add_argument(
        "-e", "--encrypt",
        action="store_true",
        help="Encrypt decrypted .lgd.bak file(s) back to .lgd"
    )

    args = parser.parse_args()

    config.init_app_env()

    target_path = args.target_path
    keep_files = not args.clean
    stop_on_error = args.stop_on_error
    refine = args.refine
    splitter = args.reorganize
    decrypt = args.decrypt
    encrypt = args.encrypt

    # 校验参数：refine 必须在 reorganize 开启时才能使用
    if refine and not splitter:
        logger.error_and_stop("[CONFIG] --refine option can only be used when --reorganize is enabled.")
        return

    # 校验加密解密参数
    if decrypt and encrypt:
        logger.error_and_stop("[CONFIG] Cannot specify both --decrypt and --encrypt.")
        return

    # 若指定了加密或解密，则执行专有逻辑，不走原反编译 pipeline
    if decrypt or encrypt:
        try:
            logger.set_stop_on_error(stop_on_error)
            run_crypt_workflow(target_path, decrypt=decrypt, encrypt=encrypt)
        except FatalError:
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        return

    try:
        logger.set_stop_on_error(stop_on_error)
        
        target_p = Path(target_path)

        # 确定要清理的目标根文件夹
        if target_p.is_dir():
            clean_root = target_p
        elif target_p.is_file():
            clean_root = target_p.parent
        else:
            logger.error_and_stop(f"[PROCESSING] Target path does not exist: {target_path}")
            return

        # 敏感操作：执行前置冲突 LGC 清理，如用户取消则优雅中止
        if not cleanup_existing_lgc_files(clean_root):
            sys.exit(0)

        if target_p.is_file():
            # single mode
            if target_p.suffix.lower() != '.lgd':
                logger.error_and_stop(f"[PROCESSING] The specified file '{target_path}' is not a .lgd file.")
                return

            logger.info(f"[PROCESSING] Starting Single File Mode: {target_path}")
            # 运行顺序调整：反编译大 LGC 时暂不精炼，在切分重组后再统一对所有小 LGC 进行精炼
            is_success = process_single_file(target_path, keep_files, refine=False)
            if is_success:
                logger.info(f"[PROCESSING] Task Finished Successfully: {target_path}")
                
                # 若启用 --splitter 选项，自动执行单大文件切分写盘
                if splitter:
                    run_splitter_pipeline(target_p)
                    
                    # refine 运行顺序在 reorganize 之后
                    if refine:
                        output_dir = target_p.parent / target_p.stem
                        refine_reorganized_files(output_dir)
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

                # 运行顺序调整：反编译大 LGC 时暂不精炼，在合并重组后再统一对所有小 LGC 进行精炼
                if process_single_file(file_path, keep_files, refine=False):
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

            if splitter and success_list:
                run_splitter_pipeline(target_p, success_list=success_list)
                
                # refine 运行顺序在 reorganize 之后
                if refine:
                    refine_reorganized_files(target_p)


        else:
            logger.error_and_stop(f"[PROCESSING] Target path does not exist: {target_path}")

    except FatalError:
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
