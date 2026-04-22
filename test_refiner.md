# 测试文件夹目录结构重构计划

为了提升 `tests` 文件夹的专业性和可维护性，建议将其重构为镜像 `src` 代码结构的布局，并明确区分单元测试、集成测试和测试资源。

## 用户审核事项

> [!IMPORTANT]
> 1. **目录更名**：现有的 `test_asm`, `test_ast` 等目录将被移动并更名，以匹配 `src` 中的包名。
> 2. **遗留代码处理**：如果存在旧版代码则 将被移动到 `archive/` 目录，不再作为常规测试运行。 `test_old_ver`是为了测试新旧版本的lgd解包能力 不属于此类
> 3. **辅助工具更名**：`test_utils.py` 因为不是实际测试文件，将被移动到 `utils/` 并更名。

## 拟议的更改

### 1. 结构化目录方案

新的 `tests` 目录结构将如下所示：

```text
tests/
├── unit/                       # 单元测试，镜像 src/lgd_tool 结构
│   ├── lgd_decompiler/
│   │   ├── common/             # 存放通用工具测试 (如 asm_util)
│   │   ├── generate_intermediate/ # 存放中间层生成测试 (如 asm_generation)
│   │   ├── generate_LGC/       # 存放 LGC 生成测试 (原 test_optimizer)
│   │   └── LGC_refiner/        # 存放 LGC 优化测试 (原 test_refiner)
│   ├── test_logger.py
│   └── test_config.py
├── integration/                # 集成测试，验证完整流程
├── fixtures/                   # 存放测试用例所需的静态数据 (迁移各目录下的 data/)
├── utils/                      # 测试辅助工具函数 (非测试用例)
├── archive/                    # 遗留/过期测试代码 (原 test_old_ver)
├── conftest.py                 # 全局 Pytest 配置与 Fixtures
└── pytest.ini                  # Pytest 运行参数配置
```

### 2. 文件迁移映射 [MODIFY]

| 原路径 | 新路径 | 说明 |
| :--- | :--- | :--- |
| `tests/test_asm/test_asm_util.py` | `tests/unit/lgd_decompiler/common/test_asm_util.py` | 归类到 common |
| `tests/test_ast/test_ast_util.py` | `tests/unit/lgd_decompiler/common/test_ast_util.py` | 归类到 common |
| `tests/test_asm/test_asm_generation.py` | `tests/unit/lgd_decompiler/generate_intermediate/test_asm_generation.py` | 归类到生成环节 |
| `tests/test_optimizer/*` | `tests/unit/lgd_decompiler/generate_LGC/*` | 对应优化器组件 |
| `tests/test_refiner/*` | `tests/unit/lgd_decompiler/LGC_refiner/*` | 对应重构器组件 |
| `tests/test_old_ver/` | `tests/archive/legacy_v1/` | 归档遗留测试 |
| `tests/test_utils.py` | `tests/utils/test_helpers.py` | 更名以避免被 pytest 错误识别为测试 |

### 3. 数据管理优化

- 将分散在各个目录下的 `data/` 文件夹统一迁移到 `tests/fixtures/`。
- 更新测试代码中的文件引用路径，使用基于 `tests/fixtures/` 的相对路径或通过 pytest fixture 动态获取。

## 验证计划

### 自动测试
- 在重构前后分别运行 `pytest`，确保测试通过（且测试数量一致或因迁移而更清晰）。
- 运行 `pytest --collect-only` 核对所有测试是否被正确发现。

### 手动验证
- 检查文件系统结构是否符合预期。
- 确认 `archive/` 下的代码不会被 `pytest` 默认执行。
