;Function refreshEnemyPathDirections() Begin
  66F45:  24 92 14 00 00     PUSH_VAR     lastRefreshPathDirectionsWaveNumber
  66F4A:  24 7F 0D 00 00     PUSH_VAR     nextWaveNumber
  66F4F:  0D                 EQ           
  66F50:  18 0A 00 00 00     JMP_FALSE    loc_66F5B          ; Rel: +0xA
  66F55:  1F                 RET          
  66F56:  19 1F 00 00 00     LINE_NUM     31                 ; Code Line 31
loc_66F5B:
  66F5B:  01 A4 00 00 00     PUSH_INT     164
  66F60:  26 47 03 00 00     ASSIGN       getEquipmentByCategory_arg0
  66F65:  1A                 ARG_COMMIT   
  66F66:  01 0F 00 00 00     PUSH_INT     15
  66F6B:  26 48 03 00 00     ASSIGN       getEquipmentByCategory_arg1
  66F70:  1A                 ARG_COMMIT   
  66F71:  24 7E 0D 00 00     PUSH_VAR     missionIndex
  66F76:  26 49 03 00 00     ASSIGN       getEquipmentByCategory_arg2
  66F7B:  1A                 ARG_COMMIT   
  66F7C:  01 C1 BD F0 FF     PUSH_INT     -999999
  66F81:  26 4A 03 00 00     ASSIGN       getEquipmentByCategory_arg3
  66F86:  1A                 ARG_COMMIT   
  66F87:  1E B3 01 00 00     CALL_FUNC    getEquipmentByCategory
  66F8C:  26 93 14 00 00     ASSIGN       refreshEnemyPathDirections_local0
  66F91:  19 21 00 00 00     LINE_NUM     33                 ; Code Line 33
  66F96:  19 22 00 00 00     LINE_NUM     34                 ; Code Line 34
  66F9B:  24 7F 0D 00 00     PUSH_VAR     nextWaveNumber
  66FA0:  24 93 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local0
  66FA5:  11                 GE           
  66FA6:  18 0A 00 00 00     JMP_FALSE    loc_66FB1          ; Rel: +0xA
  66FAB:  1F                 RET          
  66FAC:  19 24 00 00 00     LINE_NUM     36                 ; Code Line 36
loc_66FB1:
  66FB1:  24 7F 0D 00 00     PUSH_VAR     nextWaveNumber
  66FB6:  26 92 14 00 00     ASSIGN       lastRefreshPathDirectionsWaveNumber
  66FBB:  19 26 00 00 00     LINE_NUM     38                 ; Code Line 38
  66FC0:  24 82 0D 00 00     PUSH_VAR     nextWaveIndex
  66FC5:  26 94 14 00 00     ASSIGN       refreshEnemyPathDirections_local1
  66FCA:  19 28 00 00 00     LINE_NUM     40                 ; Code Line 40
  66FCF:  19 29 00 00 00     LINE_NUM     41                 ; Code Line 41
  66FD4:  24 94 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local1
  66FD9:  01 FF FF FF FF     PUSH_INT     -1
  66FDE:  0D                 EQ           
  66FDF:  18 0A 00 00 00     JMP_FALSE    loc_66FEA          ; Rel: +0xA
  66FE4:  1F                 RET          
  66FE5:  19 2B 00 00 00     LINE_NUM     43                 ; Code Line 43
