# 字符串常量被改写（asm_parser 把 PUSH_STR 当作普通操作数切分）

## 发现

| 项 | 内容 |
|---|---|
| 反编译器版本 | 现场用 lgd_tool **0.7.0** 生成；**0.8.0**（`de0dc1c`）复现结果完全相同 |
| 样本 | ASW 7.3.4（PC 移植，运行在 Alien Shooter Gold PC 引擎上） |
| lgd | `maps/main.lgd`（原版，文件日期 1981-01-01，md5 `73558dafa73470e6408ee7599acbef81`）<br>同目录下的 `pvp/`、`strike/`、`survive/`、`addon*/` 关卡 lgd 都包含同一份主脚本，症状相同 |
| 函数 | 字符串内容被改动的有 103 个函数，影响联网的是 `setMultiplayerData()` 和 `multiplayerP2PMessageSend()` 等 |
| 存在范围 | `asm_parser.py` 第 122 行是首次提交 `70f00bc`（2026-02-23）就有的代码，**所有版本都有**，不是回归 |
| 状态 | **已修复**（0.8.0 之后的工作区，未提交），见“修复”一节 |

发现过程：用 0.7.0 反编译 ASW 7.3.4 的全部 lgd，不做任何修改直接重新编译。游戏能进，大厅能连上，也不会出现红色的联网失败提示，但**随机匹配一直匹配不到人，加入房间也会失败**。逐函数对比原版 lgd 和重编译 lgd 的字节码，发现字符串常量被改了。

反编译和重新编译都没有任何 ERROR，编译器也没有报错。

## 现象

`setMultiplayerData()` 向引擎登记大厅房间/玩家的负载键名，键名之间用 `;` 分隔：

| 位置 | 原版字符串 | 反编译结果 |
|---|---|---|
| `multiplayerSetRoomPayloadKeys` | `"gamma;missionName;gameMode;mode;map;level;checkpoints;number;pvpSide;rating;disableBanOnLeave;"` | `"\"gamma"` |
| `multiplayerSetPlayerPayloadKeys` | `"light;banner;…;runplatform;protocolVersion;team;"` + 3 个 `";"` + `"idHiPart;idLoPart;"` | `"\"light"` + 3 个 `""` + `"\"idHiPart"` |
| `multiplayerSetSessionDataKeys` | `"store_equiped;"` | `"\"store_equiped"` |
| `multiplayerP2PMessageSend` | `"message_type;" + arg1` | `"\"message_type" + arg1` |

ASW 7.3.4 的 `main.lgd` 中，12340 条 `PUSH_STR` 有 318 条被改写，共 234 种不同的字符串：

| 类型 | 条数 | 例子 |
|---|---|---|
| 含 `,` | 219 | `",  perkId: "` → `" perkId: "`；广告配置 JSON `{"rewardedVideo": true, "currency": …}` 的逗号全部丢失，变成无效 JSON |
| 连续空白（不含 `,` `;`） | 86 | `"  isMultiplayer = "` → `" isMultiplayer = "` |
| 含 `;` | 13 | 即上表的联网字符串，加上 `impl_removeItemPayload` 和 `sendSquadLeaderToSquadMemebers` 用到的 `";"` |

大部分是日志文本，改了也不影响逻辑。但只要字符串被当作**数据格式**（分隔符、协议前缀、JSON），就会出语义错误。

### 联网为什么坏了

引擎用 `;` 切分键名列表，按键名从注册表取值，**值为空的键直接跳过**（Alien Shooter Gold PC 引擎 `webrtc_session.cpp` 的 `payloadFromRegistry`）：

``` cpp
auto payloadKeys = registry.getString(keysRegKey, "").split(";");
for (STRING key : payloadKeys) {
    STRING value = registry.getString(valueRegPrefix + key, "");
    if (!value.isEmpty()) { /* add KV to payload */ }
}
```

键名表坏了以后只剩一个不存在的键 `"gamma`，它的值永远为空。所以 CreateRoom 和 JoinRoom 发给大厅的 Payload **是空的**，没有 gameMode、map、level、protocolVersion。大厅的 WebSocket 连接本身正常，所以不报错；但服务器没法按模式和版本匹配，加入的一方也读不到地图和关卡。P2P 消息的类型前缀坏了，组队消息也解析不了。

## 目录

