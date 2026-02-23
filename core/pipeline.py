"""
core/pipeline.py
"""

import os
import sys
import threading

from generate_LGC.lgc_generator import LgcGenerator
from generate_intermediate.renderer_asm import LgdAsmRenderer
from logger import logger
from core.context import LgdAnalysisContext
from core.parsers import P1LiteralParser, P2SymbolParser, FixedTableParser, BytecodeParser
from core.analyzer import LgdAnalyzer
from generate_intermediate.renderer_c import HumanReadableCRenderer
from generate_intermediate.exporter_csv import LgdCsvExporter
from generate_intermediate.lgd_decryptor import LgdDecryptor


class LgdPipeline:
    def __init__(self, file_path):
        self.file_path = file_path

    def run(self, is_debug: bool = False, keep_intermediate: bool = True):
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            return

        # 1. Load File
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            logger.info(f"Loaded file: {self.file_path} ({len(data)} bytes)")
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
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
        ctx.literal_table, next_off = p1_parser.parse(ctx.p1_offset_start)
        ctx.p1_offset_end = next_off

        # Log P1 Details
        logger.info(f"[Part 1 Literal] Count: {len(ctx.literal_table)}")
        logger.info(f"[Part 1 Literal] Offset Range: 0x{ctx.p1_offset_start:X} -> 0x{ctx.p1_offset_end:X}")

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

        full_dec_path = self.file_path + ".decrypted.lgd"
        full_decryptor = LgdDecryptor(ctx)
        full_decryptor.export(full_dec_path)


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

        if self.file_path.endswith(".lgd"):
            clean_output_lgc = self.file_path[:-4] + ".lgc"
        else:
            clean_output_lgc = self.file_path + ".lgc"

        sys.setrecursionlimit(200000)
        threading.stack_size(64 * 1024 * 1024)
        logger.info(f"[Decompiling...] Launching Decompiler in 64MB high-capacity memory thread...")

        main_thread = threading.Thread(
            target=LgcGenerator.generate_complete_lgc,
            args=(asm_out_path, clean_output_lgc, csv_out_path)
        )
        main_thread.start()
        main_thread.join()

        # --- 6.5. Refine Final LGC ---
        # logger.info("=== Phase 6.5: Refining Final LGC ===")
        # try:
        #     if os.path.exists(clean_output_lgc):
        #         # read generated LGC
        #         with open(clean_output_lgc, 'r', encoding='utf-8') as f:
        #             raw_lgc_code = f.read()
        #
        #         # goto Refiner
        #         refiner = LgcRefiner()
        #         refined_lgc_code = refiner.refine_code(raw_lgc_code)
        #
        #         # overwrite
        #         with open(clean_output_lgc, 'w', encoding='utf-8') as f:
        #             f.write(refined_lgc_code)
        #         logger.info("[Refiner] Successfully refined LGC code (removed redundant ampersand brackets).")
        #     else:
        #         logger.error(f"[Refiner] Could not find generated LGC file: {clean_output_lgc}")
        # except Exception as e:
        #     logger.error(f"[Refiner] Failed to refine LGC code: {e}")

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
                full_dec_path
            ]
            for file in intermediate_files:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        logger.info(f"[CLEAN-UP] Deleted: {file}")
                    except Exception as e:
                        logger.error(f"[CLEAN-UP] Failed to delete {file}: {e}")



        print("\n")
        logger.info("Pipeline completed successfully.")