loc_66FEA:
  66FEA:  01 98 00 00 00     PUSH_INT     152
  66FEF:  26 47 03 00 00     ASSIGN       getEquipmentByCategory_arg0
  66FF4:  1A                 ARG_COMMIT   
  66FF5:  01 17 00 00 00     PUSH_INT     23
  66FFA:  26 48 03 00 00     ASSIGN       getEquipmentByCategory_arg1
  66FFF:  1A                 ARG_COMMIT   
  67000:  24 94 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local1
  67005:  26 49 03 00 00     ASSIGN       getEquipmentByCategory_arg2
  6700A:  1A                 ARG_COMMIT   
  6700B:  01 C1 BD F0 FF     PUSH_INT     -999999
  67010:  26 4A 03 00 00     ASSIGN       getEquipmentByCategory_arg3
  67015:  1A                 ARG_COMMIT   
  67016:  1E B3 01 00 00     CALL_FUNC    getEquipmentByCategory
  6701B:  26 95 14 00 00     ASSIGN       refreshEnemyPathDirections_local2
  67020:  19 2C 00 00 00     LINE_NUM     44                 ; Code Line 44
  67025:  19 2D 00 00 00     LINE_NUM     45                 ; Code Line 45
  6702A:  24 95 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local2
  6702F:  01 04 00 00 00     PUSH_INT     4
  67034:  0F                 GT           
  67035:  18 0A 00 00 00     JMP_FALSE    loc_67040          ; Rel: +0xA
  6703A:  1F                 RET          
  6703B:  19 2F 00 00 00     LINE_NUM     47                 ; Code Line 47
loc_67040:
  67040:  24 95 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local2
  67045:  01 00 00 00 00     PUSH_INT     0
  6704A:  12                 LE           
  6704B:  18 0A 00 00 00     JMP_FALSE    loc_67056          ; Rel: +0xA
  67050:  1F                 RET          
  67051:  19 31 00 00 00     LINE_NUM     49                 ; Code Line 49
loc_67056:
  67056:  19 34 00 00 00     LINE_NUM     52                 ; Code Line 52
  6705B:  19 35 00 00 00     LINE_NUM     53                 ; Code Line 53
  67060:  19 36 00 00 00     LINE_NUM     54                 ; Code Line 54
  67065:  01 00 00 00 00     PUSH_INT     0
  6706A:  26 9E 14 00 00     ASSIGN       refreshEnemyPathDirections_local11
  6706F:  19 37 00 00 00     LINE_NUM     55                 ; Code Line 55
loc_67074:
  67074:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  67079:  01 04 00 00 00     PUSH_INT     4
  6707E:  10                 LT           
  6707F:  18 32 00 00 00     JMP_FALSE    loc_670B2          ; Rel: +0x32
  67084:  1C 13 00 00 00     JMP          loc_67098          ; Rel: +0x13
loc_67089:
  67089:  22 9E 14 00 00     PRE_INC      refreshEnemyPathDirections_local11
  6708E:  19 37 00 00 00     LINE_NUM     55                 ; Code Line 55
  67093:  1C E0 FF FF FF     JMP          loc_67074          ; Rel: 0x-20
loc_67098:
  67098:  01 00 00 00 00     PUSH_INT     0
  6709D:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  670A2:  28                 ARRAY_IDX    
  670A3:  26 96 14 00 00     ASSIGN       refreshEnemyPathDirections_local3
  670A8:  19 38 00 00 00     LINE_NUM     56                 ; Code Line 56
  670AD:  1C DB FF FF FF     JMP          loc_67089          ; Rel: 0x-25
loc_670B2:
  670B2:  01 00 00 00 00     PUSH_INT     0
  670B7:  26 9E 14 00 00     ASSIGN       refreshEnemyPathDirections_local11
  670BC:  19 39 00 00 00     LINE_NUM     57                 ; Code Line 57
loc_670C1:
  670C1:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  670C6:  24 95 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local2
  670CB:  10                 LT           
  670CC:  18 CA 00 00 00     JMP_FALSE    loc_67197          ; Rel: +0xCA
  670D1:  1C 13 00 00 00     JMP          loc_670E5          ; Rel: +0x13
loc_670D6:
  670D6:  20 9E 14 00 00     POST_INC     refreshEnemyPathDirections_local11
  670DB:  19 39 00 00 00     LINE_NUM     57                 ; Code Line 57
  670E0:  1C E0 FF FF FF     JMP          loc_670C1          ; Rel: 0x-20
