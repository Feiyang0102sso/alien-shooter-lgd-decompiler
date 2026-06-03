## 输入

\main_561.lgd

所有参数都勾选

## 输出

\main_561.bak.lgc

\main_561.lgc 和上一个一样 很大的文件没有拆分

\main_561\ 文件夹 包含所有拆分 不知道这玩意哪儿来的

\main_561\main_561.lgd.lgc 理应是拆分后的main入口 但里面没有任何 include

\main_561\segment_xx.lgc 拆分正确 但依然里面没有任何include，export和global var也没有 reference也没有

\main_561\core 这俩到看着正常

## log

``` txt
[2026-06-03 17:58:15.066] [DEBUG] [config.py:141] Root Path: D:\python coding\lgd_tool\dist
[2026-06-03 17:58:15.067] [DEBUG] [config.py:142] Log File Path: D:\python coding\lgd_tool\dist\LgdDecompiler.log
[2026-06-03 17:58:15.068] [INFO] [main.py:213] [PROCESSING] Starting Single File Mode: D:\A-GameCenter\alien shooter\_ASW TMP\maps\internet_test\main 580\main_580.lgd

...

[2026-06-03 17:58:23.905] [DEBUG] [reorganizer.py:187] [BACKUP] Successfully created LGC backup file: main_580.bak.lgc
[2026-06-03 17:58:23.905] [INFO] [reorganizer.py:192] [SPLITTER] Running Splitter for single file: D:\A-GameCenter\alien shooter\_ASW TMP\maps\internet_test\main 580\main_580.lgd
[2026-06-03 17:58:24.046] [DEBUG] [export_processor.py:54] Extracted 172 extern declarations
[2026-06-03 17:58:24.049] [DEBUG] [export_processor.py:179] Successfully wrote export file with include guard to: D:\A-GameCenter\alien shooter\_ASW TMP\maps\internet_test\main 580\main_580\core\export.lgc
[2026-06-03 17:58:24.056] [DEBUG] [global_var_processor.py:59] Extracted 996 global variable lines
[2026-06-03 17:58:24.061] [DEBUG] [global_var_processor.py:186] Successfully wrote global variables with include guard to: D:\A-GameCenter\alien shooter\_ASW TMP\maps\internet_test\main 580\main_580\core\global_variable.lgc
[2026-06-03 17:58:24.062] [DEBUG] [func_processor.py:239] Successfully wrote segment file with include guard to: D:\A-GameCenter\alien shooter\_ASW TMP\maps\internet_test\main 580\main_580\segment_00.lgc

```

