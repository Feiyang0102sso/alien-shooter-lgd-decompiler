# Legacy LGD File Documentation

> [!NOTE]
>
> This document describes the lgd format shipped with the **old PC engines** (Sigma games before 2010, with AS2C as the milestone).
>
> It is **not the same format** as the lgd produced by `lgd_generator.exe` / `lgc_compiler.exe`, and the two are incompatible. To tell them apart, this document calls the former **Legacy LGD** and the latter **New LGD**.

## Overview

TL;DR: **Legacy LGD is the compiled script exactly as it sits in memory, dumped to disk as-is.**

The only export code we have found is `Save()` in the map editor. Whether Sigma had a separate standalone compiler, we don't know; all we can say is that none has ever leaked. The format doesn't look purpose-designed either. In memory, the engine holds three things:

1. **Literal Table** (arguably better called the Stack Object Table): initial values of all variables and parameters
2. **Symbol Table**: variable names, function names and their metadata
3. **Bytecode**

Legacy LGD simply writes these three out in order. Loading reads them straight back, skipping compilation.

> [!IMPORTANT]
>
> **An lgc is never turned into an lgd file during normal loading.** Both paths end in the same three in-memory structures, and the executor only cares about memory:
>
> ```
> .lgc ──(runtime compile)──┐
>                           ├──► Literal Table + Symbol Table + Bytecode (memory) ──► executor
> .lgd ──(deserialize)──────┘
> ```
>
> The lgd is merely a "save file" of this memory state. During normal loading, the engine never writes compiled results back to disk: `Save()` has no call sites anywhere in the decompiled code.

> [!NOTE]
>
> Among the samples we have, the only official release that ships Legacy LGD is the **Russian version of Crazy Launch**. Why they did this is still unknown. Every other PC release ships plain-text `.lgc`.
>
> Its format is the same as the AS1 engine, and this document focuses on that version.
>
> The ZS1 engine reads and writes the same format, but its compiler is an upgraded one: it supports function forward declarations (`Foo();`) and adds the `ActionN` / `ScriptEventN` mapping tables. So ZS1 scripts fail to compile with the AS1 compiler; even if they did, the lgd does not store those two tables, so map triggers and `ScriptEventN` callbacks would be disconnected after loading.
>
> The format also varies slightly between engines; if time permits, that will be covered later.

The engine recognizes both `.lgc` and `.lgd`. When both exist, `.lgc` is loaded first.

## Part 1: Literal Table

### 1. Format

Every variable, array element, function parameter and local variable takes one entry.

The format is `Flag | Value`. If uninitialized, only the Flag is stored.

Compared with New LGD, there are no `Size` and `ID` fields, very simple. Array lengths and ownership are all recorded by the Symbol Table in Part 2.

| **Offset** | **Field** | **Length** | **Description** |
| --- | --- | --- | --- |
| `0` | **Flag** | 1 byte | Type / status bits |
| `1` | **Value** | 0 / 4 / n+1 bytes | Present only when initialized. 4 bytes for int; for string, XOR 0x17 terminated by `00` |

### 2. Examples

#### extern func

```c++
extern MessageText(string text, int x, int y, int fontNvid = -1) 65;
```

```c++
01                      // para string text
42                      // para int x
42                      // para int y
0A FF FF FF FF          // para int fontNvid = -1
```

#### int array

```c++
int partArray[4] = { 1, 2 };
```

```c++
0E 01 00 00 00          // partArray[0] = 1
0E 02 00 00 00          // partArray[1] = 2
46                      // partArray[2]
46                      // partArray[3]
```

#### str array

```c++
string strArrayInit[3] = "x";
// AS1-only syntax: initializes the whole array with a scalar; other versions reject it
```

```c++
05                      // strArrayInit[0]
05                      // strArrayInit[1]
0D 6F 00                // strArrayInit[2] = "x"
```

### 3. Flag Bits