loc_670E5:
  670E5:  01 99 00 00 00     PUSH_INT     153
  670EA:  26 47 03 00 00     ASSIGN       getEquipmentByCategory_arg0
  670EF:  1A                 ARG_COMMIT   
  670F0:  01 17 00 00 00     PUSH_INT     23
  670F5:  26 48 03 00 00     ASSIGN       getEquipmentByCategory_arg1
  670FA:  1A                 ARG_COMMIT   
  670FB:  24 94 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local1
  67100:  26 49 03 00 00     ASSIGN       getEquipmentByCategory_arg2
  67105:  1A                 ARG_COMMIT   
  67106:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  6710B:  26 4A 03 00 00     ASSIGN       getEquipmentByCategory_arg3
  67110:  1A                 ARG_COMMIT   
  67111:  1E B3 01 00 00     CALL_FUNC    getEquipmentByCategory
  67116:  26 9F 14 00 00     ASSIGN       refreshEnemyPathDirections_local12
  6711B:  19 3A 00 00 00     LINE_NUM     58                 ; Code Line 58
  67120:  19 3B 00 00 00     LINE_NUM     59                 ; Code Line 59
  67125:  01 18 00 00 00     PUSH_INT     24
  6712A:  26 4E 03 00 00     ASSIGN       getEquipmentIndexByName_arg0
  6712F:  1A                 ARG_COMMIT   
  67130:  24 9F 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local12
  67135:  26 4F 03 00 00     ASSIGN       getEquipmentIndexByName_arg1
  6713A:  1A                 ARG_COMMIT   
  6713B:  1E B5 01 00 00     CALL_FUNC    getEquipmentIndexByName
  67140:  26 A0 14 00 00     ASSIGN       refreshEnemyPathDirections_local13
  67145:  19 3C 00 00 00     LINE_NUM     60                 ; Code Line 60
  6714A:  19 3D 00 00 00     LINE_NUM     61                 ; Code Line 61
  6714F:  24 A0 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local13
  67154:  01 FF FF FF FF     PUSH_INT     -1
  67159:  14                 NE           
  6715A:  18 37 00 00 00     JMP_FALSE    loc_67192          ; Rel: +0x37
  6715F:  01 01 00 00 00     PUSH_INT     1
  67164:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  67169:  28                 ARRAY_IDX    
  6716A:  26 96 14 00 00     ASSIGN       refreshEnemyPathDirections_local3
  6716F:  19 40 00 00 00     LINE_NUM     64                 ; Code Line 64
  67174:  02 70 61 74 68 5F  PUSH_STR     "path_"
        00
  6717B:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  67180:  A4                 CALL_EXT_164                    ; itoa
  67181:  08                 ADD          
  67182:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  67187:  28                 ARRAY_IDX    
  67188:  26 9A 14 00 00     ASSIGN       refreshEnemyPathDirections_local7
  6718D:  19 42 00 00 00     LINE_NUM     66                 ; Code Line 66
loc_67192:
  67192:  1C 43 FF FF FF     JMP          loc_670D6          ; Rel: 0x-BD
loc_67197:
  67197:  19 47 00 00 00     LINE_NUM     71                 ; Code Line 71
  6719C:  4C                 CALL_EXT_76                     ; FirstSprite
  6719D:  26 A1 14 00 00     ASSIGN       refreshEnemyPathDirections_local14
  671A2:  19 48 00 00 00     LINE_NUM     72                 ; Code Line 72
loc_671A7:
  671A7:  24 A1 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local14
  671AC:  18 03 01 00 00     JMP_FALSE    loc_672B0          ; Rel: +0x103
  671B1:  1C 14 00 00 00     JMP          loc_671C6          ; Rel: +0x14
loc_671B6:
  671B6:  4D                 CALL_EXT_77                     ; NextSprite
  671B7:  26 A1 14 00 00     ASSIGN       refreshEnemyPathDirections_local14
  671BC:  19 48 00 00 00     LINE_NUM     72                 ; Code Line 72
  671C1:  1C E5 FF FF FF     JMP          loc_671A7          ; Rel: 0x-1B
