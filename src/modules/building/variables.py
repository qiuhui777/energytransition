# -*- coding: utf-8 -*-
"""建筑结果变量定义"""

from dataclasses import dataclass, field
from typing import List
from ...base import BaseVariables


@dataclass
class BuildingVariables(BaseVariables):
    """建筑结果变量定义"""
    
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
        '氢',      # 行19
        '生物质',  # 行20
        '热'       # 行21
    ])
    
    # 建筑面积类型（行31-33）
    BUILDING_AREA_TYPES: List[str] = field(default_factory=lambda: [
        '城镇住宅',
        '农村住宅',
        '公共建筑'
    ])
    
    # 人均建筑面积类型（行38-40）
    PER_CAPITA_AREA_TYPES: List[str] = field(default_factory=lambda: [
        '城镇住宅',
        '农村住宅',
        '公共建筑'
    ])
    
    # 人口类型（行42-43）
    POPULATION_TYPES: List[str] = field(default_factory=lambda: [
        '城市人口',
        '农村人口'
    ])
    
    # 电量转换系数
    ELECTRICITY_CONVERSION_FACTOR: float = 1.229
