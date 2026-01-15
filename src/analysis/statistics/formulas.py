# -*- coding: utf-8 -*-
"""统计表格计算公式定义

根据temp12.xlsx中的统计表格计算公式定义
"""

from typing import List, Dict, Optional


class StatisticsFormulas:
    """统计表格计算公式"""
    
    def __init__(self):
        pass
    
    # ==================== 第二部分：CO2排放量计算 ====================
    
    def calc_co2_total(self, energy_net: float, industrial_process: float) -> float:
        """计算CO2排放量: CO2排放量 = 能源净排放 + 工业过程"""
        return energy_net + industrial_process
    
    def calc_energy_net_emission(self, industry: float, building: float, 
                                  transport: float, power: float,
                                  other: float, daccs: float) -> float:
        """计算能源净排放: 能源净排放 = 工业 + 建筑 + 交通 + 电力 + 其他 + DACCS"""
        return industry + building + transport + power + other + daccs
    
    def calc_ghg_net_emission(self, energy_net: float, industrial_process: float,
                               non_co2: float, carbon_sink: float) -> float:
        """计算温室气体净排放"""
        return energy_net + industrial_process + non_co2 + carbon_sink
    
    # ==================== 第三部分：CO2排放详细计算 ====================
    
    def calc_ccs_total(self, industry_ccs: float, power_ccs: float, 
                       daccs: float) -> float:
        """计算CCS总量"""
        return industry_ccs + power_ccs + daccs
    
    def calc_energy_gross_emission(self, energy_net: float, ccs: float) -> float:
        """计算能源总排放"""
        return energy_net - ccs
    
    def calc_co2_gross(self, energy_net: float, industrial_process: float) -> float:
        """计算CO2总排放"""
        return energy_net + industrial_process

    def calc_co2_net(self, co2_gross: float, carbon_sink: float) -> float:
        """计算CO2净排放"""
        return co2_gross + carbon_sink
    
    def calc_ghg_net(self, co2_net: float, non_co2: float) -> float:
        """计算温室气体净排放"""
        return co2_net + non_co2
    
    # ==================== 第四部分：能源净排放分部门计算 ====================
    
    def calc_sector_energy_net(self, industry: float, building: float,
                                transport: float, power: float,
                                other: float, daccs: float) -> float:
        """计算能源净排放（分部门汇总）"""
        return industry + building + transport + power + other + daccs
    
    # ==================== 第五部分：用电量计算 ====================
    
    def calc_electricity_total(self, industry: float, building: float,
                                transport: float, other: float,
                                hydrogen: float) -> float:
        """计算用电量总计"""
        return industry + building + transport + other + hydrogen
    
    # ==================== 第六部分：宏观指标计算 ====================
    
    def convert_to_percent(self, value: float) -> float:
        """将小数转换为百分比"""
        return value * 100
    
    # ==================== 辅助函数 ====================
    
    def safe_get(self, data: Dict, key: str, default: float = 0.0) -> float:
        """安全获取字典值"""
        value = data.get(key, default)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_get_list(self, data: List, index: int, default: float = 0.0) -> float:
        """安全获取列表值"""
        if index < 0 or index >= len(data):
            return default
        value = data[index]
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
