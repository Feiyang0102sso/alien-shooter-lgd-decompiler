## 源码

```cpp
// Такт генерации монстров
monstersCreationTact(int dummy)
{
  int category = categoryMission;
  // Стрелка на монстра которого нужно убить
  arrowToMissionMonster();

  int coorX = GetX(dummy);
  int coorY = GetY(dummy);

  // Получить уровень сложности в игре на данный момент времени
  int inGameDifficulty = getCurrentInGameDifficulty();
  // Получить начальный сдвиг в таблице количества монстров для соответствующего уровня сложности
  int shift = getMonsterQuantityDifficultyShift(inGameDifficulty);
  // Период сложности на миссии начиная со старта с 0
  int difficultyPeriod = GetRegInt(GAME_SESSION_TIME_INSECONDS, 0) / DIFFICULTY_INGAME_SHIFT_PERIOD;

  // Cписок индексов монстров которых на миссии уже достаточно
  int killMonsterOverrideCount = getEquipmentByCategory(EQUIPMENT_KILL_MONSTER_QUANTITY_COUNT, category, missionIndex);
  int killMonsterNVid = getEquipmentByCategory(EQUIPMENT_KILL_MONSTER, category, missionIndex);
  int no_monster = 0;
  int monsterIndex = UNDEFINED_INDEX;
  int i;
  for( i = 0; i <  missionMonsterTypeCount; i++)
  {
    monsterIndex = missionMonsterTypeIndex[i];
    int monsterNVid = MonsterQuantity[monsterIndex];
    no_monster = GetVidData(monsterNVid, VID_COUNT1);
    // если заданы более приоритетные значения количества монстров KillMonster синхронно на карте по периодам времени сложности
    if( (killMonsterOverrideCount > 0) && (monsterNVid == killMonsterNVid) )
    {
      if(difficultyPeriod < killMonsterOverrideCount) 
        MonsterQuantity[shift+monsterIndex] = getEquipmentByCategory(EQUIPMENT_KILL_MONSTER_QUANTITY, category, missionIndex, difficultyPeriod);
      else
        MonsterQuantity[shift+monsterIndex] = getEquipmentByCategory(EQUIPMENT_KILL_MONSTER_QUANTITY, category, missionIndex, killMonsterOverrideCount-1);
    }

    int requiredMonsterQuantity = MonsterQuantity[shift+monsterIndex];
    if(no_monster >=  requiredMonsterQuantity)
      missionMonsterTypeFull[i] = true;
    else
      missionMonsterTypeFull[i] = false;
  }

  // Суммировать вероятности рождения монстров
  int sum_p = 0;
  for( i = 0; i <  missionMonsterTypeCount; i++)
  {
    if(!missionMonsterTypeFull[i])
    {
      monsterIndex = missionMonsterTypeIndex[i];
      sum_p += MonsterQuantity[shift+monsterIndex];
    }
  }
  
  // Выбрать рождающегося монстра
  monsterIndex = UNDEFINED_INDEX;

  // Проверить не нужно ли рожать боса
  bool createBoss = false;
  int type = getEquipmentByCategory(EQUIPMENT_TYPE, category, missionIndex);
  if (type == typeBossMission)
  {
    int sessionTimeInSeconds = GetRegInt(GAME_SESSION_TIME_INSECONDS, 0);   
    int timeBeforeBoss = getEquipmentByCategory(EQUIPMENT_TIME_BEFORE_BOSS, category, missionIndex);
    int killCount = getEquipmentByCategory(EQUIPMENT_KILL_COUNT, category, missionIndex);
    if( (sessionTimeInSeconds >= timeBeforeBoss) && (killCount > bossCreated) )
    {
      // Рожаем боса если их ещё не достаточно
      createBoss = true;
      int monsterNVid = getEquipmentByCategory(EQUIPMENT_KILL_MONSTER, category, missionIndex);
      // Найти номер боса в таблице
      for( monsterIndex = 0; monsterIndex < MONSTERS_VID_COUNT; monsterIndex++)
      {
        if(monsterNVid == MonsterQuantity[monsterIndex])
          break;
      }

      // Номер боса не найден - ошибочная ситуация
      if(monsterIndex == MONSTERS_VID_COUNT)
      {
        Log("!WARNING! ERROR: No boss nvid in MonsterQuantity table! Boss nvid = " + itoa(monsterNVid));
        return;
      }
    }
  }

  // Если не боса то выбираем обычного монстра
  if(!createBoss)
  {
    int randomValue = Random(sum_p);
    for( i = 0; i <  missionMonsterTypeCount; i++)
    {
      if(!missionMonsterTypeFull[i])
      {
        monsterIndex = missionMonsterTypeIndex[i];
        if( (randomValue -= MonsterQuantity[shift+monsterIndex]) < 0 )
          break;
      }
    }

    // Если юнитов уже максимальное количество
    if( i >= missionMonsterTypeCount )
      return;

    // Проверить что количество монстров такого типа не превысило лимит
    no_monster = GetVidData(MonsterQuantity[monsterIndex], VID_COUNT1);
    if(no_monster >=  MonsterQuantity[shift+monsterIndex])
      return;
  }

  // Выбор места для рождения
  int deltaX = 0;
  int deltaY = 0;
  int maxAttemps = 10;
  int attemps = 0;
  do
  {
    // Защита от возможности бесконечного цикла
    attemps++;
    if(attemps == maxAttemps)
      return;

    int x = Random(3);
    if     ( x==0 ) deltaX = -50;
    else if( x==1 ) deltaX =  50;
    else if( x==2 ) deltaY = -50;
    else            deltaY =  50;
  } 
  while( CanPlace(MonsterQuantity[monsterIndex], coorX+deltaX, coorY+deltaY, 0) );

  // Увеличить счётчик созданных босов
  if(createBoss)
  {
    bossCreated++;
  }

  // Создать монстра
  int unit = CreateSprite(MonsterQuantity[monsterIndex], coorX+deltaX, coorY+deltaY, 0);
  // Монстр атакует героя
  Action( unit, ACT_ATTACK, Flagman(0), 0);
}

```

