"""
common/definitions.py
const value storage
no need to initialize
"""

from logger import logger


class LgdDefinitions:
    """
    Unified management of Flag definitions,
    type mappings,
    and constants in LGD files.
    """

    # XOR Keys
    VARIABLE_XOR_KEY = 0x17
    # BYTECODE_XOR_KEY = 0x25


    # === for more strict check rules ===
    # True:  type not defined in TYPE_MAP is encountered, log warning
    # False: only check for lower bytes and no warning logs
    STRICT_CHECK = True

    # === Flag Definition ===
    _FLAG_INFO = {
        0x81: {"type": "string", "mode": "def_only"},
        0x82: {"type": "int", "mode": "def_only"},
        0x85: {"type": "string", "mode": "array_def"},
        0x86: {"type": "int", "mode": "array_def"},
        0x89: {"type": "string", "mode": "scalar"},
        0x8A: {"type": "int", "mode": "scalar"},
        0x8D: {"type": "string", "mode": "array_init"},
        0x8E: {"type": "int", "mode": "array_init"},
    }

    # === Base Types ===
    BASE_VARIABLE = 0x01
    BASE_EXTERN = 0x02
    BASE_FUNCTION = 0x03

    # === Type Whitelist detailed version ===
    # little endian 02 01 -> 0x0102
    TYPE_MAP = {
        # --- variable ---
        # Hex: 01 00
        0x0001: "Variable",

        # --- Extern Function ---
        # Hex: 02 00 -> 0x0002
        0x0002: "Extern Function",
        # Hex: 02 01 -> 0x0102
        0x0102: "Extern (Ret Used)",

        # --- Script Function ---
        # Hex: 03 00 -> 0x0003
        0x0003: "Function (Void)",
        # Hex: 03 02 -> 0x0203
        0x0203: "Function (Returns Value)",
        # Hex: 03 03 -> 0x0303
        0x0303: "Function (Returns & Used)",

    }

    @classmethod
    def get_flag_info(cls, flag: int, offset: int = None) -> dict:
        """
        Get Flag Info
        :param flag: Flag vals
        :param offset: (optional) Flag Offset, used to locate warnings
        """
        if flag not in cls._FLAG_INFO:
            # construct logging info
            msg = f"[Definitions] Found undefined FLAG: 0x{flag:02X}"
            if offset is not None:
                msg += f" @ Offset: 0x{offset:X}"  # with offset to debug

            logger.warning(msg)
            return {"type": "unknown_int", "mode": "scalar"}
        return cls._FLAG_INFO[flag]

    @classmethod
    def validate_and_get_desc(cls, type_val: int, offset: int = None) -> tuple[int, str]:
        """
        Get and Varify Type
        :param type_val: Type Val
        :param offset: (Optional) type Offset, used to locate warnings
        """
        base_type = type_val & 0xFF
        description = cls.TYPE_MAP.get(type_val, "Unknown Type")

        if cls.STRICT_CHECK:
            if type_val not in cls.TYPE_MAP:
                # construct logging info
                msg = f"[Definitions] Undocumented TYPE: 0x{type_val:04X} "
                if offset is not None:
                    msg += f" @ Offset: 0x{offset:X}" # with offset to debug
                msg += ". Please add to TYPE_MAP."

                logger.warning(msg)

        return base_type, description