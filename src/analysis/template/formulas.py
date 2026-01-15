# -*- coding: utf-8 -*-
"""数据模板计算公式定义"""

from typing import List, Dict, Optional


class TemplateFormulas:
    """数据模板计算公式"""
    
    def __init__(self):
        # 排放因子
        self.emission_factors = {
            '煤': 2.64,
            '油': 2.08,
            '气': 1.63
        }
        # 氢能转换系数: 亿tce -> 万吨
        self.hydrogen_conversion = 0.20477 * 10000
    
    # ==================== CO2排放计算 ====================
    
    def calculate_co2_from_coal(self, coal_consumption: float) -> float:
        """
        计算煤炭CO2排放
        公式: CO2 = 煤炭消费量 * 煤排放因子
        """
        return coal_consumption * self.emission_factors['煤']
    
    def calculate_co2_from_oil(self, oil_consumption: float) -> float:
        """
        计算石油CO2排放
        公式: CO2 = 石油消费量 * 油排放因子
        """
        return oil_consumption * self.emission_factors['油']
    
    def calculate_co2_from_gas(self, gas_consumption: float) -> float:
        """
        计算天然气CO2排放
        公式: CO2 = 天然气消费量 * 气排放因子
        """
        return gas_consumption * self.emission_factors['气']
    
    def calculate_direct_co2_total(self, co2_coal: float, co2_oil: float, 
                                    co2_gas: float) -> float:
        """
        计算直接CO2排放总量
        公式: 直接总排放 = 来自煤炭 + 来自石油 + 来自天然气
        """
        return co2_coal + co2_oil + co2_gas
    
    def calculate_indirect_co2_from_power(self, power_consumption: float,
                                           net_emission: float,
                                           total_power_consumption: float) -> float:
        """
        计算来自电力的间接CO2排放
        公式: 来自电力 = 部门电力消费 * 电力净排放 / 电力消费总量
        """
        if total_power_consumption == 0:
            return 0.0
        ratio = net_emission / total_power_consumption
        if ratio > 0:
            return power_consumption * ratio
        return 0.0
    
    # ==================== 电力部门计算 ====================
    
    def calculate_power_net_emission(self, total_direct: float, 
                                      fossil_ccs: float, 
                                      biomass_ccs: float) -> float:
        """
        计算电力净排放
        公式: 净排放 = 总直接排放 - 化石能源CCS - 生物质CCS
        """
        return total_direct - fossil_ccs - biomass_ccs
    
    def calculate_power_growth_rate(self, current: float, 
                                     previous: float) -> float:
        """
        计算电力增长率
        公式: 增长率 = (当期 - 上期) / 上期
        """
        if previous == 0:
            return 0.0
        return (current - previous) / previous
    
    def calculate_total_power_consumption(self, industry: float, building: float,
                                           transport: float, other: float,
                                           electrolysis: float) -> float:
        """
        计算电力消费总量
        公式: 总量 = 工业 + 建筑 + 交通 + 其他 + 电制氢
        """
        return industry + building + transport + other + electrolysis
    
    def calculate_terminal_power_consumption(self, industry: float, 
                                              building: float,
                                              transport: float) -> float:
        """
        计算电力用于终端部门直接消费
        公式: 终端消费 = 工业 + 建筑 + 交通
        """
        return industry + building + transport
    
    # ==================== 氢能计算 ====================
    
    def calculate_hydrogen_demand_total(self, industry: float, building: float,
                                         transport: float) -> float:
        """
        计算总氢需求
        公式: 总氢需求 = 工业 + 建筑 + 交通
        """
        return industry + building + transport
    
    def calculate_hydrogen_in_tons(self, hydrogen_tce: float) -> float:
        """
        将氢能从亿tce转换为万吨
        公式: 万吨 = 亿tce * 0.20477 * 10000
        """
        return hydrogen_tce * self.hydrogen_conversion
    
    def calculate_green_hydrogen(self, biomass_h2: float, 
                                  electrolysis_h2: float) -> float:
        """
        计算绿氢总量
        公式: 绿氢 = 生物质制氢 + 电制氢
        """
        return biomass_h2 + electrolysis_h2
    
    def calculate_hydrogen_ratio(self, hydrogen_type: float, 
                                  total: float) -> float:
        """
        计算氢能类型占比
        公式: 占比 = 类型产量 / 总产量
        """
        if total == 0:
            return 0.0
        return hydrogen_type / total
    
    # ==================== 生物质计算 ====================
    
    def calculate_biomass_total(self, industry: float, building: float,
                                 transport: float, power: float,
                                 hydrogen: float) -> float:
        """
        计算生物质总计
        公式: 总计 = 工业 + 建筑 + 交通 + 电力 + 氢能
        """
        return industry + building + transport + power + hydrogen
    
    # ==================== 非CO2排放计算 ====================
    
    def calculate_non_co2_total(self, values: List[float]) -> float:
        """
        计算非CO2排放总量
        公式: 总量 = SUM(各项)
        """
        return sum(v for v in values if v is not None)
    
    # ==================== 汇总计算 ====================
    
    def calculate_sector_sum(self, values: List[float]) -> float:
        """
        计算部门汇总
        """
        return sum(v for v in values if v is not None)
    
    def calculate_total_capacity(self, capacities: Dict[str, float]) -> float:
        """
        计算总装机容量
        """
        # 排除'总装机'本身
        return sum(v for k, v in capacities.items() 
                   if k != '总装机' and v is not None)
    
    def calculate_total_generation(self, generations: Dict[str, float]) -> float:
        """
        计算总发电量
        """
        # 排除'总发电量'本身
        return sum(v for k, v in generations.items() 
                   if k != '总发电量' and v is not None)