## 测试样本

| 项 | 值 |
|---|---|
| 文件 | `tests/fixtures/default.lgd` |
| 函数 | `monstersCreationTact` |
| 说明 | 项目内 fixture，生存模式通用脚本 |

---

## 反编译（修复前）

``` cpp
monstersCreationTact(int monstersCreationTact_arg0)
{
    int monstersCreationTact_local0;
    int monstersCreationTact_local1;
    int monstersCreationTact_local2;
    int monstersCreationTact_local3;
    int monstersCreationTact_local4;
    int monstersCreationTact_local5;
    int monstersCreationTact_local6;
    int monstersCreationTact_local7;
    int monstersCreationTact_local8;
    int monstersCreationTact_local9;
    int monstersCreationTact_local10;
    int monstersCreationTact_local11;
    int monstersCreationTact_local12;
    int monstersCreationTact_local13;
    int monstersCreationTact_local14;
    int monstersCreationTact_local15;
    int monstersCreationTact_local16;
    int monstersCreationTact_local17;
    int monstersCreationTact_local18;
    int monstersCreationTact_local19;
    int monstersCreationTact_local20;
    int monstersCreationTact_local21;
    int monstersCreationTact_local22;
    int monstersCreationTact_local23;
    int monstersCreationTact_local24;
    int monstersCreationTact_local25;
    int monstersCreationTact_local26;

    monstersCreationTact_local0 = 15;
    // --- Line 417 ---
    // --- Line 418 ---
    arrowToMissionMonster();
    // --- Line 420 ---
    monstersCreationTact_local1 = GetX(monstersCreationTact_arg0);
    // --- Line 421 ---
    // --- Line 422 ---
    monstersCreationTact_local2 = GetY(monstersCreationTact_arg0);
    // --- Line 422 ---
    // --- Line 423 ---
    monstersCreationTact_local3 = getCurrentInGameDifficulty();
    // --- Line 425 ---
    // --- Line 426 ---
    monstersCreationTact_local4 = getMonsterQuantityDifficultyShift(monstersCreationTact_local3);
    // --- Line 427 ---
    // --- Line 428 ---
    monstersCreationTact_local5 = (GetRegInt("scrambled.game.session.seconds", 0) / 60);
    // --- Line 429 ---
    // --- Line 430 ---
    monstersCreationTact_local6 = getEquipmentByCategory(114, monstersCreationTact_local0, missionIndex, -999999);
    // --- Line 432 ---
    // --- Line 433 ---
    monstersCreationTact_local7 = getEquipmentByCategory(78, monstersCreationTact_local0, missionIndex, -999999);
    // --- Line 433 ---
    // --- Line 434 ---
    monstersCreationTact_local8 = 0;
    // --- Line 434 ---
    // --- Line 435 ---
    monstersCreationTact_local9 = -1;
    // --- Line 435 ---
    // --- Line 436 ---
    // --- Line 437 ---
    for (monstersCreationTact_local10 = 0; (monstersCreationTact_local10 < missionMonsterTypeCount); (monstersCreationTact_local10++)) {
        monstersCreationTact_local9 = missionMonsterTypeIndex[monstersCreationTact_local10];
        // --- Line 440 ---
        monstersCreationTact_local11 = MonsterQuantity[monstersCreationTact_local9];
        // --- Line 440 ---
        // --- Line 441 ---
        monstersCreationTact_local8 = GetVidData(monstersCreationTact_local11, 35);
        // --- Line 442 ---
        if (((monstersCreationTact_local6 > 0) && (monstersCreationTact_local11 == monstersCreationTact_local7))) {
        if ((monstersCreationTact_local5 < monstersCreationTact_local6)) {
        MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)] = getEquipmentByCategory(115, monstersCreationTact_local0, missionIndex, monstersCreationTact_local5);
        // --- Line 447 ---
        } else {
        MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)] = getEquipmentByCategory(115, monstersCreationTact_local0, missionIndex, (monstersCreationTact_local6 - 1));
        // --- Line 449 ---
        }
        }
        monstersCreationTact_local12 = MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)];
        // --- Line 451 ---
        // --- Line 452 ---
        if ((monstersCreationTact_local8 >= monstersCreationTact_local12)) {
        missionMonsterTypeFull[monstersCreationTact_local10] = 1;
        // --- Line 454 ---
        } else {
        missionMonsterTypeFull[monstersCreationTact_local10] = 0;
        // --- Line 456 ---
        }
    }
    monstersCreationTact_local13 = 0;
    // --- Line 459 ---
    // --- Line 460 ---
    for (monstersCreationTact_local10 = 0; (monstersCreationTact_local10 < missionMonsterTypeCount); (monstersCreationTact_local10++)) {
        if ((!missionMonsterTypeFull[monstersCreationTact_local10])) {
        monstersCreationTact_local9 = missionMonsterTypeIndex[monstersCreationTact_local10];
        // --- Line 465 ---
        monstersCreationTact_local13 += MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)];
        // --- Line 466 ---
        }
    }
    monstersCreationTact_local9 = -1;
    // --- Line 471 ---
    monstersCreationTact_local14 = 0;
    // --- Line 473 ---
    // --- Line 474 ---
    monstersCreationTact_local15 = getEquipmentByCategory(42, monstersCreationTact_local0, missionIndex, -999999);
    // --- Line 474 ---
    // --- Line 475 ---
    if ((monstersCreationTact_local15 == 33)) {
        monstersCreationTact_local16 = GetRegInt("scrambled.game.session.seconds", 0);
        // --- Line 477 ---
        // --- Line 478 ---
        monstersCreationTact_local17 = getEquipmentByCategory(81, monstersCreationTact_local0, missionIndex, -999999);
        // --- Line 478 ---
        // --- Line 479 ---
        monstersCreationTact_local18 = getEquipmentByCategory(69, monstersCreationTact_local0, missionIndex, -999999);
        // --- Line 479 ---
        // --- Line 480 ---
        if (((monstersCreationTact_local16 >= monstersCreationTact_local17) && (monstersCreationTact_local18 > bossCreated))) {
            monstersCreationTact_local14 = 1;
            // --- Line 484 ---
            monstersCreationTact_local19 = getEquipmentByCategory(78, monstersCreationTact_local0, missionIndex, -999999);
            // --- Line 484 ---
            // --- Line 485 ---
            for (monstersCreationTact_local9 = 0; (monstersCreationTact_local9 < MONSTERS_VID_COUNT); (monstersCreationTact_local9++)) {
                if ((monstersCreationTact_local19 == MonsterQuantity[monstersCreationTact_local9])) {
                break;
                }
            }
            if ((monstersCreationTact_local9 == MONSTERS_VID_COUNT)) {
                Log(("!WARNING! ERROR: No boss nvid in MonsterQuantity table! Boss nvid = " + itoa(monstersCreationTact_local19)));
                // --- Line 496 ---
                return;
                // --- Line 497 ---
            }
        }
    }
    if ((!monstersCreationTact_local14)) {
        monstersCreationTact_local20 = Random(monstersCreationTact_local13);
        // --- Line 504 ---
        // --- Line 505 ---
        for (monstersCreationTact_local10 = 0; (monstersCreationTact_local10 < missionMonsterTypeCount); (monstersCreationTact_local10++)) {
            if ((!missionMonsterTypeFull[monstersCreationTact_local10])) {
            monstersCreationTact_local9 = missionMonsterTypeIndex[monstersCreationTact_local10];
            // --- Line 510 ---
            if (((monstersCreationTact_local20 -= MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)]) < 0)) {
            break;
            }
            }
        }
        if ((monstersCreationTact_local10 >= missionMonsterTypeCount)) {
            return;
            // --- Line 518 ---
        }
        monstersCreationTact_local8 = GetVidData(MonsterQuantity[monstersCreationTact_local9], 35);
        // --- Line 521 ---
        if ((monstersCreationTact_local8 >= MonsterQuantity[(monstersCreationTact_local4 + monstersCreationTact_local9)])) {
            return;
            // --- Line 523 ---
        }
    }
    monstersCreationTact_local21 = 0;
    // --- Line 526 ---
    // --- Line 527 ---
    monstersCreationTact_local22 = 0;
    // --- Line 527 ---
    // --- Line 528 ---
    monstersCreationTact_local23 = 10;
    // --- Line 528 ---
    // --- Line 529 ---
    monstersCreationTact_local24 = 0;
    // --- Line 529 ---
    // --- Line 530 ---
    while (1) {
        (monstersCreationTact_local24++);
        // --- Line 534 ---
        if ((monstersCreationTact_local24 == monstersCreationTact_local23)) {
            break;
        }
        monstersCreationTact_local25 = Random(3);
        // --- Line 537 ---
        // --- Line 538 ---
        if ((monstersCreationTact_local25 == 0)) {
            monstersCreationTact_local21 = -50;
            // --- Line 539 ---
        } else if ((monstersCreationTact_local25 == 1)) {
            monstersCreationTact_local21 = 50;
            // --- Line 540 ---
        } else if ((monstersCreationTact_local25 == 2)) {
            monstersCreationTact_local22 = -50;
            // --- Line 541 ---
        } else {
            monstersCreationTact_local22 = 50;
            // --- Line 542 ---
        }
        // --- Line 544 ---
        if ((!CanPlace(MonsterQuantity[monstersCreationTact_local9], (monstersCreationTact_local1 + monstersCreationTact_local21), (monstersCreationTact_local2 + monstersCreationTact_local22), 0))) {
            break;
        }
    }
    return;
    // --- Line 536 ---
}
```