Compared with the Old Version flags of New LGD:

1. **No `0x80` base bit.** Only from AS2-Addon and ZS2 onward does the lgd keep `0x80`.
2. **Uninitialized strings have no `0x40`.** Uninitialized ints do have it. Starting with the original AS2, uninitialized strings carry `0x40` as well.

## Part 2: Symbol Table

Follows right after the Literal Table. The first 4 bytes are the symbol count, followed by entries made of a **plain-text name** + a **fixed-size attribute block**.

> [!IMPORTANT]
>
> Unlike New LGD, Legacy LGD **does not encrypt symbol names**: they are plain ASCII + `00`.

### 1. Type Values

| Type | Meaning |
| --- | --- |
| `1` | Global variable |
| `2` | extern function |
| `3` | Script function |
| `4` | goto label (defined) |
| `5` | goto label (referenced but not yet defined; compile-time intermediate state) |

### 2. 20-Byte Attribute Block + Text Area

| **Offset** | **Length** | **Field** | **Description** |
| --- | --- | --- | --- |
| — | n+1 | **Name** | Plain text, `00`-terminated |
| `+0` | 1 | **Type** | See table above |
| `+1` | 3 | Padding | Uninitialized memory leftovers in the samples, **garbage** |
| `+4` | 4 | `def_str` pointer | Pointer value of an in-memory `STRING` object (mostly `80 75 41 00` in the samples), **garbage** |
| `+8` | 4 | **V0** | Type 1: **start index** of the variable in the Literal Table<br/>Type 2: **extern ID**<br/>Type 3: **entry offset** of the function within the bytecode |
| `+12` | 4 | **V1** | Type 2 / 3: **start index** of the parameters in the Literal Table<br/>Type 1: meaningless pointer value in the samples (e.g. `A0 38 40 00`) |
| `+16` | 4 | **V2** | Type 1: array length (1 for a scalar)<br/>Type 2 / 3: parameter count |

After all symbol entries comes a **text area**: `symbol_count` `00`-terminated strings, one `def_str` per symbol, usually just `00`.

### 3. Examples

#### extern func

```c++
extern MessageText(string text, int x, int y, int fontNvid = -1) 65;
```

```c++
4D 65 73 73 61 67 65 54 65 78 74 00         // MessageText
   02                                       // Type 2: extern function
   00 00 00                                 // padding (memory leftovers)
   DC 2C E0 00                              // def_str dangling pointer (garbage)
   41 00 00 00                              // V0 extern ID 65 (opcode 0x41 in bytecode)
   00 00 00 00                              // V1 parameter stack start [0]
   04 00 00 00                              // V2 parameter count 4
```

#### func

```c++
ScriptEvent1(int a, int b, int c)
{
    gval = a + b + c;
}
```

```c++
53 63 72 69 70 74 45 76 65 6E 74 31 00      // ScriptEvent1
   03                                       // Type 3: script function
   00 00 00                                 // padding (memory leftovers)
   DC 2C E0 00                              // def_str dangling pointer (garbage)
   35 00 00 00                              // V0 bytecode entry +0x035
   2D 00 00 00                              // V1 parameter stack start [45]
   03 00 00 00                              // V2 parameter count 3
```

#### array

```c++
int intArray[3] = { 114, 514, 19198 };
```

```c++
69 6E 74 41 72 72 61 79 00                  // intArray
   01                                       // Type 1: global variable
   00 00 00                                 // padding (memory leftovers)
   DC 2C E0 00                              // def_str dangling pointer (garbage)
   0F 00 00 00                              // V0 stack start [15]
   E8 EB D8 00                              // V1 garbage
   03 00 00 00                              // V2 element count 3
```

## Part 3: Bytecode

**Entirely plain, no encryption**; strings inside `PUSH_STR` are plain text too.

Opcodes and operands are more or less the same as New LGD, but they differ between engines. More on that later.
