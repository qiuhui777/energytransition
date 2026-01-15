# -*- coding: utf-8 -*-
"""2030年和2050年平衡表变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class BalanceVariables:
    """2030年和2050年平衡表变量定义"""
    
    # 目标年份
    TARGET_YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2030', '2035', '2050', '2060'
    ])
    
    # ==================== 终端部门 ====================
    TERMINAL_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '其它', '总计'
    ])
    
    # ==================== 供应部门 ====================
    SUPPLY_SECTORS: List[str] = field(default_factory=lambda: [
        '氢能供应', '电力供应'
    ])
    
    # ==================== 能源类型 ====================
    # 一次能源消费类型
    PRIMARY_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '非化石能源'
    ])
    
    # ==================== 电力消费/生产列 ====================
    POWER_COLUMNS: List[str] = field(default_factory=lambda: [
        '电量/万亿千瓦时',      # D列
        '电热当量/亿tce'        # E列
    ])
    
    # ==================== 氢能消费列 ====================
    HYDROGEN_COLUMN: str = '氢能消费/亿tce'  # F列
    
    # ==================== 一次能源消费列 ====================
    PRIMARY_ENERGY_COLUMNS: List[str] = field(default_factory=lambda: [
        '煤炭',      # G列
        '石油',      # H列
        '天然气',    # I列
        '非化石能源', # J列
        '小计'       # K列
    ])
    
    # ==================== 终端能源消费列 ====================
    TERMINAL_ENERGY_COLUMN: str = '终端能源消费/亿tce'  # L列
    
    # ==================== 终端消费结构列 ====================
    TERMINAL_STRUCTURE_COLUMN: str = '终端消费结构/%'  # M列
    
    # ==================== CO2排放列 ====================
    CO2_COLUMN: str = 'CO2直接排放/亿吨'  # N列
    
    # ==================== 汇总行 ====================
    SUMMARY_ROWS: List[str] = field(default_factory=lambda: [
        '一次能源消费',
        '一次能源结构',
        '工业过程',
        '非二氧化碳',
        'CCS',
        '碳汇',
        '能源相关CO2',
        '温室气体排放'
    ])
    
    # ==================== 转换系数 ====================
    CONVERSION_FACTORS: Dict[str, float] = field(default_factory=lambda: {
        '电热当量系数': 1.229,  # 万亿千瓦时 -> 亿tce
    })
    
    # ==================== CO2排放因子 ====================
    CO2_EMISSION_FACTORS: Dict[str, float] = field(default_factory=lambda: {
        '煤炭': 2.66,   # 亿吨CO2/亿tce
        '石油': 1.73,
        '天然气': 1.56
    })
    
    # ==================== 数据模板行号映射 (用于从数据模板读取电力消费) ====================
    TEMPLATE_ROW_MAPPING: Dict[str, int] = field(default_factory=lambda: {
        '工业_电力': 114,    # E114
        '建筑_电力': 115,    # E115
        '交通_电力': 116,    # E116
        '其它_电力': 118,    # E118
        '氢能供应_电力': 120  # E120
    })
    
    # ==================== 年份列映射 (数据模板中的列) ====================
    YEAR_COLUMN_MAPPING: Dict[str, str] = field(default_factory=lambda: {
        '2020': 'C',
        '2030': 'E',
        '2035': 'F',
        '2050': 'I',
        '2060': 'K'
    })
    
    # ==================== 能源消费结构行号映射 ====================
    STRUCTURE_ROW_MAPPING: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        '工业': {
            '氢能': 6,
            '煤炭': 2,
            '石油': 3,
            '天然气': 4,
            '非化石能源': 7
        },
        '建筑': {
            '氢能': 12,
            '煤炭': 8,
            '石油': 9,
            '天然气': 10,
            '非化石能源': 13
        },
        '交通': {
            '氢能': 18,
            '煤炭': 14,
            '石油': 15,
            '天然气': 16,
            '非化石能源': 19
        },
        '其它': {
            '煤炭': 31,
            '石油': 32,
            '天然气': 33
        },
        '电力供应': {
            '煤炭': 20,
            '石油': 21,
            '天然气': 22,
            '非化石能源_核': 23,
            '非化石能源_水': 24,
            '非化石能源_风': 25,
            '非化石能源_光': 26,
            '非化石能源_生物质': 27
        },
        '氢能供应': {
            '煤炭': 30,
            '非化石能源': 29
        }
    })
    
    # ==================== 碳排放轨迹行号映射 ====================
    TRAJECTORY_ROW_MAPPING: Dict[str, int] = field(default_factory=lambda: {
        '工业过程': 41,
        '非二氧化碳': 43,
        'CCS_电力': 37,
        'CCS_工业': 32,
        'DACCS': 39,
        '碳汇': 45
    })