---

## 反编译（修复后）

对 `tests/fixtures/default.lgd` 重新反编译，`monstersCreationTact` 尾部已恢复刷怪逻辑：

```cpp
    while (1) {
        (monstersCreationTact_local24++);
        // --- Line 534 ---
        if ((monstersCreationTact_local24 == monstersCreationTact_local23)) {
            return;
            // --- Line 536 ---
        }
        monstersCreationTact_local25 = Random(3);
        // ... deltaX / deltaY ...
        if ((!CanPlace(MonsterQuantity[monstersCreationTact_local9], ...))) {
            break;
        }
    }
    if (monstersCreationTact_local14) {
        (bossCreated++);
        // --- Line 549 ---
    }
    monstersCreationTact_local26 = CreateSprite(MonsterQuantity[monstersCreationTact_local9], ...);
    // --- Line 552 ---
    Action(monstersCreationTact_local26, 32, Flagman(0), 0);
    // --- Line 555 ---
}
```

---

## 根因分析

### 现象

修复前，反编译输出在 do-while（被改写为 `while(1) + break`）结束后直接 `return`，丢失了源码 **135–144 行** 的全部逻辑：

- `if (createBoss) bossCreated++;`
- `CreateSprite(...)`
- `Action(unit, ACT_ATTACK, Flagman(0), 0)`

