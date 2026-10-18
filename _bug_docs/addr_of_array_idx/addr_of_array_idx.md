# &arr[i] 反编译丢失下标（ADDR_OF 漏消费 ARRAY_IDX）

## 发现

| 项 | 内容 |
|---|---|
| 反编译器版本 | lgd_tool **0.7.0**（`da8bfd3`） |
| 样本 | ASTD |
| lgd | `maps/main.lgd`、`maps/logo.lgd`、`maps/addon0/default.lgd`（NEW 格式，文件日期 2023-07-17） |
| md5 | main `a309f8542415b5d70bfcfd0e554d003d`<br>logo `07ca3f2f4c486f0cf041c49588eda9bd`<br>addon0/default `bebcbc8b144a306300c987c67f8c2e4e` |
| 函数 | `refreshEnemyPathDirections()`，三个 lgd 中各 1 处 |
| 存在范围 | 至少从 `ce0a54b`（2026-03-19）起即存在；0.6.0（`f898a39`）、0.6.1（`6dd0693`）、0.7.0 输出完全相同，不是回归 |

发现过程：修复 [segment 0 重复引用](../duplicate_segment0_in_export/duplicate_segment0_in_export.md) 后，ASTD 拆分版仍无法编译。该错误此前一直被 `Function redefinition` 挡住：`--stop-on-error` 下编译器遇到第一个错误即停止，而 `export.lgc` 位于每个文件的最前面。

ASF453 / ASLH / ASNE 中均未出现：这三个游戏的源码里从未使用过 `&数组[下标]` 这种写法。

## 现象

未拆分的 lgc 直接编译即报错：

``` txt
Compile: main.lgc[ERROR]: invalid operation for array: %,
 in file: .../main.lgc at line 22196
```

``` c
if (Action(refreshEnemyPathDirections_local14, 165, (&refreshEnemyPathDirections_local7), __DUMMY_ARG__[refreshEnemyPathDirections_local11])) {
```

反编译过程中没有任何 ERROR 或 WARNING。

## 目录

| 路径 | 内容 |
|---|---|
| `scene/refreshEnemyPathDirections.asm` | 现场：该函数完整 asm（`main.lgd.asm` 第 52784~53021 行） |
| `scene/refreshEnemyPathDirections.decompiled.lgc` | 现场：0.7.0 的反编译结果（`main.lgc` 第 22119~22210 行） |
| `scene/refreshEnemyPathDirections.reconstructed.lgc` | 根据 asm 推测还原的源码 |
| `maps/addr_of.lgc` | 最小复刻：后面跟着默认参数，生成 `__DUMMY_ARG__[i]` |
| `maps/addr_of_full_args.lgc` | 变体：参数全部显式传入，下标泄漏到下一条语句 |
| `maps/addr_of_user_func.lgc` | 变体：传给普通函数，参数整个丢失 |
| `maps/addr_of_assign.lgc` | 变体：直接赋值，下标跑到等号左边 |

`maps/` 下的 `.lgc` 用 `lgc_compiler.exe` 编译出 lgd 后，再用修复前的反编译器处理即可复现。

## 源码在干什么

每波开始时，给场上 vid 为 1364 / 3956 的敌人分配一条可走的路径：

1. 读出本波的路径数量（最多 4 条），逐条确认路径在地图上存在，存在就把 `pathName[i] = "path_" + itoa(i)`
2. 遍历所有单位，对目标敌人依次尝试 `Action(unit, 165, &pathName[i])`，即把路径名的**地址**交给引擎；成功就把 vid 改为 1364 并 break
3. 最后 `Action(unit, 62, vid)` 设置单位外观

问题出在第 2 步的 `&pathName[i]`：取字符串数组元素的地址。

## 成因

asm（`scene/refreshEnemyPathDirections.asm`，0x6724E 起）：

``` txt
PUSH_VAR     refreshEnemyPathDirections_local14    ; unit
PUSH_INT     165
PUSH_VAR     refreshEnemyPathDirections_local11    ; i
ARRAY_IDX                                          ; 挂起下标 i
ADDR_OF      refreshEnemyPathDirections_local7     ; 应为 &pathName[i]
PUSH_VAR     Action_arg3                           ; 编译器补的默认参数
PUSH_VAR     Action_arg4                           ; 编译器补的默认参数
CALL_EXT_79                                        ; Action
```

asm 本身没有问题。`ARRAY_IDX` 是挂在下一条带变量指令上的"前缀"，`ast_builder.build_block_ast` 把下标存进 `pending_array_index`，等下一个变量来消费：

1. `ADDR_OF` 只生成 `&local7`，**没有消费**挂起的下标。`PRE_INC` / `POST_INC` 曾因同类问题加过"防止索引被下一个变量错误吞噬"的修复，`ADDR_OF` 漏了
2. 下标泄漏给下一条 `PUSH_VAR Action_arg3`。它是别的函数的参数名，被识别为默认参数噪声，替换为 `__DUMMY_ARG__`，又因带着下标，被包成 `ArrayAccessNode(__DUMMY_ARG__, i)`
3. 调用处的过滤只删除**裸的** `VarNode("__DUMMY_ARG__")`，被包裹的漏网，最终输出 `__DUMMY_ARG__[i]`

## 触发条件

