;Function multiplayerP2PMessageSend() Begin
  128E0F:  24 92 1D 00 00     PUSH_VAR     multiplayerP2PMessageSend_arg0
  128E14:  26 8F 1D 00 00     ASSIGN       multiplayerSendMessageViaLobby_arg0
  128E19:  1A                 ARG_COMMIT   
  128E1A:  02 74 65 6D 70 2E  PUSH_STR     "temp.p2p_to_send."
        70 32 70 5F 74 6F
        5F 73 65 6E 64 2E
        00
  128E2D:  26 90 1D 00 00     ASSIGN       multiplayerSendMessageViaLobby_arg1
  128E32:  1A                 ARG_COMMIT   
  128E33:  02 6D 65 73 73 61  PUSH_STR     "message_type;"
        67 65 5F 74 79 70
        65 3B 00
  128E42:  24 93 1D 00 00     PUSH_VAR     multiplayerP2PMessageSend_arg1
  128E47:  08                 ADD          
  128E48:  26 91 1D 00 00     ASSIGN       multiplayerSendMessageViaLobby_arg2
  128E4D:  1A                 ARG_COMMIT   
  128E4E:  1E 9D 06 00 00     CALL_FUNC    multiplayerSendMessageViaLobby
  128E53:  19 DA 03 00 00     LINE_NUM     986               ; Code Line 986
  128E58:  1F                 RET                            ; mark end of function
;Function multiplayerP2PMessageSend() End
