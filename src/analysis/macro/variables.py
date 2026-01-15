# -*- coding: utf-8 -*-
"""宏观测算参考变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class MacroVariables:
    """宏观测算参考变量定义"""
    
    # 基准年份
    BASE_YEAR: int = 2005
    
    # 基准年GDP（万亿元）
    BASE_GDP: float = 18.2
    
    # 年份列表
    YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060'
    ])
    
    # 能源类型
    ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '非化石'
    ])
    
    # 部门类型
    SECTOR_TYPES: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '制氢', '其他'
    ])
    
    # 煤炭部门分类（行34-40）
    COAL_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '制氢', '其他'
    ])
    
    # 石油部门分类（行43-48）
    OIL_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '其他'
    ])
    
    # 天然气部门分类（行51-56）
    GAS_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '其他'
    ])
    
    # 非化石能源分类（行59-69）
    NON_FOSSIL_TYPES: List[str] = field(default_factory=lambda: [
        '工业-生物质', '建筑-生物质', '交通-生物质', '电力-生物质',
        '其他-生物质', '氢能-生物质', '生物质总量',
        '电力-水能', '电力-核能', '电力-风光'
    ])
    
    # CO2排放因子（吨CO2/吨标煤）
    EMISSION_FACTORS: Dict[str, float] = field(default_factory=lambda: {
        '煤': 2.66,   # 行29
        '油': 2.12,   # 行30
        '气': 1.63    # 行31
    })
    
    # 宏观指标类型
    MACRO_INDICATORS: List[str] = field(default_factory=lambda: [
        'GDP年增长率',           # 行3 - Input
        'GDP指数',               # 行4 - 计算
        '一次能源指数',          # 行5 - 计算
        '二氧化碳指数',          # 行6 - 计算
        '能源消费弹性',          # 行7 - 计算
        '能源消费年增长率',      # 行8 - 计算
        '能源消费量',            # 行9 - 计算
        '煤炭占比',              # 行10 - 计算
        '石油占比',              # 行11 - 计算
        '天然气占比',            # 行12 - 计算
        '非化石占比',            # 行13 - 计算
        '单位能耗CO2强度',       # 行14 - 计算
        '单位能耗CO2强度年下降率', # 行15 - 计算
        'CO2排放量',             # 行16 - 计算
        'CO2排放增长率',         # 行17 - 计算
        'GDP的CO2强度',          # 行18 - 计算
        '单位GDP的CO2强度下降率', # 行19 - 计算
        '比2005年下降幅度',      # 行20 - 计算
        'GDP的能耗强度',         # 行21 - 计算
        '5年GDP能源强度下降幅度', # 行22 - Input
        '5年GDP的CO2强度下降幅度', # 行23 - 计算
        '单位GDP能耗强度年下降率', # 行24 - 计算
        '二氧化碳年下降率',      # 行25 - 计算
        '二氧化碳五年累计下降率', # 行26 - 计算
        '二氧化碳五年绝对下降量', # 行27 - 计算
        '碳捕集量'               # 行28 - 来自其他模块
    ])
    
    # 输入变量（需要用户提供）
    INPUT_VARIABLES: List[str] = field(default_factory=lambda: [
        'GDP年增长率',
        '5年GDP能源强度下降幅度'
    ])
