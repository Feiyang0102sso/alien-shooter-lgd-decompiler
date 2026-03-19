from pathlib import Path
import lgd_tool.config
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline

# 强制使用测试数据目录下的数据库进行验证
lgd_tool.config.REFINER_DATA_DIR = Path(__file__).parent / "data"

if __name__ == "__main__":
    from lgd_tool import config
    config.init_app_env()
    
    lgd_path = Path(r"d:\python coding\lgd_tool\tests\test_refiner\data\tutorial_00.lgd")
    print(f"Starting decompile and refine on: {lgd_path}")
    
    # 跑全流程，开启 refine
    # 此时 LgcRefiner 内部会自动打印未优化的常量（如果有）
    pipeline = LgdPipeline(str(lgd_path))
    pipeline.run(keep_intermediate=True, refine=True)
    
    lgc_path = lgd_path.with_suffix('.lgc')
    if lgc_path.exists():
        print(f"\nRefinement completed. Check logs for details. Output: {lgc_path}")
    else:
        print(f"Error: {lgc_path} was not generated!")