| 路径 | 内容 |
|---|---|
| `scene/setMultiplayerData.asm` | 现场：0.8.0 生成的完整 asm（`main.lgd.asm` 第 133737~134073 行） |
| `scene/setMultiplayerData.decompiled.lgc` | 现场：0.8.0 的反编译结果 |
| `scene/setMultiplayerData.reconstructed.lgc` | 按原版字节码还原字符串后的源码 |
| `scene/multiplayerP2PMessageSend.*` | 同上，第二个现场（`main.lgd.asm` 第 41963~41983 行） |
| `maps/string_literal.lgc` | 最小复刻：`;`、`,`、连续空白、引号内的 `;` |
| `maps/string_newline.lgc` | 最小复刻：字符串中的真实换行符 |

`maps/` 下的 `.lgc` 用 `lgc_compiler.exe` 编译出 lgd，再用修复前的反编译器处理即可复现。注意：反编译器会**先删除目标目录里已有的 `.lgc`**，所以要把 lgd 拷到空目录再反编译。

还原版的验证方法：把两个 `reconstructed.lgc` 替换回 0.8.0 输出的完整 `main.lgc`，重新编译后，这两个函数的字符串与原版完全一致，`multiplayerP2PMessageSend` 的归一化字节码也完全一致。

## 成因

asm 渲染出来的字符串是正确的：

``` txt
  17A0B4:  02 67 61 6D 6D 61  PUSH_STR     "gamma;missionName;gameMode;mode;map;level;checkpoints;number;pvpSide;rating;disableBanOnLeave;"
  17A1BB:  02 3B 00           PUSH_STR     ";"
  128E33:  02 6D 65 73 73 61  PUSH_STR     "message_type;"
```

问题出在 **asm → AST 这一段**，一共三步。

### 1. `asm_parser.py:122`：把字符串当作普通操作数切分

``` python
clean_args_str = raw_args.split(';')[0].replace(',', ' ').strip()
operands = clean_args_str.split()
```

这一行原本处理的是 `PUSH_VAR a, b   ; 注释` 这类指令：`;` 后面是注释，`,` 是操作数分隔符。它对 `PUSH_STR` 没有做特殊处理：

| 操作 | 本意 | 对字符串的副作用 |
|---|---|---|
| `split(';')[0]` | 去掉行尾注释 | 字符串在第一个 `;` 处被截断，**闭合引号也一起丢了** |
| `replace(',', ' ')` | 逗号分隔符变空格 | 字符串里的 `,` 全部变成空格 |
| `split()` | 按空白切操作数 | 连续空白、制表符被吞掉 |

### 2. `ast_builder.py:76-83`：拼回去，但判断不出引号已经残缺

``` python
val = " ".join(ops) if ops else ""
if val.startswith('"') and val.endswith('"'):
    val = val[1:-1]
val = val.replace('\\', '\\\\').replace('"', '\\"')
```

- `join(" ")` 只能用一个空格拼回去，所以连续空白统一变成一个空格（`,` 变成的空格也在这里合并）
- `"gamma;…"` 截断后是 `"gamma`，只有开头一个引号，`endswith('"')` 不成立，引号没被去掉，随后又被转义，最终输出 `"\"gamma"`
- `";"` 截断后只剩一个字符 `"`，它同时满足 `startswith` 和 `endswith`，`val[1:-1]` 得到空串，最终输出 `""`

### 3. `renderer_asm.py:323`：asm 里的字符串格式本身有歧义

``` python
safe_str = op.replace('\n', '\\n').replace('\r', '\\r')
val_str = f'"{safe_str}"'
```

- 字符串里的 `"` 和 `\` 没有转义，所以 `"x\";\"y"`（源码里的写法）渲染成 `PUSH_STR "x";"y"`。只看这一行，无法判断字符串到哪里结束。**只改 parser，不改 asm 格式，修不干净**
- 换行符写成两个字符 `\n`，但 parser 和 ast_builder 都不做反转义，ast_builder 还会把 `\` 再转义一次。结果是源码里的 `"line1\nline2"` 反编译成 `"line1\\nline2"`，重新编译后变成字面量反斜杠加 `n`，而不是换行。ASW 7.3.4 里没有含换行的字符串，所以这次没碰到，但它是同一类问题

全局变量的字符串初值经由 csv 和 `lgc_context` 生成，不经过 asm_parser，所以**不受影响**：ASW 7.3.4 `main.lgd` 的全局字符串初值，重编译后一个都没丢。

## 触发条件

只要 `PUSH_STR` 的内容满足下面任意一条，就会触发：

| 内容 | 0.8.0 反编译结果 | 重新编译后 | 编译 |
|---|---|---|---|
| `"gamma;missionName;gameMode;"` | `"\"gamma"` | `"gamma`（开头多一个引号，后面全丢） | **通过，语义错** |
| `";"` | `""` | 空串 | **通过，语义错** |
| `"message_type;"` | `"\"message_type"` | `"message_type` | **通过，语义错** |
| `",  perkId: "` | `" perkId: "` | 逗号丢失，空格合并 | 通过 |
| `"{\"a\": 1, \"b\": 2}"` | `"{\"a\": 1 \"b\": 2}"` | JSON 无效 | **通过，语义错** |
| `"  isMultiplayer =   "` | `" isMultiplayer = "` | 空格合并 | 通过 |
| `"x\";\"y"` | `"x"` | `x` | **通过，语义错** |
| `"line1\nline2"`（真实换行符） | `"line1\\nline2"` | 反斜杠 + `n` | **通过，语义错** |

