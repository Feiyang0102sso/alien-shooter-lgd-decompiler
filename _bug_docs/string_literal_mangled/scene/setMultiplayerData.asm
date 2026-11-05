;Function setMultiplayerData() Begin
  17A008:  02 33 31 00        PUSH_STR     "31"
  17A00C:  26 D0 55 00 00     ASSIGN       setMultiplayerData_local0
  17A011:  19 01 08 00 00     LINE_NUM     2049              ; Code Line 2049
  17A016:  19 02 08 00 00     LINE_NUM     2050              ; Code Line 2050
  17A01B:  02 77 73 73 3A 2F  PUSH_STR     "wss://asgoldlobby.sigma-team.net/"
        2F 61 73 67 6F 6C
        64 6C 6F 62 62 79
        2E 73 69 67 6D 61
        2D 74 65 61 6D 2E
        6E 65 74 2F 00
  17A03E:  26 8C 1D 00 00     ASSIGN       multiplayerAddPossibleServerUrl_arg0
  17A043:  1A                 ARG_COMMIT   
  17A044:  1E 99 06 00 00     CALL_FUNC    multiplayerAddPossibleServerUrl
  17A049:  19 0D 08 00 00     LINE_NUM     2061              ; Code Line 2061
  17A04E:  02 77 73 73 3A 2F  PUSH_STR     "wss://asgoldlobby1.sigma-team.net/"
        2F 61 73 67 6F 6C
        64 6C 6F 62 62 79
        31 2E 73 69 67 6D
        61 2D 74 65 61 6D
        2E 6E 65 74 2F 00
  17A072:  26 8C 1D 00 00     ASSIGN       multiplayerAddPossibleServerUrl_arg0
  17A077:  1A                 ARG_COMMIT   
  17A078:  1E 99 06 00 00     CALL_FUNC    multiplayerAddPossibleServerUrl
  17A07D:  19 0E 08 00 00     LINE_NUM     2062              ; Code Line 2062
  17A082:  02 6E 65 74 2E 73  PUSH_STR     "net.sigma-team.asfree"
        69 67 6D 61 2D 74
        65 61 6D 2E 61 73
        66 72 65 65 00
  17A099:  26 26 1D 00 00     ASSIGN       multiplayerInitialize_arg0
  17A09E:  1A                 ARG_COMMIT   
  17A09F:  24 D0 55 00 00     PUSH_VAR     setMultiplayerData_local0
  17A0A4:  26 27 1D 00 00     ASSIGN       multiplayerInitialize_arg1
  17A0A9:  1A                 ARG_COMMIT   
  17A0AA:  1E 2E 06 00 00     CALL_FUNC    multiplayerInitialize
  17A0AF:  19 11 08 00 00     LINE_NUM     2065              ; Code Line 2065
  17A0B4:  02 67 61 6D 6D 61  PUSH_STR     "gamma;missionName;gameMode;mode;map;level;checkpoints;number;pvpSide;rating;disableBanOnLeave;"
        3B 6D 69 73 73 69
        6F 6E 4E 61 6D 65
        3B 67 61 6D 65 4D
        6F 64 65 3B 6D 6F
        64 65 3B 6D 61 70
        3B 6C 65 76 65 6C
        3B 63 68 65 63 6B
        70 6F 69 6E 74 73
        3B 6E 75 6D 62 65
        72 3B 70 76 70 53
        69 64 65 3B 72 61
        74 69 6E 67 3B 64
        69 73 61 62 6C 65
        42 61 6E 4F 6E 4C
        65 61 76 65 3B 00
  17A114:  26 D1 55 00 00     ASSIGN       setMultiplayerData_local1
  17A119:  19 12 08 00 00     LINE_NUM     2066              ; Code Line 2066
  17A11E:  19 13 08 00 00     LINE_NUM     2067              ; Code Line 2067
  17A123:  24 D1 55 00 00     PUSH_VAR     setMultiplayerData_local1
  17A128:  26 4C 1D 00 00     ASSIGN       multiplayerSetRoomPayloadKeys_arg0
  17A12D:  1A                 ARG_COMMIT   
  17A12E:  1E 59 06 00 00     CALL_FUNC    multiplayerSetRoomPayloadKeys
  17A133:  19 14 08 00 00     LINE_NUM     2068              ; Code Line 2068
  17A138:  02 6C 69 67 68 74  PUSH_STR     "light;banner;title;title_level;clan;rating;rank;gameTime;enemiesKilled;compleatedMissions;runplatform;protocolVersion;team;"
        3B 62 61 6E 6E 65
        72 3B 74 69 74 6C
        65 3B 74 69 74 6C
        65 5F 6C 65 76 65
        6C 3B 63 6C 61 6E
        3B 72 61 74 69 6E
        67 3B 72 61 6E 6B
        3B 67 61 6D 65 54
        69 6D 65 3B 65 6E
        65 6D 69 65 73 4B
        69 6C 6C 65 64 3B
        63 6F 6D 70 6C 65
        61 74 65 64 4D 69
        73 73 69 6F 6E 73
        3B 72 75 6E 70 6C
        61 74 66 6F 72 6D
        3B 70 72 6F 74 6F
        63 6F 6C 56 65 72
        73 69 6F 6E 3B 74
        65 61 6D 3B 00
  17A1B5:  1E F7 0A 00 00     CALL_FUNC    getVIPZombieAddonKey
  17A1BA:  08                 ADD          
  17A1BB:  02 3B 00           PUSH_STR     ";"
  17A1BE:  08                 ADD          
  17A1BF:  02 67 61 6D 65 5F  PUSH_STR     "game_width"
        77 69 64 74 68 00
  17A1CB:  08                 ADD          
  17A1CC:  02 3B 00           PUSH_STR     ";"
  17A1CF:  08                 ADD          
  17A1D0:  02 67 61 6D 65 5F  PUSH_STR     "game_height"
        68 65 69 67 68 74
        00
  17A1DD:  08                 ADD          
  17A1DE:  02 3B 00           PUSH_STR     ";"
  17A1E1:  08                 ADD          
  17A1E2:  26 D2 55 00 00     ASSIGN       setMultiplayerData_local2
  17A1E7:  19 14 08 00 00     LINE_NUM     2068              ; Code Line 2068
  17A1EC:  19 15 08 00 00     LINE_NUM     2069              ; Code Line 2069
  17A1F1:  1E F9 0E 00 00     CALL_FUNC    isSteam
  17A1F6:  18 23 00 00 00     JMP_FALSE    loc_17A21A        ; Rel: +0x23
  17A1FB:  02 69 64 48 69 50  PUSH_STR     "idHiPart;idLoPart;"
        61 72 74 3B 69 64
        4C 6F 50 61 72 74
        3B 00
  17A20F:  27 D2 55 00 00 08  OP_ASSIGN    setMultiplayerData_local2, +=
  17A215:  19 17 08 00 00     LINE_NUM     2071              ; Code Line 2071
