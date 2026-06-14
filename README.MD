# LgdDecompiler V 0.7.0

🌍 **Language / 语言**

- [🇺🇸 English Version](#english-version)
- [🇨🇳 中文版](#chinese-version)

------

<a id="english-version"></a>
## 🇺🇸 English Version

### Changelog

- **v0.7.0 (2026-06-14):**
  - Added new standalone encryption/decryption package for binary patching workflows.
  - Added CLI options `--decrypt` (`-d`) and `--encrypt` (`-e`) for file-level or directory-level batch encryption and decryption.
- **v0.6.1 (2026-06-03):**
  - Optimized and fixed the path logic of the reorganize module. 
  - Fixed the issue where paths would contain the root directory during single-file decompilation.
  - Fixed the issue where parameter array parameters in function declarations lost their array brackets `[]` when generating LGC.
  - Fixed the issue where `#include "segment_00.lgc"` was incorrectly written to `export.lgc` when no physical segment_00 was generated. This occurs when decompiling a previously merged LGC file compiled into LGD again.
- **v0.6.0 (2026-05-30):**
  - Added `--reorganize` option to split large LGC scripts and merge similar items.
  - Optimized the `--refine` option logic; it can now only be used after `--reorganize`.
  - Added conflict resolution functionality to automatically clear all LGC files in the folder on each run.
- **v0.5.0 (2026-05-22):**
  - Fixed do-while latches mis-structured as empty `while (cond) {}` or `while(1)` without `break`, extending the v0.3.0 multi-block fix.
  - Fixed do-while inverted loop-exit semantics when generating `if (cond) break;` (outer `!` stripped incorrectly).
  - Fixed side-effect statements dropped on the `if (...) break;` path during do-while structuring.
  - Fixed dual-exit do-while losing post-loop code .
  - Fixed ASM output truncating string literals longer than 40 characters.
  - **Known Fixes:**
    - *Alien Shooter Last Hope*: turret creation success rate restored to match the original.
    - *Alien Shooter Free 4.5.3*: basic regression tests pass.
    - *Alien Shooter Free 4.5.3*: shop / UI issues caused by truncated resource paths.
    - *Alien Shooter Free 4.5.3*: survival mode not spawning monsters.
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

Simply drag and drop a directory containing `.lgd`/`.lgd.bak` files, or a single file, onto the corresponding `.bat` script.

You can select the Decrypt (2) or Encrypt (3) main modes to decode `.lgd` files into editable plaintext `.lgd.bak` (for hex binary patching) and encrypt them back.

You have the option to keep the intermediate files generated during the analysis process, or clear them to strictly output only the final `.LGC` files.

During execution, please ignore any yellow `[Warning]` logs. As long as there are no red `[Error]` logs, the decompiled scripts should be syntactically sound.

------

<a id="chinese-version"></a>
## 🇨🇳 中文版

### 更新日志

- **v0.7.0 (2026-06-14):**
  - 新增独立的 LGD 二进制文件加密解密模块，用以支持二进制补丁（binary patch）修改流。
  - 主 CLI 新增 `--decrypt` (`-d`) 与 `--encrypt` (`-e`) 命令行参数，支持单文件与目录批量加解密。
- **v0.6.1 (2026-06-03):**
  - 优化并修复 reorganize 模块的路径逻辑。
  - 修复单文件反编译时路径会包含根目录的问题。
  - 修复函数声明参数中的数组参数在生成 LGC 时丢失数组符号 `[]` 的问题。
  - 修复未物理生成段文件却在 `core/export.lgc` 错误写入 `#include "segment_00.lgc"` 的问题（主要因使用未重组的单大 LGC 编译为 LGD 后，再次尝试使用重组反编译所触发）。
- **v0.6.0 (2026-05-30):**
  - 新增 `--reorganize` 选项，对大 LGC 脚本进行拆分并合并同类项
  - 优化`--refine` 选项逻辑，现在其仅能在  `--reorganize` 之后使用
  - 新增冲突处理功能，会在每次运行时自动清空文件夹下所有 LGC 文件
- **v0.5.0 (2026-05-22):**
  - 修复 do-while latch 被错误结构化为空 `while (cond) {}` 或缺少 `break` 的 `while(1)`；在 v0.3.0 多基本块修复基础上继续完善。
  - 修复 do-while 生成 `if (cond) break;` 时外层 `!` 被误剥，导致循环退出语义反转。
  - 修复 do-while 结构化时 `if (...) break;` 路径上的副作用语句被丢弃。
  - 修复双出口 do-while 丢失 post-loop 代码。
  - 修复 ASM 输出截断长度超过 40 的字符串字面量。
  - **已知修复：**
    - *Alien Shooter Last Hope*：炮塔创建成功率恢复至与原版一致。
    - *Alien Shooter Free 4.5.3*：基本回归测试通过。
    - *Alien Shooter Free 4.5.3*：截断资源路径引发的商店 / UI 异常。
    - *Alien Shooter Free 4.5.3*：生存模式不刷怪。
- **v0.4.0 (2026-03-20):**
  - AST 路径探索算法优化：复杂度由 $O(2^N)$ 降低至 $O(N)$，大幅提升反编译速度。
  - 代码字符串生成算法优化：复杂度由 $O(2^N)$ 降低至 $O(N)$，大幅提升反编译速度。
  - 处理大型 LGD 文件时不再卡死。
  - 优化 `if else-if` 代码生成逻辑，消除重复代码块。
  - 新增处理局部 `unstatic` 数组的能力。
  - 新增 `--refine` 选项，优化 `extern` 函数与宏定义常量，提升可读性。
  - 新增自动识别旧版 `flag` 的支持。
  - 修复未使用的 `#ifdef` 或语法错误引起的 Stack_out 错误。
- **v0.3.0 (2026-03-13):**
  - 修复控制流中 `do-while` 死循环问题。
  - 修复嵌套赋值异常造成的逻辑错误。
  - 修复未使用的 `#ifdef` 在 `&&` / `||` 中引起的 Stack_In 错误。
  - **已知修复（*注：均以 Alien Shooter Last Hope 为准*）：**
    - 修复生存模式卡死。
    - 修复怪物不掉落装备。
- **v0.2.0 (2026-03-09):**
  - 新增 `stop_on_error` 选项，优化错误处理逻辑。
  - 优化 CSV 导出与 LGC 反编译中 `extern` 函数的参数记录。
  - 优化 ASM / LGC 反编译中的 `PUSH_INT` 处理：过大或过小的整数自动视为常量或 mask，而非 signed int。
  - **已知修复（*注：均以 Alien Shooter Last Hope 为准*）：**
    - 修复战役模式点击通关按钮闪退。
    - 修复战役模式地图随机出现 Loading 图标。
    - 修复指向怪物的箭头仅显示一次。
- **v0.1.0 (2026-02-24):** 初始发布。

### lgd文档

如果你有兴趣了解更多有关lgd文件的信息,请访问

[lgd说明手册 MD](docs/lgd_doc_CN.md)

或

[lgd说明手册 PDF](docs/lgd_doc_CN.pdf)


### 如何使用

将含有 `.lgd` / `.lgd.bak` 的文件夹路径或单个文件直接拖拽到对应的 `.bat` 脚本上即可执行。

拖拽文件至脚本后，你还可以选择运行解密 (2) 或加密 (3) 模式，将 `.lgd` 文件解密为明文 `.lgd.bak`（以便使用 Hex 工具直接进行二进制补丁修改），或将其重新打包回密。

你可以选择保留分析过程中的中间产物，或者清除它们只保留最终生成的 `.LGC` 源码文件。

在运行过程中出现的黄色 `[警告]` 日志可以忽略，只要不出现红色的 `[报错]`，生成的脚本在语法上至少是完整的。