`monstersCreationTact_local26` 已声明但从未赋值，对应源码里的 `unit`。

函数前半段（统计怪物类型、Boss 分支、加权随机选怪）与源码一致，**问题出在 do-while 出口之后的 CFG 结构化**，而非字节码缺失。

---

### 字节码验证（`tests/fixtures/default.lgd`）

对 fixture 跑 pipeline 生成的 asm 中，`monstersCreationTact` 尾部**完整包含**刷怪指令：

```
loc_B3BF7:  CanPlace(...)
            JMP_FALSE    loc_B3B47          ; 可放置 → 回跳
loc_B3C29:  PUSH createBoss
            JMP_FALSE    loc_B3C3D
loc_B3C33:  POST_INC     bossCreated
loc_B3C3D:  CALL_EXT_65                     ; CreateSprite
            ASSIGN       monstersCreationTact_local26
            CALL_EXT_79                     ; Action
            RET
```

结论：**二进制里有 CreateSprite / Action，是反编译器结构化阶段丢代码，不是 .lgd 编译产物缺指令。**

---

### 源码 CFG 结构（关键）

`monstersCreationTact` 末尾的 do-while 有**两种不同语义的出口**：

```
┌─ do-while body ─────────────────────────────┐
│  attemps++                                  │
│  if (attemps == maxAttemps)  ──return──► [A]  ← 出口 A：提前 return，不刷怪
│  Random(3) → deltaX/deltaY                  │
└─────────────────────────────────────────────┘
         │ while (CanPlace(...))  ← CanPlace 为 true 时继续
         ▼ CanPlace 为 false（找到位置）
    [B] createBoss 判断                          ← 出口 B：正常 post-loop 入口
      if (createBoss) bossCreated++
      unit = CreateSprite(...)
      Action(unit, ACT_ATTACK, ...)
      return
```

