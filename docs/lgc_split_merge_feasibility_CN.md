# LGC 拆分与合并 — 方案定稿

> 将反编译产出的大 `.lgc` 拆回多文件，并在脚本目录内合并重复模块。  
> 背景：`lgd_tool` 产出单一 `.lgc`；官方编译器用 `#include` 链成 `.lgd`（一地图一包）。

---

## 1. 输入与输出

| 输入 | 输出 |
|------|------|
| 反编译 `.lgc`（+ 可选 `.csv`） | 多文件 `.lgc` 树 + `#include` 链 |
| 整个 `include_root` 目录 | `core/export.lgc`、`core/global_variable.lgc`、`common.lgc`、各地图入口 |

**不可恢复**：官方排版/注释；**`#ifdef` / 条件编译**；从 `.lgd` 直接出多文件（需先反编译）。

---

## 2. 已定方案

### 2.1 函数 → 行号切段（segment）

1. `split_top_level_functions()`，记录每函数 `min_line` / `max_line`
2. 按 Global ID 顺序：若 **`next.min_line < prev.max_line`** → 新 segment
3. 依据：LGC 先定义后调用；同文件内行号不交叉。函数体内回跳不参与。

segment 命名：泄露源码对齐 > `segment_NN.lgc`。

**最后一个 segment**：行号切出的**最后一份** `.lgc` **一律不当作主脚本**（地图入口），其中有多少个函数都不改变这一规则；主脚本须由 manifest / 路径单独指定。拆分流程仍须**检测该 segment 内是否包含 `main()`**（用于校验或报告，不用于把最后一段自动标成入口）。

### 2.2 头部三分法

| 内容 | 输出路径 | 说明 |
|------|----------|------|
| `extern` | `core/export.lgc` | 引擎 API |
| `#define` 常量 | `core/export.lgc` | **启用 `--refine` 时**写入此处 |
| 全局变量（无冲突） | `core/global_variable.lgc` | 见 §2.3 |
| 全局变量（有冲突） | **所属 segment 对应 `.lgc`** | 见 §2.3 |

### 2.3 全局变量分配（`scan_globals.py`）

编译器禁止重复定义：`[ERROR]: int redefinition "Foo"`。  
跨地图扫描时，同名出现多次是反编译副本重复，**不是**源码定义多次。

| 扫描结果 | 写入位置 |
|----------|----------|
| 多文件且声明一致 `[OK]` | `core/global_variable.lgc`（一份） |
| 仅 1 个文件出现（count=1）且无冲突 | `core/global_variable.lgc` |
| 多文件且声明不一致 `[CONFLICT]` | **不进入** `global_variable.lgc`；**保留在各自 segment 源文件** |

**冲突处理原则**（如 `Musics[28]` 各关卡 init/常量不同）：

- 不追究根因（关卡宏不同、反编译差异等均可）
- **凡冲突者，定义写在它所属的 segment 文件下**，不强行并入 `global_variable.lgc`
- 写盘时：共享文件 `#include global_variable.lgc` 且 **strip 已在其中定义的 global**；含冲突名的 segment 文件保留本地定义

### 2.4 include 链（示例）

相对 `include_root`，不带 `maps/` 前缀：

```c
#include "core\export.lgc"
#include "core\global_variable.lgc"
#include "common.lgc"
#include "tutorial.lgc"
// 本 segment 若有 CONFLICT global，写在本文件；其余只有函数
```

地图入口（`addon0/level_01.lgc`）同理；`--source-dir` / `-I` 决定根目录，磁盘不必叫 `maps/`。

### 2.5 地图入口 `main()`

- 一 `.map` → 一 `.lgd`；入口为 `level_xx.lgc` 等，**不等于**行号切分的最后一个 segment
- 须扫描各 segment 是否含 `main()`；反编译里 `main` 常在最后一个 segment，但**不因位置而将该 segment 定为主脚本**
- `main` 之后的死代码函数仍归属同一 segment，不触发新切段

### 2.6 File_ID

仅 **VAR** 可作 globals 归属辅助；**FUNC / EXTERN 全为 0**，函数切段不用。

---

## 3. 单文件拆分流程

```
decompiled.lgc
  ├─ extern              → core/export.lgc
  ├─ #define（若 refine） → core/export.lgc
  ├─ globals
  │    ├─ scan：无冲突    → core/global_variable.lgc（跨图合并时汇总）
  │    └─ scan：CONFLICT → 留在本 segment 的 .lgc
  └─ 函数
       ├─ segment_by_line_jump()
       └─ 每 segment 一个 .lgc + #include
```

校验：展开 include 后，每个 global 名**至多一处**定义（`global_variable` 与 segment 本地不重复）。

---

## 4. 目录级合并（可选）

- 纯函数 segment：hash 相同则合并为一份 + `#include`
- 地图入口不合并
- 含 CONFLICT global 的 segment 不与其他图合并 global 定义

---

## 5. 工具

| 工具 | 用途 |
|------|------|
| `scripts/lgc_globals_scan/scan_globals.py` | count=1 统计；count≥2 列表；CONFLICT → WARNING |
| `scripts/endless_loop_detect/scan_while_issues.py` | `split_top_level_functions`（待抽库） |
| `scripts/refine_data_prepare/` + `--refine` | export 内 extern / `#define` |
| `docs/lgd_doc_CN.md` | 编译器与符号表 |

---

## 6. 实施顺序

| 阶段 | 内容 |
|------|------|
| **1** | 行号 segment 拆函数；scan 分流 globals → `global_variable.lgc` / segment 本地 |
| **2** | `#include` + manifest；试点再编译 |
| **3** | 跨地图 hash 合并无冲突函数文件 |

远期：`lgd_tool split --lgd main.lgd --manifest ...`

---

## 7. 已知限制

- 无法恢复 segment 原始文件名、`#ifdef`
- globals 无行号，不能靠行号切段
- 冲突 global 分散在各 segment，需 strip 避免与 `global_variable.lgc` 重复定义
- 反编译质量（while/iff）影响可编译性

---

*定稿：2026-05-23*
