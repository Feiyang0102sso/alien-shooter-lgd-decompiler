# LgdDecompiler V 0.4.0

🌍 **Language / 语言**

- [🇺🇸 English Version](# 🇺🇸 English Version)
- [🇨🇳 中文版](# 🇨🇳 中文版)

------

## 🇺🇸 English Version

### Changelog

- **v0.4.0 (2026-03-20):**
  - AST Path Exploration algorithm optimized: Complexity reduced from $O(2^N)$ to $O(N)$, significantly improving performance.
  - Code String Generation algorithm optimized: Complexity reduced from $O(2^N)$ to $O(N)$, significantly improving performance.
  - No longer stuck when processing large LGD files.
  - Optimized `if else-if` code generation algorithm  to eliminate duplicate code blocks.
  - Add capability in processing local `unstatic` arrays.
  - Added --refine option for optimizing `extern` functions and macro-defined constants, making code more readable.
  - Add auto detect support for old version `flag`.
  - Fixed the Stack_out error caused by unused `#ifdef` or grammar miskate
- **v0.3.0 (2026-03-13):**
  - Fixed the `do-while` infinite loop issue in the control flow.
  - Fixed the logical error caused by nested assignment anomalies.
  - Fixed the Stack_In error in  `&&` `||`caused by unused `#ifdef`
  - **Known Fixes (*Note: All based on Alien Shooter Last Hope*):**
    - Fixed the issue where survival mode gets stuck.
    - Fixed the issue where monsters do not drop any loot
- **v0.2.0 (2026-03-09):**
  - Added `stop_on_error` option and optimized error handling logic.
  - Optimized CSV export and LGC decompilation logic for `extern` functions to appropriately record parameter counts and states.
  - Optimized `PUSH_INT` processing during ASM and LGC decompilation. Extremely large or small integers are now automatically treated as constants or mask values instead of being strictly calculated as signed ints.
  - **Known Fixes (*Note: All based on Alien Shooter Last Hope*):**
    - Fixed crash when clicking the mission success button in campaign mode.
    - Fixed random "Loading" icon appearing on campaign mode maps.
    - Fixed monster indicator arrow appearing only once.
- **v0.1.0 (2026-02-24):** Initial release.

### lgd Manual

If you are interested in learning more about lgd files, please visit

[lgd Manual MD](docs/lgd_doc_EN.md)

Or

[lgd Manual PDF](docs/lgd_doc_EN.pdf)

### How to Use

Simply drag and drop a directory containing `.lgd` files, or a single `.lgd` file, onto the corresponding `.bat` script.

You have the option to keep the intermediate files generated during the analysis process, or clear them to strictly output only the final `.LGC` files.

During execution, please ignore any yellow `[Warning]` logs. As long as there are no red `[Error]` logs, the decompiled scripts should be syntactically sound.


### Project Structure

```bash
LgdDecompiler/
├── main.py                     # Program entry point
├── config.py                   # Global configuration
├── logger.py                   # Logging module
│
├── common/                     # LGD file definition modules
│   ├── binary_utils.py         # Utils: XOR decryption and string formatting
│   ├── definitions.py          # Part 1 & Part 2 table definitions
│   ├── opcodes.py              # VM opcode mapping and instruction definitions
│   └── structures.py           # Overall LGD structural blueprints
│
├── core/                       # Initial analysis and conversion modules
│   ├── analyzer.py             # Further analysis of wrapped objects
│   ├── context.py              # State management for the decompilation context
│   ├── parsers.py              # Parses raw data and wraps into objects
│   └── pipeline.py             # Main pipeline scheduler
│
├── generate_intermediate/      # Intermediate product generation
│   ├── lgd_decryptor.py        # Decrypts the raw .lgd binary file
│   ├── renderer_asm.py         # Converts bytecode into readable .asm for analysis
│   ├── renderer_c.py           # Experimental analyzer for P1 & P2 (for manual review)
│   └── exporter_csv.py         # Exports string/extern tables to CSV format
│
├── generate_LGC/               # Core LGC code generator
│   ├── asm_parser.py           # ASM Parser: Reads .asm and converts to structured objects
│   ├── asm_structs.py          # Data structures for assembly instructions and methods
│   ├── cfg_builder.py          # CFG Builder: Splits Basic Blocks and jump edges
│   ├── cfg_structs.py          # Data structures for CFG basic blocks
│   ├── ast_builder.py          # AST Builder: Derives expressions via symbolic execution
│   ├── ast_structs.py          # AST Nodes (Variables, constants, binary ops, etc.)
│   ├── flow_structurer.py      # Flow Structurer: Identifies If/While/For via graph theory
│   ├── lgc_context.py          # LGC specific context (local variables, type inference)
│   ├── lgc_header_manager.py   # Header Manager: Handles globals, externs, and arrays
│   ├── lgc_optimizer.py        # Optimizer: Simplifies AST structures and redundant expressions
│   └── lgc_generator.py        # Code Generator: Traverses AST to output final scripts
│
├── LGC_refiner/                # Post-processing code optimizer (Planned)
│   └── lgc_refiner.py          
│
└── test/                       # Test suites
```


------

## 🇨🇳 中文版

### 更新日志

- **v0.4.0 (2026-03-20):**
  - AST 路径探索算法优化：复杂度由 $O(2^N)$ 降低至 $O(N)$ ，大幅提升了反编译速度.
  - 代码字符串生成算法优化：复杂度由 $O(2^N)$ 降低至 $O(N)$，大幅提升了反编译速度。
  - 解决了处理大型 LGD 文件时的程序卡死的问题。 
  - 优化了 `if else-if` 代码生成逻辑，彻底消除了反编译过程中产生的大量重复代码。
  - 添加处理局部非静态数组变量的能力。
  - 新增`--refine`选项，支持对 `extern` 函数和宏定义常数进行优化,增加代码可读性。
  - 添加自动识别旧版`flag`的功能.
  - 修复了由未使用的 `#ifdef` 或语法错误引起的Stack_out 错误
- **v0.3.0 (2026-03-13):**
  - 修复了控制流中造成`do-while`死循环的问题。
  - 修复了嵌套赋值异常造成的逻辑谬误。
  - 修复了由未使用的 `#ifdef` 引起的 `&&` `||` 中的 Stack_In 错误
  - **已知修复（*注：均以 Alien Shooter Last Hope 为准*）：**
    - 修复生存模式会卡死的问题。
    - 修复怪物不掉落装备的问题。
- **v0.2.0 (2026-03-09):**
  - 添加 `stop_on_error` 选项，并且优化 error 处理逻辑。
  - 优化 csv 导出和 lgc 反编译时处理 extern 函数的逻辑，现在可以记录它们的参数数量等状态。
  - 优化 asm 和 lgc 反编译时对 `PUSH_INT` 的处理，现在特别大和特别小的 int 会自动被当作常量或 mask 值处理，而不是全算作 signed int。
  - **已知修复（*注：均以 Alien Shooter Last Hope 为准*）：**
    - 修复战役模式点击通关按钮闪退的问题。
    - 修复战役模式地图中随机出现 loading 图标的问题。
    - 修复指向怪物的箭头只能出现一次的问题。
- **v0.1.0 (2026-02-24):** 初始发布 (Initial release)。

### lgd文档

如果你有兴趣了解更多有关lgd文件的信息,请访问

[lgd说明手册 MD](docs/lgd_doc_CN.md)

或

[lgd说明手册 PDF](docs/lgd_doc_CN.pdf)


### 如何使用

将含有 `.lgd` 的文件夹路径或单个 `.lgd` 文件直接拖拽到对应的 `.bat` 脚本上即可执行。

你可以选择保留分析过程中的中间产物，或者清除它们只保留最终生成的 `.LGC` 源码文件。

在运行过程中出现的黄色 `[警告]` 日志可以忽略，只要不出现红色的 `[报错]`，生成的脚本在语法上至少是完整的。


### 项目结构

```bash
LgdDecompiler/
├── main.py                     # 程序入口点
├── config.py                   # 全局配置
├── logger.py                   # 日志模块
│
├── common/                     # lgd文件定义模块
│   ├── binary_utils.py         # 辅助工具：XOR解密算法和格式化字符串
│   ├── definitions.py          # LGD P1与P2表格中的基础定义
│   ├── opcodes.py              # 虚拟机操作码映射表与指令定义
│   └── structures.py           # LGD 总体结构蓝图
│
├── core/                       # 初步分析与转化模块
│   ├── analyzer.py             # 对封装对象进行进一步分析
│   ├── context.py              # 反编译对象上下文状态管理
│   ├── parsers.py              # 解析二进制并封装为对象
│   └── pipeline.py             # 总体任务调度
│
├── generate_intermediate/      # 中间产物生成
│   ├── lgd_decryptor.py        # 解密原始的 .lgd 二进制文件
│   ├── renderer_asm.py         # 将字节码转换为可读的 .asm 汇编代码，供后续分析使用
│   ├── renderer_c.py           # 对P1、P2的实验性早期分析版本，用于人工走读校验
│   └── exporter_csv.py         # 将字符串表、外部函数表等导出为 CSV
│
├── generate_LGC/               # LGC源码生成器核心
│   ├── asm_parser.py           # 汇编解析器：读取 .asm 文本并转换回结构化对象
│   ├── asm_structs.py          # 定义汇编指令和方法的数据结构
│   ├── cfg_builder.py          # 控制流图 (CFG) 构建器：切分基本块与跳转边
│   ├── cfg_structs.py          # 定义 CFG 基本块的数据结构
│   ├── ast_builder.py          # 抽象语法树 (AST) 构建器：通过符号执行推导表达式与堆栈状态
│   ├── ast_structs.py          # 定义 AST 节点 (变量、常量、二元运算、函数调用等)
│   ├── flow_structurer.py      # 控制流结构化器：利用图论和支配树识别还原 If/While/For 结构
│   ├── lgc_context.py          # LGC 代码生成的特定上下文（局部变量名、类型推导等）
│   ├── lgc_header_manager.py   # 头部管理器：处理全局变量、外部引用 (Externs) 和数组声明
│   ├── lgc_optimizer.py        # LGC 代码优化器：优化 AST 结构，简化冗余表达式
│   └── lgc_generator.py        # LGC 代码生成器：遍历结构化的 AST 树，输出最终脚本代码
│
├── LGC_refiner/                # 代码后期优化模块（开发中）
│   └── lgc_refiner.py          
│
└── test/                       # 测试套件
```

