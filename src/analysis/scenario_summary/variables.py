# -*- coding: utf-8 -*-
"""情景数据一览表变量定义

基于temp11.xlsx中的情景数据一览表定义变量名称和结构
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ScenarioSummaryVariables:
    """情景数据一览表变量定义"""
    
    # 年份列表
    YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060'
    ])
    
    # ==================== 基础指标 (行2-4) ====================
    # 人口 (亿人)
    POPULATION: str = '人口'
    # GDP年增长率 (%)
    GDP_GROWTH_RATE: str = 'GDP年增长率'
    # GDP指数 (2005=1)
    GDP_INDEX: str = 'GDP指数'
    
    # ==================== 能源消费 (行5-9) ====================
    # 能源消费量 (亿tce)
    ENERGY_CONSUMPTION: str = '能源消费量'
    # 能源结构占比 (%)
    COAL_RATIO: str = '煤炭'
    OIL_RATIO: str = '石油'
    GAS_RATIO: str = '天然气'
    NON_FOSSIL_RATIO: str = '非化石'
    
    # ==================== CO2排放 (行10-15) ====================
    # 能源相关CO2排放量 (亿tce) - 注：单位应为亿tCO2
    ENERGY_CO2_EMISSION: str = '能源相关CO2排放量'
    # 各部门直接CO2排放 (亿tCO2)
    INDUSTRY_DIRECT_CO2: str = '工业部门直接CO2排放'
    BUILDING_DIRECT_CO2: str = '建筑部门直接CO2排放'
    TRANSPORT_DIRECT_CO2: str = '交通部门直接CO2排放'
    POWER_DIRECT_CO2_NO_CCS: str = '电力部分直接CO2排放-无CCS'
    OTHER_SECTOR_CO2: str = '其它部门'
    
    # ==================== 非CO2温室气体 (行16-19) ====================
    # 甲烷 (亿tCO2e)
    METHANE: str = '甲烷'
    # 氧化亚氮 (亿tCO2e)
    N2O: str = '氧化亚氮'
    # F-Gas (亿tCO2e)
    F_GAS: str = 'F-Gas'
    # 工业过程排放 (亿tCO2e)
    INDUSTRIAL_PROCESS: str = '工业过程排放'
    
    # ==================== 温室气体汇总 (行20-23) ====================
    # 温室气体排放总量 (亿tCO2e)
    TOTAL_GHG_EMISSION: str = '温室气体排放总量'
    # 碳捕集埋存量 (亿tCO2e)
    CCS_AMOUNT: str = '碳捕集埋存量'
    # 碳汇量 (亿tCO2e)
    CARBON_SINK: str = '碳汇量'
    # 温室气体净排放 (亿tCO2e)
    NET_GHG_EMISSION: str = '温室气体净排放'
    
    # ==================== 强度指标 (行24-25) ====================
    # 单位能耗CO2强度 (kgCO2/kgce)
    CO2_INTENSITY_PER_ENERGY: str = '单位能耗CO2强度'
    # 人均温室气体排放量 (tCO2e/人)
    GHG_PER_CAPITA: str = '人均温室气体排放量'
    
    # ==================== 增长率指标 (行26-30) ====================
    # 能源消费年增长率 (%)
    ENERGY_GROWTH_RATE: str = '能源消费年增长率'
    # CO2排放年增长率 (%)
    CO2_GROWTH_RATE: str = 'CO2排放年增长率'
    # 单位GDP能耗强度年下降率 (%)
    GDP_ENERGY_INTENSITY_DECLINE: str = '单位GDP能耗强度年下降率'
    # 单位GDP CO2强度年下降率 (%)
    GDP_CO2_INTENSITY_DECLINE: str = '单位GDPCO2强度年下降率'
    # 单位能耗CO2强度年下降率 (%)
    ENERGY_CO2_INTENSITY_DECLINE: str = '单位能耗CO2强度年下降率'
    
    # ==================== 5年下降幅度 (行31-32) ====================
    # 5年GDP能源强度下降幅度 (%)
    GDP_ENERGY_INTENSITY_5Y_DECLINE: str = '5年GDP能源强度下降幅度'
    # 5年GDP CO2强度下降幅度 (%)
    GDP_CO2_INTENSITY_5Y_DECLINE: str = '5年GDPCO2强度下降幅度'
    
    # ==================== 弹性系数 (行33) ====================
    # 能源消费弹性
    ENERGY_ELASTICITY: str = '能源消费弹性'
    
    # ==================== 数据来源映射 ====================
    # 定义各变量的数据来源
    DATA_SOURCES: Dict[str, Dict] = field(default_factory=lambda: {
        # 来自宏观测算参考 (macro_output.csv)
        'GDP年增长率': {'source': 'macro', 'row': 3, 'multiplier': 100},
        'GDP指数': {'source': 'macro', 'row': 4, 'multiplier': 1},
        
        # 来自能源消费结构 (structure_output.csv)
        '能源消费量': {'source': 'structure', 'row': 67, 'multiplier': 1},
        '煤炭': {'source': 'structure', 'row': 69, 'multiplier': 100},
        '石油': {'source': 'structure', 'row': 70, 'multiplier': 100},
        '天然气': {'source': 'structure', 'row': 71, 'multiplier': 100},
        '非化石': {'source': 'structure', 'row': 72, 'multiplier': 100},
        
        # 来自碳排放轨迹 (trajectory_output.csv)
        '工业部门直接CO2排放': {'source': 'trajectory', 'row': 31, 'multiplier': 1},
        '建筑部门直接CO2排放': {'source': 'trajectory', 'row': 33, 'multiplier': 1},
        '交通部门直接CO2排放': {'source': 'trajectory', 'row': 34, 'multiplier': 1},
        '电力部分直接CO2排放-无CCS': {'source': 'trajectory', 'row': 36, 'multiplier': 1},
        '其它部门': {'source': 'trajectory', 'row': 38, 'multiplier': 1},
        '工业过程排放': {'source': 'trajectory', 'row': 41, 'multiplier': 1},
        '碳捕集埋存量': {'source': 'trajectory', 'row': 45, 'multiplier': 1},
        '碳汇量': {'source': 'trajectory', 'row': 46, 'multiplier': 1},
        
        # 来自数据模板 (template_output.csv)
        '甲烷': {'source': 'template', 'row': 142, 'multiplier': 1},
        '氧化亚氮': {'source': 'template', 'row': 143, 'multiplier': 1},
        'F-Gas': {'source': 'template', 'row': 144, 'multiplier': 1},
    })
    
    # 单位定义
    UNITS: Dict[str, str] = field(default_factory=lambda: {
        '人口': '亿人',
        'GDP年增长率': '%',
        'GDP指数': '2005=1',
        '能源消费量': '亿tce',
        '煤炭': '%',
        '石油': '%',
        '天然气': '%',
        '非化石': '%',
        '能源相关CO2排放量': '亿tce',
        '工业部门直接CO2排放': '亿tCO2',
        '建筑部门直接CO2排放': '亿tCO2',
        '交通部门直接CO2排放': '亿tCO2',
        '电力部分直接CO2排放-无CCS': '亿tCO2',
        '其它部门': '亿tCO2',
        '甲烷': '亿tCO2e',
        '氧化亚氮': '亿tCO2e',
        'F-Gas': '亿tCO2e',
        '工业过程排放': '亿tCO2e',
        '温室气体排放总量': '亿tCO2e',
        '碳捕集埋存量': '亿tCO2e',
        '碳汇量': '亿tCO2e',
        '温室气体净排放': '亿tCO2e',
        '单位能耗CO2强度': 'kgco2/kgce',
        '人均温室气体排放量': 'tCO2e/人',
        '能源消费年增长率': '%',
        'CO2排放年增长率': '%',
        '单位GDP能耗强度年下降率': '%',
        '单位GDPCO2强度年下降率': '%',
        '单位能耗CO2强度年下降率': '%',
        '5年GDP能源强度下降幅度': '%',
        '5年GDPCO2强度下降幅度': '%',
        '能源消费弹性': '',
    })
