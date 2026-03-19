"""
保存常量对应的在函数中出现的位置
Action 等为函数名
1 代表出现在第一个参数 2 代表第二个，以此类推
ACT,ANI等表示常量前缀
一般常量都以组展示，注入 ACT_XXX ; ANI_XXX ...
"""

EXPORT_CONST_REFINER_RULES = {
    # --- 核心动作与指令调度 ---
    "Action": {
        1: ["ACT", "ANI", "act"]       # 例: Action(unit, ACT_ADD_AMMO, ...)
    },
    "ActionByName": {                  # [NEW]
        1: ["ACT", "ANI", "act"]       # 例: ActionByName("name", ACT_DESTROY_UNIT, -1)
    },
    "MenuAction": {
        2: ["ACT", "ANI", "act"]       # 例: MenuAction(id, dir, ACT_CHANGE_DIRECTION, val)
    },
    "AddCommand": {
        1: ["ACT", "ANI", "act"]       # 例: AddCommand(item, ACT_PAUSE, ...)
    },

    # --- 实体属性读取/设置 ---
    "GetVidData": {
        1: ["VID", "SETVID"]           # 例: GetVidData(vid, VID_MAXHP)
    },
    "SetVidData": {
        1: ["VID", "SETVID"]           # 例: SetVidData(enemyNVid[i], SETVID_DAMAGE_TYPE_COLD, 1)
    },

    # --- 引擎特效与环境 ---
    "Effect": {
        0: ["EFF"]                     # 例: Effect(EFF_FADE, 0, 0, time)
    },
    "GetEffectState": {
        0: ["EFF"]                     # 例: GetEffectState(EFF_FADE)
    },
    "SetEnvironment": {
        0: ["ENV"]                     # 例: SetEnvironment(ENV_BORN_RAIN)
    },
    "SetScrollType": {
        0: ["SCROLL"]                  # 例: SetScrollType(SCROLL_NONE)
    },

    # --- UI 与 光标 ---
    "CreateText": {
        5: ["BEH"]                     # 例: CreateText(id, x, y, z, "text", BEH_CENTER_X)
    },
    "SetCursor": {                     # [NEW]
        0: ["CURSOR"]                  # 例: SetCursor(CURSOR_NORMAL)
    },

    # --- 实体查找与遍历 ---
    "FirstUnit": {
        0: ["U"]                       # 例: FirstUnit(U_UNIT)
    },
    "FindNearestSprite": {
        0: ["GETSPRITE"]               # 例: FindNearestSprite(GETSPRITE_VID_FLAG + nvid, x, y, range)
    },
    "GetSprite": {                     # [NEW]
        0: ["GETSPRITE"]               # 例: GetSprite(GETSPRITE_VID_FLAG + LOBBY_ICON_NVID, x, y)
    },

    # --- 系统与杂项 ---
    "Log": {
        1: ["LOG"]                     # 例: Log(msg, LOG_DEBUG)
    },
    "SetRegStr": {
        0: ["GENDER_REG_KEY"],
        1: ["GENDER"]
    },
    "checkGender": {
        0: ["GENDER"]
    }
}