- **出口 A**：循环体内的 `return`，语义是「超次数放弃刷怪」
- **出口 B**：CanPlace latch 的自然落点，语义是「找到位置，继续刷怪」

两者都不能丢。

---

### CFG 基本块映射（fixture 反汇编）

| 块 ID | 偏移 | 角色 | 内容 |
|------|------|------|------|
| 44 | `B3B47` | loop header | `attemps++`，`attemps==max` 分支 |
| 45 | `B3B61` | **出口 A** | 纯 `RET`（提前 return） |
| 53 | `B3BF7` | CanPlace latch | 条件为真 → 44；为假 → 54 |
| 54 | `B3C29` | **出口 B 入口** | `if (createBoss)` |
| 55 | `B3C33` | post-loop | `bossCreated++` |
| 56 | `B3C3D` | post-loop | `CreateSprite` + `Action` + `RET` |

循环体：`{44, 46, 47, 48, 49, 50, 51, 52, 53}`

循环外后继：`{45, 54}`，两者均为 **terminal exit**（不是 trampoline）。

---

### 反编译器实际做了什么

涉及文件：`src/lgd_tool/lgd_decompiler/generate_LGC/flow_structurer.py`

#### 步骤 1：do-while → `while(1) + break`

header 块 44 含 `attemps++` 副作用，走 `while(1)+break` 路径（非纯条件 while）。

#### 步骤 2：收集循环外后继

```
outside_successors = {45, 54}
terminal_exits     = {45, 54}
post_loop_blocks   = {}        ← 旧逻辑为空
```

#### 步骤 3：`_pick_loop_exit_block()` 误选 block 45