**只要出现 `&数组[下标]` 就会触发**，与是否 extern、参数是否传满无关。泄漏的下标会被之后**第一条**消费下标的指令吃掉，症状取决于是谁吃掉的：

| 写法 | 吃掉下标的指令 | 反编译结果 | 编译 |
|---|---|---|---|
| `Action(0, 165, &pathName[i])` | `PUSH_VAR Action_arg3`（默认参数） | `(&main_local0), __DUMMY_ARG__[main_local4]` | 报错 |
| `Action(0, 165, &pathName[i], 7, 8); total = total + i;` | 下一条语句的 `PUSH_VAR main_local5` | `(&main_local0)` + `main_local5[main_local4] + ...` | 报错（碰巧是标量） |
| `setPath(&pathName[i])` | `ASSIGN setPath_arg0` | `setPath(0)` | **通过，语义错** |
| `p = &pathName[i]` | `ASSIGN main_local5` | `main_local5[main_local4] = (&main_local0)` | 报错（碰巧是标量） |

`setPath(0)` 最危险：赋值目标变成 `setPath_arg0[main_local4]`，`ARG_COMMIT` 的正则 `^(\w+)_arg(\d+)$` 匹配失败，参数落入后备池 `pending_args_fallback` 后无人取用、被静默丢弃；第二个参数的默认值 `0` 被挤到了第一个参数的位置。原调用 `setPath(&pathName[i], 0)` 变成了 `setPath(0, 0)`。

## 为什么没有任何报错

现有检查都在数栈里的节点数量，而这里的数量完全对得上：

| 检查 | 为什么没触发 |
|---|---|
| Stack_In（栈下溢） | `ADDR_OF` 压 1 个，泄漏的下标被下一个 `PUSH_VAR` 消费后也是 1 个，`CALL_EXT_79` 弹出的数量正好 |
| Stack_Out（栈残留） | 没有残留 |
| `__DUMMY_ARG__` | 生成时不打日志，过滤时漏掉了被包裹的情况 |
| `pending_array_index` | 没有任何校验 |
| 后备参数池 | 没有任何校验，未被取用的参数直接丢弃 |

这是**绑定错误**（下标挂错了对象），不是 3 月修过的 Stack_In / Stack_Out 那类**数量错误**。

## 修复

- `generate_LGC/ast_builder.py`
  - `ADDR_OF`：有挂起下标时生成 `&var[idx]`
  - 不变量检查：`ARRAY_IDX` 的下一条指令未消费下标 → error。ASTD 三份 asm 中，`ARRAY_IDX` 之后只出现过 `ASSIGN` / `OP_ASSIGN` / `PUSH_VAR` / `PRE_INC` / `POST_INC` / `ADDR_OF`，其中 `ADDR_OF` 每份恰好 1 次，即本现场
  - `__DUMMY_ARG__` 收到下标 → error
  - 块尾仍有挂起下标 → error
  - 块尾后备参数池有未被任何调用取走的参数 → error
- `generate_LGC/lgc_generator.py`：函数输出中残留 `__DUMMY_ARG__` → error

只检查"套到 `__DUMMY_ARG__` 上"或"块尾未消费"不够：`addr_of_full_args` 中下标在块内被一个普通标量消费，两者都拦不住，必须在 `ARRAY_IDX` 之后紧接着检查。

所有 error 均为 `logger.error_and_stop`：默认打印 ERROR 并继续，`--stop_on_error` 时中止。

修复后的输出：

| 用例 | 反编译结果 |
|---|---|
| `addr_of` | `Action(0, 165, (&main_local0[main_local4]));` |
| `addr_of_full_args` | `Action(0, 165, (&main_local0[main_local4]), 7, 8);`<br>`main_local5 = (main_local5 + main_local4);` |
| `addr_of_user_func` | `setPath((&main_local0[main_local4]), 0);` |
| `addr_of_assign` | `main_local5 = (&main_local0[main_local4]);` |
| ASTD 现场 | `Action(refreshEnemyPathDirections_local14, 165, (&refreshEnemyPathDirections_local7[refreshEnemyPathDirections_local11]))` |

## 测试

- 单测 `tests/unit/lgd_decompiler/generate_LGC/test_ast_array_index_binding.py`：`ADDR_OF` 生成 `&arr[i]`，以及 4 种 error（下标未被紧随指令消费、`__DUMMY_ARG__` 带下标、块尾下标残留、后备参数未取用）
- 回归 `tests/regression/test_addr_of_array_idx_regression.py`：以 `stop_on_error` 反编译 4 个复刻，断言输出语句正确且无 `__DUMMY_ARG__`
  - fixture：`tests/fixtures/original_lgc/addr_of_array_idx/`（源码），`tests/fixtures/lgd_files/addr_of_array_idx/`（编译得到的 lgd）
- 修复前代码上这 9 个用例全部失败

## 验证

- 全部 99 个样本 / fixture lgd（ASF453、ASLH、ASNE、ASTD、tests fixtures）修复前后反编译均为 0 条 ERROR，新检查无误报；修复后 0 处 `__DUMMY_ARG__`
- 4 个复刻修复后的反编译结果均可重新编译
- ASTD 原版 lgd 反编译 + 拆分后，37 个脚本全部编译通过
