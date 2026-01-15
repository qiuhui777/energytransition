# -*- coding: utf-8 -*-
"""电力结果变量定义"""

from dataclasses import dataclass, field
from typing import List
from ...base import BaseVariables


@dataclass
class PowerVariables(BaseVariables):
    """电力结果变量定义"""
    
    # 电力装机类型（行2-12）
    CAPACITY_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行2
        '煤电+CCS',    # 行3
        '气电',        # 行4
        '气电+CCS',    # 行5
        '核电',        # 行6
        '水电',        # 行7
        '风电',        # 行8
        '光伏',        # 行9
        '生物质',      # 行10
        '生物质+CCS',  # 行11
        '其他'         # 行12
    ])
    
    # 储能类型（行18-19）
    STORAGE_TYPES: List[str] = field(default_factory=lambda: [
        '抽蓄',    # 行18
        '电化学'   # 行19
    ])
    
    # 发电量类型（行23-33）
    GENERATION_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行23
        '煤电+CCS',    # 行24
        '气电',        # 行25
        '气电+CCS',    # 行26
        '核电',        # 行27
        '水电',        # 行28
        '风电',        # 行29
        '光伏',        # 行30
        '生物质',      # 行31
        '生物质+CCS',  # 行32
        '其他'         # 行33
    ])
    
    # 利用小时数类型（行56-66）
    UTILIZATION_HOURS_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行56
        '煤电+CCS',    # 行57
        '气电',        # 行58
        '气电+CCS',    # 行59
        '核电',        # 行60
        '水电',        # 行61
        '风电',        # 行62
        '光伏',        # 行63
        '生物质',      # 行64
        '生物质+CCS',  # 行65
        '其他'         # 行66
    ])
    
    # 碳捕集占比类型（行73-78）
    CCS_RATIO_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行73
        '煤电+CCS',    # 行74
        '气电',        # 行75
        '气电+CCS',    # 行76
        '生物质',      # 行77
        '生物质+CCS'   # 行78
    ])
    
    # 能源消耗类型（行81-90）
    ENERGY_CONSUMPTION_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭',        # 行81
        '石油',        # 行82
        '天然气',      # 行83
        '其它非化石能源',  # 行84
        '风能',        # 行86
        '太阳能',      # 行87
        '水能',        # 行88
        '核能',        # 行89
        '生物质能'     # 行90
    ])
    
    # CCS改造容量变化系数类型（行93-95）
    CCS_RETROFIT_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',    # 行93
        '气电',    # 行94
        '生物质'   # 行95
    ])
    
    # 燃料消耗率类型（行98-104）
    FUEL_RATE_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭',        # 行98
        '煤炭CCS',     # 行99
        '天然气',      # 行100
        '天然气CCS',   # 行101
        '生物质',      # 行102
        '生物质CCS',   # 行103
        '浓缩铀'       # 行104
    ])
    
    # 装机成本类型（行117-130）
    CAPACITY_COST_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行117
        '煤电+CCS',    # 行118
        '气电',        # 行119
        '气电+CCS',    # 行120
        '核电',        # 行121
        '水电',        # 行122
        '风电(陆上)',  # 行123
        '风电(海上)',  # 行124
        '光伏(集中)',  # 行125
        '光伏(分布式)', # 行126
        '生物质',      # 行127
        '生物质+CCS',  # 行128
        '抽蓄',        # 行129
        '电化学'       # 行130
    ])
    
    # 运维成本占比类型（行132-143）
    OM_COST_RATIO_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行132
        '煤电+CCS',    # 行133
        '气电',        # 行134
        '气电+CCS',    # 行135
        '核电',        # 行136
        '水电',        # 行137
        '风电(陆上)',  # 行138
        '风电(海上)',  # 行139
        '光伏(集中)',  # 行140
        '光伏(分布式)', # 行141
        '生物质',      # 行142
        '生物质+CCS'   # 行143
    ])
    
    # 燃料成本类型（行145-156）
    FUEL_COST_TYPES: List[str] = field(default_factory=lambda: [
        '煤电',        # 行145
        '煤电+CCS',    # 行146
        '气电',        # 行147
        '气电+CCS',    # 行148
        '核电',        # 行149
        '水电',        # 行150
        '风电(陆上)',  # 行151
        '风电(海上)',  # 行152
        '光伏(集中)',  # 行153
        '光伏(分布式)', # 行154
        '生物质',      # 行155
        '生物质+CCS'   # 行156
    ])
    
    # 设备寿命（年）
    EQUIPMENT_LIFETIME: dict = field(default_factory=lambda: {
        '煤电': 30,
        '煤电+CCS': 30,
        '气电': 25,
        '气电+CCS': 25,
        '核电': 40,
        '水电': 50,
        '风电(陆上)': 20,
        '风电(海上)': 20,
        '光伏(集中)': 25,
        '光伏(分布式)': 25,
        '生物质': 25,
        '生物质+CCS': 25,
        '抽蓄': 40,
        '电化学': 10
    })
    
    # 折现率
    DISCOUNT_RATE: float = 0.06
    
    # 天然气转换系数
    GAS_CONVERSION_FACTOR: float = 1.33  # km3天然气 -> 亿tce
    
    # CO2排放系数
    COAL_CO2_FACTOR: float = 2.66  # 吨CO2/吨煤
    GAS_CO2_FACTOR: float = 2.16   # 吨CO2/km3天然气
    BIOMASS_CO2_FACTOR: float = 1.74  # 吨CO2/吨生物质
