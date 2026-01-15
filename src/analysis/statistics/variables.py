# -*- coding: utf-8 -*-
"""统计表格变量定义

根据temp12.xlsx中的统计表格结构定义变量名称
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class StatisticsVariables:
    """统计表格变量定义"""
    
    # ==================== 年份定义 ====================
    # 能源消费/CO2排放结构年份（3列）
    YEARS_3COL: List[str] = field(default_factory=lambda: ['2035', '2050', '2060'])
    
    # CO2排放详细年份（6列）
    YEARS_6COL: List[str] = field(default_factory=lambda: ['2020', '2030', '2035', '2040', '2050', '2060'])
    
    # 电气化率/用电量年份（5列）
    YEARS_5COL: List[str] = field(default_factory=lambda: ['2020', '2030', '2035', '2050', '2060'])
    
    # 宏观指标年份（8列）
    YEARS_8COL: List[str] = field(default_factory=lambda: ['2005', '2020', '2025', '2030', '2035', '2040', '2050', '2060'])
    
    # ==================== 第一部分：能源消费量/能源结构 ====================
    ENERGY_STRUCTURE_ITEMS: List[str] = field(default_factory=lambda: [
        '能源消费量', '煤炭占比', '石油占比', '天然气占比', '非化石能源占比',
    ])

    # ==================== 第二部分：CO2排放量/二氧化碳排放结构 ====================
    CO2_EMISSION_ITEMS: List[str] = field(default_factory=lambda: [
        'CO2排放量', '能源净排放', '工业含CCS', '建筑', '交通',
        '电力含CCS', '其他', 'DACCS', '工业过程', '非二氧化碳', '碳汇', '温室气体净排放',
    ])
    
    # ==================== 第三部分：CO2排放详细（6年份） ====================
    CO2_DETAIL_ITEMS: List[str] = field(default_factory=lambda: [
        '能源净排放', 'CCS', '能源总排放', '工业过程', 'CO2总排放',
        '林业碳汇', 'CO2净排放', '非二氧化碳', '温室气体净排放',
    ])
    
    # ==================== 第四部分：能源净排放分部门（6年份） ====================
    SECTOR_EMISSION_ITEMS: List[str] = field(default_factory=lambda: [
        '能源净排放', '工业含CCS', '建筑', '交通', '电力含CCS', '其他', 'DACCS',
    ])
    
    # ==================== 第五部分：电气化率（5年份） ====================
    ELECTRIFICATION_ITEMS: List[str] = field(default_factory=lambda: [
        '工业电气化率', '建筑电气化率', '交通电气化率', '终端电气化率',
    ])
    
    # ==================== 第六部分：用电量（5年份） ====================
    ELECTRICITY_ITEMS: List[str] = field(default_factory=lambda: [
        '工业用电量', '建筑用电量', '交通用电量', '其他用电量', '电制氢用电量', '消费总量',
    ])
    
    # ==================== 第七部分：宏观指标（8年份） ====================
    MACRO_ITEMS: List[str] = field(default_factory=lambda: [
        'GDP年增长率', 'GDP指数', '能源消费量', '煤炭占比', '石油占比',
        '天然气占比', '非化石占比', '单位能耗CO2强度', '单位能耗CO2强度年下降率',
        'CO2排放量', '单位GDP能耗强度年下降率', '单位GDP的CO2强度年下降率', '比2005年下降幅度',
    ])
    
    # ==================== 数据源映射 ====================
    DATA_SOURCES: Dict[str, str] = field(default_factory=lambda: {
        'structure': 'structure_output.csv',
        'trajectory': 'trajectory_output.csv',
        'template': 'template_output.csv',
        'macro': 'macro_output.csv',
    })