loc_17A21A:
  17A21A:  24 D2 55 00 00     PUSH_VAR     setMultiplayerData_local2
  17A21F:  26 4D 1D 00 00     ASSIGN       multiplayerSetPlayerPayloadKeys_arg0
  17A224:  1A                 ARG_COMMIT   
  17A225:  1E 5A 06 00 00     CALL_FUNC    multiplayerSetPlayerPayloadKeys
  17A22A:  19 18 08 00 00     LINE_NUM     2072              ; Code Line 2072
  17A22F:  02 73 74 6F 72 65  PUSH_STR     "store_equiped;"
        5F 65 71 75 69 70
        65 64 3B 00
  17A23F:  26 4E 1D 00 00     ASSIGN       multiplayerSetSessionDataKeys_arg0
  17A244:  1A                 ARG_COMMIT   
  17A245:  1E 5B 06 00 00     CALL_FUNC    multiplayerSetSessionDataKeys
  17A24A:  19 19 08 00 00     LINE_NUM     2073              ; Code Line 2073
  17A24F:  02 6E 69 67 68 74  PUSH_STR     "nightfall"
        66 61 6C 6C 00
  17A25A:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A25F:  1A                 ARG_COMMIT   
  17A260:  01 FF FF FF FF     PUSH_INT     -1
  17A265:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A26A:  1A                 ARG_COMMIT   
  17A26B:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A270:  19 1C 08 00 00     LINE_NUM     2076              ; Code Line 2076
  17A275:  02 67 72 61 6E 64  PUSH_STR     "grand_master"
        5F 6D 61 73 74 65
        72 00
  17A283:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A288:  1A                 ARG_COMMIT   
  17A289:  01 FF FF FF FF     PUSH_INT     -1
  17A28E:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A293:  1A                 ARG_COMMIT   
  17A294:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A299:  19 1D 08 00 00     LINE_NUM     2077              ; Code Line 2077
  17A29E:  02 73 69 64 65 5F  PUSH_STR     "side_mission_type"
        6D 69 73 73 69 6F
        6E 5F 74 79 70 65
        00
  17A2B1:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A2B6:  1A                 ARG_COMMIT   
  17A2B7:  01 FF FF FF FF     PUSH_INT     -1
  17A2BC:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A2C1:  1A                 ARG_COMMIT   
  17A2C2:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A2C7:  19 1E 08 00 00     LINE_NUM     2078              ; Code Line 2078
  17A2CC:  02 6D 61 70 5F 30  PUSH_STR     "map_0_strike"
        5F 73 74 72 69 6B
        65 00
  17A2DA:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A2DF:  1A                 ARG_COMMIT   
  17A2E0:  01 FF FF FF FF     PUSH_INT     -1
  17A2E5:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A2EA:  1A                 ARG_COMMIT   
  17A2EB:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A2F0:  19 1F 08 00 00     LINE_NUM     2079              ; Code Line 2079
  17A2F5:  02 6D 61 70 5F 31  PUSH_STR     "map_1_strike"
        5F 73 74 72 69 6B
        65 00
  17A303:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A308:  1A                 ARG_COMMIT   
  17A309:  01 FF FF FF FF     PUSH_INT     -1
  17A30E:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A313:  1A                 ARG_COMMIT   
  17A314:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A319:  19 20 08 00 00     LINE_NUM     2080              ; Code Line 2080
  17A31E:  02 6D 61 70 5F 32  PUSH_STR     "map_2_strike"
        5F 73 74 72 69 6B
        65 00
  17A32C:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A331:  1A                 ARG_COMMIT   
  17A332:  01 FF FF FF FF     PUSH_INT     -1
  17A337:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A33C:  1A                 ARG_COMMIT   
  17A33D:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A342:  19 21 08 00 00     LINE_NUM     2081              ; Code Line 2081
  17A347:  02 77 65 65 6B 6C  PUSH_STR     "weekly_reset"
        79 5F 72 65 73 65
        74 00
  17A355:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A35A:  1A                 ARG_COMMIT   
  17A35B:  01 FF FF FF FF     PUSH_INT     -1
  17A360:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A365:  1A                 ARG_COMMIT   
  17A366:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A36B:  19 22 08 00 00     LINE_NUM     2082              ; Code Line 2082
  17A370:  02 6D 6F 6E 74 68  PUSH_STR     "monthly_reset"
        6C 79 5F 72 65 73
        65 74 00
  17A37F:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A384:  1A                 ARG_COMMIT   
  17A385:  01 FF FF FF FF     PUSH_INT     -1
  17A38A:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A38F:  1A                 ARG_COMMIT   
  17A390:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A395:  19 23 08 00 00     LINE_NUM     2083              ; Code Line 2083
  17A39A:  02 73 68 6F 70 5F  PUSH_STR     "shop_sale"
        73 61 6C 65 00
  17A3A5:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A3AA:  1A                 ARG_COMMIT   
  17A3AB:  01 FF FF FF FF     PUSH_INT     -1
  17A3B0:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A3B5:  1A                 ARG_COMMIT   
  17A3B6:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A3BB:  19 24 08 00 00     LINE_NUM     2084              ; Code Line 2084
  17A3C0:  02 6D 65 72 63 68  PUSH_STR     "merchant_sale"
        61 6E 74 5F 73 61
        6C 65 00
  17A3CF:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A3D4:  1A                 ARG_COMMIT   
  17A3D5:  01 FF FF FF FF     PUSH_INT     -1
  17A3DA:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A3DF:  1A                 ARG_COMMIT   
  17A3E0:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A3E5:  19 25 08 00 00     LINE_NUM     2085              ; Code Line 2085
  17A3EA:  02 67 61 63 68 61  PUSH_STR     "gacha_special"
        5F 73 70 65 63 69
        61 6C 00
  17A3F9:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A3FE:  1A                 ARG_COMMIT   
  17A3FF:  01 FF FF FF FF     PUSH_INT     -1
  17A404:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A409:  1A                 ARG_COMMIT   
  17A40A:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A40F:  19 26 08 00 00     LINE_NUM     2086              ; Code Line 2086
  17A414:  02 62 61 74 74 6C  PUSH_STR     "battle_pass"
        65 5F 70 61 73 73
        00
  17A421:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A426:  1A                 ARG_COMMIT   
  17A427:  01 FF FF FF FF     PUSH_INT     -1
  17A42C:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A431:  1A                 ARG_COMMIT   
  17A432:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A437:  19 27 08 00 00     LINE_NUM     2087              ; Code Line 2087
  17A43C:  02 61 72 65 6E 61  PUSH_STR     "arena_mission"
        5F 6D 69 73 73 69
        6F 6E 00
  17A44B:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A450:  1A                 ARG_COMMIT   
  17A451:  01 FF FF FF FF     PUSH_INT     -1
  17A456:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A45B:  1A                 ARG_COMMIT   
  17A45C:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A461:  19 28 08 00 00     LINE_NUM     2088              ; Code Line 2088
  17A466:  02 61 72 63 68 69  PUSH_STR     "architector_cristals"
        74 65 63 74 6F 72
        5F 63 72 69 73 74
        61 6C 73 00
  17A47C:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A481:  1A                 ARG_COMMIT   
  17A482:  01 FF FF FF FF     PUSH_INT     -1
  17A487:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A48C:  1A                 ARG_COMMIT   
  17A48D:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A492:  19 29 08 00 00     LINE_NUM     2089              ; Code Line 2089
  17A497:  02 61 72 63 68 69  PUSH_STR     "architector_second_cristals"
        74 65 63 74 6F 72
        5F 73 65 63 6F 6E
        64 5F 63 72 69 73
        74 61 6C 73 00
  17A4B4:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A4B9:  1A                 ARG_COMMIT   
  17A4BA:  01 FF FF FF FF     PUSH_INT     -1
  17A4BF:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A4C4:  1A                 ARG_COMMIT   
  17A4C5:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A4CA:  19 2A 08 00 00     LINE_NUM     2090              ; Code Line 2090
  17A4CF:  02 6C 6F 73 74 5F  PUSH_STR     "lost_sector_master"
        73 65 63 74 6F 72
        5F 6D 61 73 74 65
        72 00
  17A4E3:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A4E8:  1A                 ARG_COMMIT   
  17A4E9:  01 FF FF FF FF     PUSH_INT     -1
  17A4EE:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A4F3:  1A                 ARG_COMMIT   
  17A4F4:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A4F9:  19 2B 08 00 00     LINE_NUM     2091              ; Code Line 2091
  17A4FE:  02 6C 65 67 65 6E  PUSH_STR     "legendary_zombie"
        64 61 72 79 5F 7A
        6F 6D 62 69 65 00
  17A510:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A515:  1A                 ARG_COMMIT   
  17A516:  01 FF FF FF FF     PUSH_INT     -1
  17A51B:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A520:  1A                 ARG_COMMIT   
  17A521:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A526:  19 2C 08 00 00     LINE_NUM     2092              ; Code Line 2092
  17A52B:  02 64 75 6E 67 65  PUSH_STR     "dungeon_mods"
        6F 6E 5F 6D 6F 64
        73 00
  17A539:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A53E:  1A                 ARG_COMMIT   
  17A53F:  01 00 00 00 00     PUSH_INT     0
  17A544:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A549:  1A                 ARG_COMMIT   
  17A54A:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A54F:  19 2D 08 00 00     LINE_NUM     2093              ; Code Line 2093
  17A554:  02 64 75 6E 67 65  PUSH_STR     "dungeon_adept_weapons"
        6F 6E 5F 61 64 65
        70 74 5F 77 65 61
        70 6F 6E 73 00
  17A56B:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A570:  1A                 ARG_COMMIT   
  17A571:  01 01 00 00 00     PUSH_INT     1
  17A576:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A57B:  1A                 ARG_COMMIT   
  17A57C:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A581:  19 2E 08 00 00     LINE_NUM     2094              ; Code Line 2094
  17A586:  02 6C 6F 73 74 5F  PUSH_STR     "lost_sector_adept_weapons"
        73 65 63 74 6F 72
        5F 61 64 65 70 74
        5F 77 65 61 70 6F
        6E 73 00
  17A5A1:  26 80 1D 00 00     ASSIGN       multiplayerAddSequence_arg0
  17A5A6:  1A                 ARG_COMMIT   
  17A5A7:  01 02 00 00 00     PUSH_INT     2
  17A5AC:  26 81 1D 00 00     ASSIGN       multiplayerAddSequence_arg1
  17A5B1:  1A                 ARG_COMMIT   
  17A5B2:  1E 91 06 00 00     CALL_FUNC    multiplayerAddSequence
  17A5B7:  19 2F 08 00 00     LINE_NUM     2095              ; Code Line 2095
  17A5BC:  02 74 65 6D 70 2E  PUSH_STR     "temp.multiplayer.gathering.timeout"
        6D 75 6C 74 69 70
        6C 61 79 65 72 2E
        67 61 74 68 65 72
        69 6E 67 2E 74 69
        6D 65 6F 75 74 00
  17A5E0:  01 0E 00 00 00     PUSH_INT     14
  17A5E5:  B8                 CALL_EXT_184                   ; SetRegInt
  17A5E6:  19 32 08 00 00     LINE_NUM     2098              ; Code Line 2098
  17A5EB:  1F                 RET                            ; mark end of function
;Function setMultiplayerData() End
