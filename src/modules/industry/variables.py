# -*- coding: utf-8 -*-
"""工业结果变量定义"""

from dataclasses import dataclass, field
from typing import List
from ...base import BaseVariables


@dataclass
class IndustryVariables(BaseVariables):
    """工业结果变量定义"""
    
    # 一次消费能源类型（行2-5）
    PRIMARY_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭',      # 行2 -> 来自消费总量的煤(行15)
        '石油',      # 行3 -> 来自消费总量的油(行16)
        '天然气',    # 行4 -> 来自消费总量的气(行17)
        '生物质'     # 行5 -> 来自消费总量的生物质(行20)
    ])
    
    # 消费结构能源类型（行8-12）
    STRUCTURE_TYPES: List[str] = field(default_factory=lambda: [
        '煤',   # 行8: 煤/消费总量
        '油',   # 行9: 油/消费总量
        '气',   # 行10: 气/消费总量
        '电',   # 行11: 电/消费总量
        '其他'  # 行12: 1 - SUM(煤+油+气+电)
    ])
    
    # 消费总量能源类型（行15-21）
    CONSUMPTION_TYPES: List[str] = field(default_factory=lambda: [
        '煤',      # 行15
        '油',      # 行16
        '气',      # 行17
        '电',      # 行18
        '氢',      # 行19: 氢调整 + 氢原始
        '生物质',  # 行20
        '热'       # 行21
    ])
    
    # 电量转换系数
    ELECTRICITY_CONVERSION_FACTOR: float = 1.229