loc_671C6:
  671C6:  24 A1 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local14
  671CB:  53                 CALL_EXT_83                     ; GetUnitVid
  671CC:  26 A2 14 00 00     ASSIGN       refreshEnemyPathDirections_local15
  671D1:  19 49 00 00 00     LINE_NUM     73                 ; Code Line 73
  671D6:  19 4A 00 00 00     LINE_NUM     74                 ; Code Line 74
  671DB:  24 A2 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local15
  671E0:  01 54 05 00 00     PUSH_INT     1364
  671E5:  0D                 EQ           
  671E6:  2D 10 00 00 00     OR_JMP       loc_671F7          ; Rel: +0x10
  671EB:  24 A2 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local15
  671F0:  01 74 0F 00 00     PUSH_INT     3956
  671F5:  0D                 EQ           
  671F6:  0E                 LOG_OR       
loc_671F7:
  671F7:  18 B3 00 00 00     JMP_FALSE    loc_672AB          ; Rel: +0xB3
  671FC:  01 74 0F 00 00     PUSH_INT     3956
  67201:  26 A2 14 00 00     ASSIGN       refreshEnemyPathDirections_local15
  67206:  19 4E 00 00 00     LINE_NUM     78                 ; Code Line 78
  6720B:  01 00 00 00 00     PUSH_INT     0
  67210:  26 9E 14 00 00     ASSIGN       refreshEnemyPathDirections_local11
  67215:  19 50 00 00 00     LINE_NUM     80                 ; Code Line 80
loc_6721A:
  6721A:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  6721F:  24 95 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local2
  67224:  10                 LT           
  67225:  18 66 00 00 00     JMP_FALSE    loc_6728C          ; Rel: +0x66
  6722A:  1C 13 00 00 00     JMP          loc_6723E          ; Rel: +0x13
loc_6722F:
  6722F:  22 9E 14 00 00     PRE_INC      refreshEnemyPathDirections_local11
  67234:  19 50 00 00 00     LINE_NUM     80                 ; Code Line 80
  67239:  1C E0 FF FF FF     JMP          loc_6721A          ; Rel: 0x-20
loc_6723E:
  6723E:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  67243:  28                 ARRAY_IDX    
  67244:  24 96 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local3
  67249:  18 3D 00 00 00     JMP_FALSE    loc_67287          ; Rel: +0x3D
  6724E:  24 A1 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local14
  67253:  01 A5 00 00 00     PUSH_INT     165
  67258:  24 9E 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local11
  6725D:  28                 ARRAY_IDX    
  6725E:  25 9A 14 00 00     ADDR_OF      refreshEnemyPathDirections_local7
  67263:  24 5A 00 00 00     PUSH_VAR     Action_arg3
  67268:  24 5B 00 00 00     PUSH_VAR     Action_arg4
  6726D:  4F                 CALL_EXT_79                     ; Action
  6726E:  18 18 00 00 00     JMP_FALSE    loc_67287          ; Rel: +0x18
  67273:  01 54 05 00 00     PUSH_INT     1364
  67278:  26 A2 14 00 00     ASSIGN       refreshEnemyPathDirections_local15
  6727D:  19 55 00 00 00     LINE_NUM     85                 ; Code Line 85
  67282:  1C 09 00 00 00     JMP          loc_6728C          ; Rel: +0x9
loc_67287:
  67287:  1C A7 FF FF FF     JMP          loc_6722F          ; Rel: 0x-59
loc_6728C:
  6728C:  24 A1 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local14
  67291:  01 3E 00 00 00     PUSH_INT     62
  67296:  24 A2 14 00 00     PUSH_VAR     refreshEnemyPathDirections_local15
  6729B:  24 5A 00 00 00     PUSH_VAR     Action_arg3
  672A0:  24 5B 00 00 00     PUSH_VAR     Action_arg4
  672A5:  4F                 CALL_EXT_79                     ; Action
  672A6:  19 5A 00 00 00     LINE_NUM     90                 ; Code Line 90
loc_672AB:
  672AB:  1C 0A FF FF FF     JMP          loc_671B6          ; Rel: 0x-F6
loc_672B0:
  672B0:  1F                 RET                             ; mark end of function
;Function refreshEnemyPathDirections() End
