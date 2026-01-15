# -*- coding: utf-8 -*-
"""数据模板变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TemplateVariables:
    """数据模板变量定义 - 中国碳中和路径数据汇总模板"""
    
    # 年份列表
    YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060'
    ])
    
    # 部门类型
    SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力'
    ])
    
    # ==================== 工业部门变量 (行5-28) ====================
    # 终端能源消费量
    INDUSTRY_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '电力', '氢能', '其它非化石能源', '生物质'
    ])
    
    # 工业其他变量
    INDUSTRY_OTHER_VARS: List[str] = field(default_factory=lambda: [
        '工业用电电力部门需求', '工业电力自解决量',
        '工业用氢电力部门外部需求', '工业用氢自解决量',
        '工业用热总量', '工业用热自解决量', '工业用热电力部门提供量', '工业向建筑部门供热量'
    ])
    
    # 工业CO2排放
    INDUSTRY_CO2_VARS: List[str] = field(default_factory=lambda: [
        '直接总排放', '来自煤炭', '来自石油', '来自天然气',
        '工业过程CO2', '来自电力'
    ])
    
    # ==================== 建筑部门变量 (行31-51) ====================
    BUILDING_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '电力', '氢能', '其它非化石能源', '生物质'
    ])
    
    BUILDING_OTHER_VARS: List[str] = field(default_factory=lambda: [
        '建筑电力消费来自电力部门的量', '建筑分布式自解决量',
        '建筑用热总量', '建筑用热自解决量', '建筑用热来自电力部门', '建筑用热来自工业部门'
    ])
    
    BUILDING_CO2_VARS: List[str] = field(default_factory=lambda: [
        '直接总排放', '来自煤炭', '来自石油', '来自天然气', '来自电力'
    ])
    
    # ==================== 交通部门变量 (行54-68) ====================
    TRANSPORT_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '电力', '氢能', '其它非化石能源', '生物质'
    ])
    
    TRANSPORT_OTHER_VARS: List[str] = field(default_factory=lambda: [
        '交通可提供的电化学储能量'
    ])
    
    TRANSPORT_CO2_VARS: List[str] = field(default_factory=lambda: [
        '直接总排放', '来自煤炭', '来自石油', '来自天然气', '来自电力'
    ])
    
    # ==================== 电力部门变量 (行72-130) ====================
    # 能源消耗
    POWER_ENERGY_TYPES: List[str] = field(default_factory=lambda: [
        '煤炭', '石油', '天然气', '其它非化石能源'
    ])
    
    POWER_NON_FOSSIL_TYPES: List[str] = field(default_factory=lambda: [
        '风能', '太阳能', '水能', '核能', '生物质能'
    ])
    
    # 电力装机数据
    POWER_CAPACITY_TYPES: List[str] = field(default_factory=lambda: [
        '煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
        '风电', '光伏', '生物质', '生物质+CCS', '储能', '总装机'
    ])
    
    # 发电量数据
    POWER_GENERATION_TYPES: List[str] = field(default_factory=lambda: [
        '煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
        '风电', '光伏', '生物质', '生物质+CCS', '总发电量'
    ])
    
    # 电力消费数据
    POWER_CONSUMPTION_TYPES: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力用于终端部门直接消费', '其他',
        '电力用于终端部门总消费', '电制氢', '电力消费总量', '电力增长率'
    ])
    
    # 电力CO2排放
    POWER_CO2_VARS: List[str] = field(default_factory=lambda: [
        '来自煤炭', '来自天然气', '总直接排放', '化石能源CCS', '生物质CCS', '净排放'
    ])
    
    # ==================== 非二氧化碳排放 (行134-144) ====================
    NON_CO2_BY_SECTOR: List[str] = field(default_factory=lambda: [
        '工业', '能源', '农业', '废弃物', '制冷剂'
    ])
    
    NON_CO2_BY_GAS: List[str] = field(default_factory=lambda: [
        'CH4', 'N2O', 'F-gases'
    ])
    
    # ==================== 碳汇量 (行148-149) ====================
    CARBON_SINK_VARS: List[str] = field(default_factory=lambda: ['碳汇量'])
    
    # ==================== 氢能 (行154-173) ====================
    HYDROGEN_SUPPLY_TYPES: List[str] = field(default_factory=lambda: [
        '灰氢', '蓝氢', '生物质制氢', '电制氢'
    ])
    
    HYDROGEN_EFFICIENCY_VARS: List[str] = field(default_factory=lambda: [
        '电制氢效率', '煤制氢效率', '生物质制氢效率'
    ])
    
    HYDROGEN_CONSUMPTION_VARS: List[str] = field(default_factory=lambda: [
        '电消费', '煤消费', '生物质消费'
    ])
    
    HYDROGEN_DEMAND_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '总氢需求'
    ])
    
    HYDROGEN_RATIO_VARS: List[str] = field(default_factory=lambda: [
        '灰氢比例', '蓝氢比例', '生物质制氢总占比'
    ])
    
    # ==================== 生物质 (行177-182) ====================
    BIOMASS_SECTORS: List[str] = field(default_factory=lambda: [
        '工业', '建筑', '交通', '电力', '氢能', '总计'
    ])
    
    # ==================== 排放因子 ====================
    EMISSION_FACTORS: Dict[str, float] = field(default_factory=lambda: {
        '煤': 2.64,   # 吨CO2/吨标煤
        '油': 2.08,
        '气': 1.63
    })
    
    # 氢能转换参数
    HYDROGEN_CONVERSION: float = 0.20477  # 1万立方米 = 0.893吨 = 4.361吨标煤
