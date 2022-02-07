# ！/usr/bin/env python
# -*- coding: UTF-8 -*-

def format_txt(s: str) -> str:
    """去除字符串中不必要的成分并返回

    Args:
        s (str): 要整理的字符串

    Returns:
        str: 处理后的字符串
    """
    return (
        s.strip()
            .replace("\xa0", "")
            .replace("\u2002", "")
            .replace("\u3000", "")
            .strip()
    )
