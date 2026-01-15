# -*- coding: utf-8 -*-
"""碳排放轨迹变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TrajectoryVariables:
    """碳排放轨迹变量定义"""
    
    # 年份列表
    YEARS: List[str] = field(default_factory=lambda: [
        '2020', '2025', '2030', '2035', '2040', '2045', '2050', '2055', '2060'
    ])
    
    # ==================== 部门类型 ====================
    SECTORS: List[str] = field(default_factory=lambda: [
        '工业部门', '建筑部门', '交通部门', '电力部门'
    ])
    
    # ==================== 工业部门排放变量 (行2-8) ====================
    INDUSTRY_EMISSION_VARS: List[str] = field(default_factory=lambda: [
        '来自煤炭', '来自石油', '来自天然气', '工业过程CO2', '来自电力', '来自氢能', '工业CCS'
    ])
    
    # ==================== 建筑部门排放变量 (行9-12) ====================
    BUILDING_EMISSION_VARS: List[str] = field(default_factory=lambda: [
        '来自煤炭', '来自石油', '来自天然气', '来自电力'
    ])
    
    # ==================== 交通部门排放变量 (行13-16) ====================
    TRANSPORT_EMISSION_VARS: List[str] = field(default_factory=lambda: [
        '来自煤炭', '来自石油', '来自天然气', '来自电力'
    ])
    
    # ==================== 电力部门排放变量 (行17-20) ====================
    POWER_EMISSION_VARS: List[str] = field(default_factory=lambda: [
        '来自煤炭', '来自天然气', '化石能源CCS', '生物质CCS'
    ])
    
    # ==================== 总排放（含间接排放）变量 (行21-24) ====================
    TOTAL_WITH_INDIRECT_VARS: List[str] = field(default_factory=lambda: [
        '工业(含工业过程）', '建筑', '交通', '电力'
    ])
    
    # ==================== 总排放变量 (行25-28) ====================
    TOTAL_EMISSION_VARS: List[str] = field(default_factory=lambda: [
        '工业(含工业过程）', '建筑', '交通', '电力'
    ])
    
    # ==================== 汇总排放变量 (行29-46) ====================
    SUMMARY_VARS: List[str] = field(default_factory=lambda: [
        '工业排放', '工业直接排放', '工业CCS', '建筑排放', '交通排放',
        '电力排放', '电力直接排放', '电力CCS', '其他排放', 'DACCS',
        '能源相关CO2', '工业过程', '二氧化碳排放', '非二氧化碳', '温室气体排放',
        '碳汇', '温室气体净排放'
    ])
    
    # ==================== CCS变量 (行50-55) ====================
    CCS_VARS: List[str] = field(default_factory=lambda: [
        '煤电CCS', '气电CCS', '生物质CCS', '工业CCS', 'DACCS', '总CCS'
    ])
    
    # ==================== 中和分析变量 (行61-71) ====================
    NEUTRALITY_VARS: List[str] = field(default_factory=lambda: [
        '能源相关CO2', '二氧化碳中和', '温室气体中和',
        'CO2中和', '工业部门', '建筑部门', '交通部门', '电力部门', 'DACCS', '温室气体中和'
    ])
    
    # ==================== 燃烧排放变量 (行75-77) ====================
    COMBUSTION_VARS: List[str] = field(default_factory=lambda: [
        '燃烧排放', '工业CCS', '工业过程排放'
    ])
    
    # ==================== 排放因子 ====================
    EMISSION_FACTORS: Dict[str, float] = field(default_factory=lambda: {
        '煤': 2.66,   # 吨CO2/吨标煤
        '油': 1.73,
        '气': 1.56
    })
    
    # ==================== 单位 ====================
    UNITS: Dict[str, str] = field(default_factory=lambda: {
        'emission': '亿吨CO2',
        'energy': '亿tce',
        'ratio': '%'
    })