旧逻辑在 `post_loop_blocks` 为空时，从 `terminal_exits` 按**物理地址最小**选取：

- block 45 @ `0xB3B61` — 纯 `RET`（出口 A）
- block 54 @ `0xB3C29` — post-loop 入口（出口 B）

**选中了 block 45** → `while(1)` 结束后从这里继续结构化 → 输出只有一个 `return` → block 54–56 全部被跳过。

#### 为什么旧版 `_find_side_effect_post_loop_blocks()` 没识别 block 54？

旧实现只认 **trampoline**（`outside_successors - terminal_exits`）。本案例中 block 54 **已在 `terminal_exits` 内**（其后继 55/56 不在 `{45,54}` 集合里），不是 trampoline，因此检测不到 post-loop。

这与「POST_LOOP 被 `_resolve_terminal_loop_exits` 当跳板排除」的**旧文档推断不同**；真实根因是 **两个 terminal 并存时，按地址误选了纯 RET 的 early-exit 块**。

---

### 次要问题：循环内 `return` 被降级为 `break`

| 场景 | 源码 | 修复前 | 修复后 |
|------|------|--------|--------|
| 10 次仍找不到位置 | `return`（不刷怪） | `break` → 落到 `return`（碰巧不刷怪） | `return` |
| 找到位置 | 继续 post-loop | post-loop 丢失 | `break` → post-loop 正常执行 |

修复 post-loop 丢失后，`attemps==max` 必须输出 `return` 而非 `break`，否则超次数路径会误执行刷怪。

---

### 为什么 `generateCameraMonsters` 没中招

同文件 `generateCameraMonsters` 也有 `CanPlace` + `while(1) + break` + `CreateSprite`，但能正常输出，因为：

- post-loop 的 `CreateSprite` 之后还有外层 `while` 回跳等逻辑
- 循环外 terminal 集合中，**最低地址的 terminal 不是纯 RET early-exit**，或未触发「双 terminal + 纯 RET 误选」组合

`monstersCreationTact` 恰好同时满足：纯 RET 的 early-exit（45）地址低于 post-loop 入口（54）。

---

### 影响范围

任何符合以下模式的函数都可能中招：

```
do {
    ...
    if (guard) return;          // 循环内提前 return → 纯 RET terminal，地址往往靠前
} while (condition);            // latch 自然出口 → post-loop terminal，地址靠后

if (flag) side_effect();
CreateSprite(...);
return;
```

生存模式所有地图刷怪点都走 `monstersCreationTact`，反编译丢失刷怪逻辑后表现为**全图不刷怪**。

---

## 修复（flow_structurer.py）

### 改动摘要

1. **`_find_side_effect_post_loop_blocks()`**  
   除 trampoline 外，增加识别 **latch 的自然 terminal 出口**：CanPlace latch 的循环外后继若在 `terminal_exits` 中且**非纯 RET**，视为 post-loop（block 54）。

2. **`_pick_loop_exit_block()`**  
   - 优先从 `post_loop_blocks` 继续结构化  
   - 多个 terminal 并存时，**跳过纯 RET 块**，避免误选 early-exit（block 45）

3. **辅助方法**  
   - `_is_pure_return_block()`：判断块是否仅含 `RET`  
   - `_block_has_side_effects()`：语句/指令层侧效检测

4. **循环内分支（已有逻辑，配合 post-loop 生效）**  
   - 目标为 post-loop → `break`  
   - 目标为 early-exit 且存在 post-loop → `return`（`attemps==max`）  
   - 其余 → `break`

5. **回归测试**  
   `tests/unit/lgd_decompiler/generate_LGC/test_flow_structurer_post_loop.py`  
   - `test_terminal_post_loop_not_pure_ret_early_exit`：模拟 fixture 双 terminal 形态

### 验证

对 `tests/fixtures/default.lgd` 跑完整 pipeline：

- `CreateSprite` / `Action` / `bossCreated++` 均出现在 `monstersCreationTact` 尾部
- `attemps == maxAttemps` 路径输出 `return` 而非 `break`
- 32 项 unit + regression 测试通过

