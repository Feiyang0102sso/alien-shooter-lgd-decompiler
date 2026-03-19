"""
common/binary_utils.py
functions to parse the binary strings
"""


def read_xor_string(data: bytes, offset: int, xor_key: int) -> tuple[str, int, list[int]]:
    """
    读取并解密 XOR 字符串。
    Args:
        data: 二进制数据
        offset: 当前偏移量
        xor_key: 解密用的 key (使其通用化)
    Returns:
        (解码后的字符串, 新的偏移量, 原始字节列表)
    """
    raw_bytes = [] #存储读取到的原始字节（包括终止符）
    chars = [] #存储解密后的字符
    curr = offset
    data_len = len(data)

    while curr < data_len:
        b = data[curr]
        raw_bytes.append(b)
        curr += 1
        if b == 0x00: #在终止符处停止
            break
        chars.append(chr(b ^ xor_key))

    return "".join(chars), curr, raw_bytes


def fmt_hex(bytes_input) -> str:
    """通用 Hex 格式化工具"""
    if isinstance(bytes_input, (bytes, bytearray)):
        bytes_list = list(bytes_input)
    elif isinstance(bytes_input, int):
        bytes_list = [bytes_input]
    else:
        bytes_list = bytes_input

    return " ".join(f"{b:02X}" for b in bytes_list)