上表前 7 行是 `maps/string_literal.lgc`，最后一行是 `maps/string_newline.lgc`，都是 0.8.0 的实际输出。

用上面三步写成的模拟函数，逐个处理 ASW 7.3.4 `main.lgd` 的全部字符串，预测结果与 0.8.0 实际输出重编译后的字符串**逐函数一致**。只有 4 个函数对不上，它们是别的问题，见文末。

## 为什么没有任何报错

| 检查 | 为什么没触发 |
|---|---|
| asm_parser 的 Begin/End/RET 检查 | 只检查函数边界，不检查操作数内容 |
| AST 栈检查（Stack_In / Stack_Out） | 字符串改了，但仍然只压 1 个 `ConstNode`，数量对得上 |
| lgc_compiler | 改写后的字面量仍然合法（`"\"gamma"` 是合法字符串），编译通过 |
| 游戏运行 | 引擎不校验键名，空 Payload 照样能发给大厅，只是匹配不到 |

这是**内容错误**，不是数量错误，现有的计数类检查都发现不了。asm 里本来就有完整、正确的字符串，问题出在读回来的这一步，而这一步完全没有校验。

## 修复

先实测 lgc_compiler 支持哪些转义：`\\`、`\"`、`\n`、`\r`、`\t` 可用；`\xNN`、`\0`、`\'` 会报 `Unexpected symbol after '\'`；其余字节（含 0xF1 这类非 ASCII）原样写进 lgd。据此 ASM 与 LGC 共用同一套规则：

| 文件 | 改动 |
|---|---|
| `common/string_literal.py`（新增） | `escape_string` / `unescape_string` 及字面量正则 `QUOTED_LITERAL_PATTERN`，只处理上面 5 种转义；遇到不支持的转义直接抛错，不猜 |
| `renderer_asm.py` | 字符串操作数用 `escape_string`，asm 中的字面量不再有歧义 |
| `asm_parser.py` | 操作数以 `"` 开头时整串按字面量解析（允许后跟 `;` 注释），反转义后作为**一个**操作数；格式不符走原有的 `error_and_stop` |
| `ast_builder.py` | `PUSH_STR` 直接用原始值，`escape_string` 转义一次；操作数个数不为 1 时报 error |
| `lgc_context.py` | 全局变量字符串初值的 `_escape_string` 改调同一函数（原来不转义换行，Windows 下写文件会变成 `\r\n`） |

原计划的第 4 条“与字节码逐条比较”没有放进反编译流程：`LgcGenerator` 只拿得到 asm 路径，硬塞字节码要改接口。改为由 asm_parser 对格式严格报错

## 另案（同次对比顺带发现，与本 bug 无关）

上面提到的 4 个模拟对不上的函数，原因各不相同，需要另行调查：

| 函数 | 现象 |
|---|---|
| `qualityName` | 原版字节为 `quality_\xF1ommon`（单字节 0xF1，不是合法 UTF-8），反编译后写成 UTF-8 的 `ñ`（0xC3 0xB1），字节变了 |
| `processRealKeyboard` | 原版函数第一句就是无条件 `return 0;`，后面的代码不可达，被反编译器丢掉。行为不变，但字节码与原版不同。`regression_main` 的 `logWaveStat`、`tutorial_00` 的 `socialSignInDialog` 等同理（此前写的“函数体丢失”不准确，已更正） |
| `getEquipedModelByProxyNumberAndType` | 少了一个空串常量和一条 `RET` |
| `createStrikeEnemyBatch` | 一段日志代码被重复输出 |

另外，0.8.0 直接反编译（不加 `--reorganize` / `--refine`）再重编译，共有 31 个函数存在非字符串差异（只比较整数常量、运算符、调用），例如 `createMonsterSafe` 等函数里的逻辑非 `!x` 变成了常量 `1`，尚未核实。用户此前那份经 `--reorganize --refine` 处理的 0.7.0 输出中，还有 `selectTemporaryWeapon` 等函数的整数常量 `370→433`、`364→427`，这在 0.8.0 直接输出中没有出现，疑似 refine 阶段的常量替换造成，也尚未核实。
