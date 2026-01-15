# -*- coding: utf-8 -*-
"""能源结构计算公式定义"""

from typing import List, Dict


class StructureFormulas:
    """能源结构计算公式"""
    
    def __init__(self):
        # 电力转换系数（万亿kWh -> 亿tce）
        self.electricity_conversion = 1.229
    
    # ==================== 终端消费计算 ====================
    
    def calculate_sector_total(self, coal: float, oil: float, gas: float,
                                electricity: float, hydrogen: float,
                                biomass: float) -> float:
        """
        计算部门总消费
        公式: 总消费 = 煤炭 + 石油 + 天然气 + 电力 + 氢能 + 生物质
        """
        return coal + oil + gas + electricity + hydrogen + biomass
    
    def calculate_terminal_total(self, industry: float, building: float,
                                  transport: float, other: float) -> float:
        """
        计算终端总消费
        公式: 终端总消费 = 工业 + 建筑 + 交通 + 其他
        """
        return industry + building + transport + other
    
    def convert_electricity_to_tce(self, electricity_kwh: float) -> float:
        """
        将电力从万亿kWh转换为亿tce
        公式: 亿tce = 万亿kWh * 1.229
        """
        return electricity_kwh * self.electricity_conversion
    
    # ==================== 电气化率计算 ====================
    
    def calculate_electrification_rate(self, electricity: float, 
                                        total: float) -> float:
        """
        计算电气化率
        公式: 电气化率 = 电力消费 / 总消费
        """
        if total == 0:
            return 0.0
        return electricity / total
    
    def calculate_hydrogen_ratio(self, hydrogen: float, total: float) -> float:
        """
        计算氢能占比
        公式: 氢能占比 = 氢能消费 / 总消费
        """
        if total == 0:
            return 0.0
        return hydrogen / total
    
    # ==================== 一次能源计算 ====================
    
    def calculate_primary_coal(self, industry_coal: float, building_coal: float,
                                transport_coal: float, power_coal: float,
                                hydrogen_coal: float, other_coal: float) -> float:
        """
        计算一次能源煤炭消费
        公式: 煤 = 工业煤 + 建筑煤 + 交通煤 + 电力煤 + 氢能煤 + 其他煤
        """
        return (industry_coal + building_coal + transport_coal + 
                power_coal + hydrogen_coal + other_coal)
    
    def calculate_primary_oil(self, industry_oil: float, building_oil: float,
                               transport_oil: float, power_oil: float,
                               other_oil: float) -> float:
        """
        计算一次能源石油消费
        公式: 油 = 工业油 + 建筑油 + 交通油 + 电力油 + 其他油
        """
        return industry_oil + building_oil + transport_oil + power_oil + other_oil
    
    def calculate_primary_gas(self, industry_gas: float, building_gas: float,
                               transport_gas: float, power_gas: float,
                               other_gas: float) -> float:
        """
        计算一次能源天然气消费
        公式: 气 = 工业气 + 建筑气 + 交通气 + 电力气 + 其他气
        """
        return industry_gas + building_gas + transport_gas + power_gas + other_gas
    
    def calculate_primary_non_fossil(self, wind: float, solar: float,
                                      hydro: float, nuclear: float,
                                      biomass: float) -> float:
        """
        计算一次能源非化石消费
        公式: 非化石 = 风 + 光 + 水 + 核 + 生物质
        """
        return wind + solar + hydro + nuclear + biomass
    
    def calculate_total_primary_energy(self, coal: float, oil: float,
                                        gas: float, non_fossil: float) -> float:
        """
        计算一次能源总消费
        公式: 总能源消费 = 煤 + 油 + 气 + 非化石
        """
        return coal + oil + gas + non_fossil
    
    # ==================== 能源结构占比计算 ====================
    
    def calculate_energy_ratio(self, energy: float, total: float) -> float:
        """
        计算能源占比
        公式: 占比 = 能源消费 / 总消费 * 100
        """
        if total == 0:
            return 0.0
        return energy / total * 100
    
    # ==================== 生物质汇总 ====================
    
    def calculate_total_biomass(self, industry: float, building: float,
                                 transport: float, power: float,
                                 hydrogen: float) -> float:
        """
        计算生物质总消费
        公式: 生物质总量 = 工业 + 建筑 + 交通 + 电力 + 氢能
        """
        return industry + building + transport + power + hydrogen
    
    # ==================== 氢能汇总 ====================
    
    def calculate_total_hydrogen(self, industry: float, building: float,
                                  transport: float) -> float:
        """
        计算氢能总消费
        公式: 氢能总量 = 工业 + 建筑 + 交通
        """
        return industry + building + transport
