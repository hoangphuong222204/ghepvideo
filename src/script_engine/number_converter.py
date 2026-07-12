"""Utility module for expanding numbers into spelled-out Vietnamese text."""

import re

# Single digits and basic groups
DIGITS = {
    "0": "không",
    "1": "một",
    "2": "hai",
    "3": "ba",
    "4": "bốn",
    "5": "năm",
    "6": "sáu",
    "7": "bảy",
    "8": "tám",
    "9": "chín"
}


def _read_three_digits(s: str, is_first: bool = False) -> str:
    """Reads a block of exactly 3 digits in Vietnamese syntax."""
    s = s.zfill(3)
    hundred = s[0]
    ten = s[1]
    unit = s[2]

    words = []

    # Hundred position
    if hundred != "0" or not is_first:
        words.append(DIGITS[hundred] + " trăm")

    # Ten position
    if ten == "0":
        if hundred != "0" and unit != "0":
            words.append("linh")
    elif ten == "1":
        words.append("mười")
    else:
        words.append(DIGITS[ten] + " mươi")

    # Unit position
    if unit != "0":
        if unit == "1" and ten not in {"0", "1"}:
            words.append("mốt")
        elif unit == "5" and ten != "0":
            words.append("lăm")
        elif unit == "4" and ten not in {"0", "1"}:
            words.append("tư")
        else:
            words.append(DIGITS[unit])

    return " ".join(words)


def int_to_vietnamese_words(n: int) -> str:
    """Converts a positive integer into spelled-out Vietnamese words."""
    if n == 0:
        return "không"

    s = str(n)
    groups = []
    
    # Pad string to multiple of 3
    pad_len = (3 - len(s) % 3) % 3
    s = "0" * pad_len + s

    # Slice into blocks of 3
    for i in range(0, len(s), 3):
        groups.append(s[i:i+3])

    units = ["", "nghìn", "triệu", "tỷ"]
    words = []
    
    num_groups = len(groups)
    for idx, group in enumerate(groups):
        if group == "000":
            continue
            
        group_words = _read_three_digits(group, idx == 0)
        unit_idx = (num_groups - 1 - idx) % 4
        
        # Every 4th unit group starts "tỷ" chain
        tys = (num_groups - 1 - idx) // 4
        unit_name = units[unit_idx]
        
        chunk = group_words
        if unit_name:
            chunk += f" {unit_name}"
        if tys > 0 and unit_idx == 0:
            chunk += " " + " ".join(["tỷ"] * tys)
            
        words.append(chunk)

    result = " ".join(words).strip()
    # Normalize double spaces
    return re.sub(r"\s+", " ", result)


class NumberConverter:
    """Utility class to orchestrate expansion of numerical patterns in text."""

    @classmethod
    def expand_numbers(cls, text: str) -> str:
        """Finds all standard integer numbers in a string and expands them.

        E.g., "Sản phẩm 100 cam kết hiệu quả" -> "Sản phẩm một trăm cam kết hiệu quả".
        """
        if not text:
            return ""

        def replace_match(match: re.Match) -> str:
            num_str = match.group(0)
            try:
                val = int(num_str)
                return int_to_vietnamese_words(val)
            except ValueError:
                return num_str

        # Match consecutive digits
        pattern = re.compile(r"\b\d+\b")
        return pattern.sub(replace_match, text)
