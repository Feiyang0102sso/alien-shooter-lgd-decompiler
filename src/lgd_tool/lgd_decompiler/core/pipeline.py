"""
core/pipeline.py
"""

import sys
import threading
from pathlib import Path

from lgd_tool.lgd_decompiler.generate_LGC.lgc_generator import LgcGenerator
from lgd_tool.lgd_decompiler.generate_intermediate.renderer_asm import LgdAsmRenderer
from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.core.context import LgdAnalysisContext
from lgd_tool.lgd_decompiler.core.parsers import P1LiteralParser, P2SymbolParser, FixedTableParser, BytecodeParser
from lgd_tool.lgd_decompiler.core.analyzer import LgdAnalyzer
from lgd_tool.lgd_decompiler.generate_intermediate.renderer_c import HumanReadableCRenderer
from lgd_tool.lgd_decompiler.generate_intermediate.exporter_csv import LgdCsvExporter


class LgdPipeline:
    def __init__(self, file_path):
        self.file_path = file_path

    def run(self, is_debug: bool = False, keep_intermediate: bool = True, refine: bool = False):
        file_p = Path(self.file_path)
        if not file_p.exists():
            logger.error_and_stop(f"File not found: {self.file_path}")
            return

        # 1. Load File
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
        except Exception as e:
            logger.error_and_stop(f"Failed to read file: {e}")
            return

        # Initialize Context
        ctx = LgdAnalysisContext(
            file_path=self.file_path,
            file_size=len(data),
            raw_data=data
        )

        print("\n")
        logger.info("=== Phase 1: Parsing ===")

        # Parse P1
        ctx.p1_offset_start = 0
        p1_parser = P1LiteralParser(data)
        ctx.literal_table, next_off, ctx.is_old_version = p1_parser.parse(ctx.p1_offset_start)
        ctx.p1_offset_end = next_off

        # Log P1 Details
        logger.info(f"[Part 1 Literal] Count: {len(ctx.literal_table)}")
        logger.info(f"[Part 1 Literal] Offset Range: 0x{ctx.p1_offset_start:X} -> 0x{ctx.p1_offset_end:X}")

        if ctx.is_old_version:
            version_str = "OLD"
        else:
            version_str = "NEW"

        msg = "[Parser] Version check finished. Detected " + version_str + " version flags."
        logger.info(msg)

        # Parse P2
        ctx.p2_offset_start = next_off
        p2_parser = P2SymbolParser(data)
        ctx.symbol_table, next_off = p2_parser.parse(ctx.p2_offset_start)
        ctx.p2_offset_end = next_off

        # Log P2 Details
        logger.info(f"[Part 2 Symbol ] Count: {len(ctx.symbol_table)}")
        logger.info(f"[Part 2 Symbol ] Offset Range: 0x{ctx.p2_offset_start:X} -> 0x{ctx.p2_offset_end:X}")

        # ---  Action / ScriptEvent  table---
        ft_parser = FixedTableParser(data)

        # Action Table
        ctx.action_tbl_offset_start = next_off
        ctx.action_table, next_off = ft_parser.parse(ctx.action_tbl_offset_start, "Action")
        ctx.action_tbl_offset_end = next_off
        logger.info(f"[Action Table  ] Defined: {len(ctx.action_table)}")
        logger.info(
            f"[Action Table  ] Offset Range: 0x{ctx.action_tbl_offset_start:X} -> 0x{ctx.action_tbl_offset_end:X}")

        # ScriptEvent Table
        ctx.event_tbl_offset_start = next_off
        ctx.script_event_table, next_off = ft_parser.parse(ctx.event_tbl_offset_start, "ScriptEvent")
        ctx.event_tbl_offset_end = next_off
        logger.info(f"[Event Table   ] Defined: {len(ctx.script_event_table)}")
        logger.info(
            f"[Event Table   ] Offset Range: 0x{ctx.event_tbl_offset_start:X} -> 0x{ctx.event_tbl_offset_end:X}")

        # ctx.bytecode_offset_start = next_off
        # logger.info(f"[Bytecode      ] Start Offset: 0x{ctx.bytecode_offset_start:X}")

        print("\n")
        logger.info("=== Phase 2: Analysis ===")
        analyzer = LgdAnalyzer(ctx)
        analyzer.analyze()

        print("\n")
        logger.info("=== Phase 3: Rendering  &  Exporting intermediate dumps ===")
        renderer = HumanReadableCRenderer(ctx)
        renderer.render(self.file_path + ".c")

        csv_out_path = self.file_path + ".csv"
        exporter = LgdCsvExporter(ctx)
        exporter.export(csv_out_path)

        # full_dec_path = self.file_path + ".decrypted.lgd"
        # full_decryptor = LgdDecryptor(ctx)
        # full_decryptor.export(full_dec_path)


        # --- 4. Parse Bytecode ---
        print("\n")
        logger.info("=== Phase 4: Analyze the bytecodes===")
        ctx.bytecode_offset_start = next_off

        bc_parser = BytecodeParser(data)
        ctx.bytecode_instructions, next_off = bc_parser.parse(ctx.bytecode_offset_start)

        logger.info(f"[Bytecode      ] Instructions: {len(ctx.bytecode_instructions)}")
        logger.info(f"[Bytecode      ] End Offset: 0x{next_off:X}")

        # --- 5. Render asm ---
        print("\n")
        logger.info("=== Phase 5: Rendering assembly files===")
        asm_out_path = self.file_path + ".asm"
        asm_renderer = LgdAsmRenderer(ctx)
        asm_renderer.render(asm_out_path)

        # --- 6. Compiling Final LGC ---
        print("\n")
        logger.info("=== Phase 6: Compiling Final LGC ===")

        # Ensure we use pathlib for cleaner extension modification
        file_p = Path(self.file_path)
        if file_p.suffix.lower() == ".lgd":
            clean_output_lgc = str(file_p.with_suffix(".lgc"))
        else:
            clean_output_lgc = self.file_path + ".lgc"

        sys.setrecursionlimit(200000)
        threading.stack_size(64 * 1024 * 1024)
        logger.info(f"[Decompiling...] Launching Decompiler in 64MB high-capacity memory thread...")

        thread_exc = []

        def generate_lgc_wrapper(*args):
            try:
                LgcGenerator.generate_complete_lgc(*args)
            except BaseException as e:
                thread_exc.append(e)

        main_thread = threading.Thread(
            target=generate_lgc_wrapper,
            args=(asm_out_path, clean_output_lgc, csv_out_path)
        )
        main_thread.start()
        main_thread.join()

        if thread_exc:
            raise thread_exc[0]

        # --- 6.5. Refine Final LGC ---
        if refine:
            print("\n")
            logger.info("=== Phase 6.5: Refining Final LGC ===")
            lgc_p = Path(clean_output_lgc)
            if lgc_p.exists():
                from lgd_tool.lgd_decompiler.LGC_refiner.refiner import LgcRefiner
                from lgd_tool.config import REFINER_DATA_DIR

                refiner = LgcRefiner(REFINER_DATA_DIR)
                raw_lgc_code = lgc_p.read_text(encoding='utf-8')
                refined_lgc_code = refiner.refine(raw_lgc_code)
                lgc_p.write_text(refined_lgc_code, encoding='utf-8')
            else:
                logger.warning(f"[Refiner] Generated LGC file not found: {clean_output_lgc}")

        # ==========================================
        # --- 7. Cleanup ---
        # ==========================================
        if not keep_intermediate:
            print("\n")
            logger.info("=== Phase 7: Cleaning up intermediate files ===")
            intermediate_files = [
                asm_out_path,
                csv_out_path,
                self.file_path + ".c",
                # full_dec_path
            ]
            for file in intermediate_files:
                inter_p = Path(file)
                if inter_p.exists():
                    try:
                        inter_p.unlink()
                        logger.info(f"[CLEAN-UP] Deleted: {file}")
                    except Exception as e:
                        logger.error(f"[CLEAN-UP] Failed to delete {file}: {e}")



        print("\n")
        logger.info("Pipeline completed successfully.")