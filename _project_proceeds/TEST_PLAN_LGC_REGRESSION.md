# LGC 回归测试计划（独立套件 · 按方法逐行比较）

> **性质**：与 `tests/unit/` 无关；工具在 `tests/utils/regression/`。  
> **输入**：`tests/fixtures/lgd_files/regression_*.lgd`  
> **基线**：`tests/fixtures/regression_lgc/regression_*.lgc`（**同目录只放 lgc**，与 lgd 同名配对）  
> **断言**：按方法逐行比较；列 diff 行；可选 `max_diff_lines`。

---

## 1. 目录结构（当前约定）

```text
tests/
  fixtures/
    lgd_files/
      tutorial_00.lgd              # unit 等其它测试用（无前缀）
      test_asm_empty.lgd
      regression_tutorial_00.lgd     # 回归专用：必须 regression_ 前缀
      regression_level_01.lgd
      ...
    regression_lgc/                # 只放基线 .lgc，不再分子目录
      regression_tutorial_00.lgc
      regression_level_01.lgc
  regression/
    lgc/
      test_lgc_regression.py
  utils/
    regression/
      paths.py
      lgc_compare.py               # 待实现
      workdir.py                   # 待实现
  output/                          # .gitignore
    regression_lgc/
      regression_tutorial_00/
        input.lgc
        on_failure/
```

**不要**再在 `regression_lgc/` 下建 `expected_lgc/`、`manifest.json`（可选）、或 `lgd/` 子目录。若仍有 `regression_lgc/lgd/*.lgd`，属误放，应删掉或移回 `lgd_files/` 并加前缀。

---

## 2. 命名配对规则

| 类型 | 位置 | 文件名 |
|------|------|--------|
| 输入 LGD | `lgd_files/` | `regression_<名>.lgd` |
| 基线 LGC | `regression_lgc/` | `regression_<名>.lgc` |

**同一对**共用同一文件名（仅扩展名不同），例如：

```text
lgd_files/regression_tutorial_00.lgd
regression_lgc/regression_tutorial_00.lgc
```

实现时**默认自动扫描**：`lgd_files/regression_*.lgd`，对每个文件要求存在 `regression_lgc/<同名>.lgc`。  
无需 `manifest.json`；若以后要加阈值，可用可选配置文件 `regression_lgc/config.json`（实现时再定）。

---

## 3. 路径常量（`tests/conftest.py`）

```python
REGRESSION_LGC_DIR = FIXTURES_DIR / "regression_lgc"
REGRESSION_LGD_PREFIX = "regression_"
REGRESSION_OUTPUT_DIR = TESTS_DIR / "output" / "regression_lgc"
```

---

## 4. 比较流程

```text
1. 枚举 lgd_files/regression_*.lgd
2. 在 output/regression_lgc/<basename>/ 跑 Pipeline(keep_intermediate=False)
3. work 内只留 input.lgc，其余全删；勿污染 lgd_files/ 旁生成 .asm/.csv
4. 读 regression_lgc/<basename>.lgc 为 expected
5. 按函数逐行 diff；超 max_diff_lines（默认 0）则 FAIL
6. 通过 → 删 work；失败 → 留 input.lgc + on_failure/
```

### 4.1 不测范围

- 文件头、extern/global 声明（只比函数块）。  
- 函数顺序（只比函数名集合）。

### 4.2 阈值（可选）

可在 `regression_lgc/config.json` 中按 **basename** 配置 `max_diff_lines`；无文件则全局默认 `0`。  
不强制 manifest；实现阶段再加即可。

---

## 5. 失败输出

```text
FAILED regression_tutorial_00 :: function OnGameStart
  line 45 (expected): ...
  line 45 (actual):   ...
work_dir: tests/output/regression_lgc/regression_tutorial_00/
```

失败磁盘：仅 `input.lgc` + `on_failure/`。

---

## 6. 基线（手动）

1. 反编译 `regression_<名>.lgd` 得到 `.lgc`。  
2. Compare 确认。  
3. 保存为 `regression_lgc/regression_<名>.lgc`（**文件名与 lgd 一致，只改扩展名**）。  
4. 新用例：在 `lgd_files/` 增加 `regression_<名>.lgd`，再拷入对应 `.lgc`。

---

## 7. 与其它测试

- **unit** 继续用无前缀的 `tutorial_00.lgd` 等。  
- **回归** 只碰 `regression_` 前缀，互不干扰。  
- `pytest tests/regression` 与 `pytest tests/unit` 分开。

---

## 8. 实现清单

- [x] 目录与命名约定（用户已整理 fixture）  
- [ ] 更新 `tests/utils/regression/paths.py`：`list_regression_pairs()`  
- [ ] `lgc_compare.py`、`workdir.py`  
- [ ] `tests/regression/lgc/test_lgc_regression.py`  
- [ ] 清理误放的 `regression_lgc/lgd/`（若仍存在）  
- [ ] 可选 `regression_lgc/config.json`（阈值）

---

## 9. 总结

| 项目 | 约定 |
|------|------|
| LGD | `lgd_files/regression_*.lgd` |
| 基线 LGC | `regression_lgc/regression_*.lgc`（**扁平，仅 lgc**） |
| 配对 | **同名**（`regression_foo.lgd` ↔ `regression_foo.lgc`） |
| 清单 | 扫描前缀，**不必** manifest |
| 工具包 | `tests/utils/regression/` |
| 运行产物 | 只留 `output/.../input.lgc` |
