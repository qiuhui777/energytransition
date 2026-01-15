# -*- coding: utf-8 -*-
"""能源结构变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class StructureVariables:
    """能源结构变量定义"""
    
    # 年份列表
    YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060'
    ])
    
    # 部门类型
    SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '氢能', '其他'
    ])
    
    # 终端消费部门
    TERMINAL_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '其他'
    ])
    
    # 能源类型（终端消费）
    ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '电力', '氢能', '生物质'
    ])
    
    # 电力部门能源类型
    POWER_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '风电', '光伏', '水电', '核电', '生物质'
    ])
    
    # 氢能部门能源类型
    HYDROGEN_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '电力', '生物质', '煤炭'
    ])
    
    # 一次能源类型
    PRIMARY_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤', '油', '气', '非化石'
    ])
    
    # 非化石能源细分
    NON_FOSSIL_TYPES: List[str] = field(default_factory=lambda: [
        '风', '光', '水', '核', '生物质'
    ])
    
    # 终端消费结构指标
    TERMINAL_INDICATORS: List[str] = field(default_factory=lambda: [
        '工业总消费', '建筑总消费', '交通总消费', '其他部门消费', '终端总消费',
        '工业电气化率', '建筑电气化率', '交通电气化率',
        '氢能总消费', '氢能占比', '终端电气化率'
    ])
    
    # 终端能源结构指标
    TERMINAL_STRUCTURE: List[str] = field(default_factory=lambda: [
        '煤', '油', '气', '生物质', '氢', '电'
    ])
    
    # 一次能源结构指标
    PRIMARY_INDICATORS: List[str] = field(default_factory=lambda: [
        '煤', '油', '气', '非化石', '风', '光', '水', '核', '生物质', '总能源消费'
    ])
    
    # 能源结构占比指标
    STRUCTURE_RATIOS: List[str] = field(default_factory=lambda: [
        '煤炭（%）', '石油（%）', '天然气（%）', '非化石能源（%）',
        '风', '光', '水', '核', '生物质'
    ])
    
    # 电力转换系数（万亿kWh -> 亿tce）
    ELECTRICITY_CONVERSION: float = 1.229
