# -*- coding: utf-8 -*-
"""宏观测算参考公式定义"""

from typing import List


class MacroFormulas:
    """宏观测算参考计算公式"""
    
    def __init__(self, base_gdp: float = 18.2):
        """
        初始化
        Args:
            base_gdp: 基准年GDP（万亿元），默认2005年为18.2万亿
        """
        self.base_gdp = base_gdp
    
    # ==================== GDP相关计算 ====================
    
    def calculate_gdp_index(self, gdp_growth_rates: List[float], 
                           base_index: float = 1.0) -> List[float]:
        """
        计算GDP指数（累计）
        公式: GDP指数 = 上期指数 * (1 + GDP年增长率)^5
        对应: 行4
        """
        indices = [base_index]
        for rate in gdp_growth_rates:
            new_index = indices[-1] * ((1 + rate) ** 5)
            indices.append(new_index)
        return indices[1:]  # 去掉基准年
    
    def calculate_gdp_from_index(self, gdp_index: float) -> float:
        """
        根据GDP指数计算GDP值
        公式: GDP = 基准GDP * GDP指数
        """
        return self.base_gdp * gdp_index
    
    # ==================== 能源消费相关计算 ====================
    
    def calculate_energy_consumption(self, coal_total: float, oil_total: float,
                                     gas_total: float, non_fossil_total: float) -> float:
        """
        计算能源消费总量
        公式: 能源消费量 = 煤炭总量 + 石油总量 + 天然气总量 + 非化石总量
        对应: 行9 = 行40 + 行48 + 行56 + 行69
        """
        return coal_total + oil_total + gas_total + non_fossil_total
    
    def calculate_energy_structure_ratio(self, energy_value: float, 
                                         total_energy: float) -> float:
        """
        计算能源结构占比
        公式: 占比 = 单项能源 / 能源消费总量 * 100
        对应: 行10 = 行40/行9*100, 行11 = 行48/行9*100, 行12 = 行56/行9*100
        """
        if total_energy == 0:
            return 0.0
        return energy_value / total_energy * 100
    
    def calculate_non_fossil_ratio(self, coal_ratio: float, oil_ratio: float,
                                   gas_ratio: float) -> float:
        """
        计算非化石能源占比
        公式: 非化石占比 = 100 - 煤炭占比 - 石油占比 - 天然气占比
        对应: 行13 = 100 - SUM(行10:行12)
        """
        return 100 - coal_ratio - oil_ratio - gas_ratio
    
    def calculate_energy_index(self, energy_consumption: float, 
                               base_energy: float) -> float:
        """
        计算一次能源指数
        公式: 一次能源指数 = 当期能源消费量 / 基准年能源消费量
        对应: 行5
        """
        if base_energy == 0:
            return 0.0
        return energy_consumption / base_energy
    
    def calculate_energy_elasticity(self, energy_index: float, 
                                    gdp_index: float) -> float:
        """
        计算能源消费弹性
        公式: 能源消费弹性 = 一次能源指数 / GDP指数
        对应: 行7
        """
        if gdp_index == 0:
            return 0.0
        return energy_index / gdp_index
    
    def calculate_energy_growth_rate(self, current_energy: float,
                                     previous_energy: float,
                                     years: int = 5) -> float:
        """
        计算能源消费年增长率
        公式: 年增长率 = (当期/上期)^(1/年数) - 1
        对应: 行8
        """
        if previous_energy == 0:
            return 0.0
        return (current_energy / previous_energy) ** (1 / years) - 1
    
    # ==================== CO2排放相关计算 ====================
    
    def calculate_co2_emission(self, energy_consumption: float,
                               coal_ratio: float, oil_ratio: float,
                               gas_ratio: float, coal_factor: float,
                               oil_factor: float, gas_factor: float,
                               carbon_capture: float = 0) -> float:
        """
        计算CO2排放量
        公式: CO2排放量 = (能源消费量*煤炭占比*煤排放因子 + 
                          能源消费量*石油占比*油排放因子 + 
                          能源消费量*天然气占比*气排放因子) / 100 + 碳捕集量
        对应: 行16
        """
        coal_emission = energy_consumption * coal_ratio * coal_factor / 100
        oil_emission = energy_consumption * oil_ratio * oil_factor / 100
        gas_emission = energy_consumption * gas_ratio * gas_factor / 100
        return coal_emission + oil_emission + gas_emission + carbon_capture
    
    def calculate_co2_index(self, co2_emission: float, 
                            base_co2: float) -> float:
        """
        计算二氧化碳指数
        公式: 二氧化碳指数 = 当期CO2排放量 / 基准年CO2排放量
        对应: 行6
        """
        if base_co2 == 0:
            return 0.0
        return co2_emission / base_co2
    
    def calculate_co2_growth_rate(self, current_co2: float,
                                  previous_co2: float,
                                  years: int = 5) -> float:
        """
        计算CO2排放增长率
        公式: 年增长率 = (当期/上期)^(1/年数) - 1
        对应: 行17
        """
        if previous_co2 == 0:
            return 0.0
        return (current_co2 / previous_co2) ** (1 / years) - 1
    
    def calculate_co2_intensity_per_energy(self, co2_emission: float,
                                           energy_consumption: float) -> float:
        """
        计算单位能耗CO2强度
        公式: 单位能耗CO2强度 = CO2排放量 / 能源消费量
        对应: 行14
        """
        if energy_consumption == 0:
            return 0.0
        return co2_emission / energy_consumption
    
    def calculate_co2_intensity_decline_rate(self, current_intensity: float,
                                             previous_intensity: float,
                                             years: int = 5) -> float:
        """
        计算单位能耗CO2强度年下降率
        公式: 年下降率 = 1 - (当期/上期)^(1/年数)
        对应: 行15
        """
        if previous_intensity == 0:
            return 0.0
        return 1 - (current_intensity / previous_intensity) ** (1 / years)
    
    # ==================== GDP强度相关计算 ====================
    
    def calculate_co2_intensity_per_gdp(self, co2_emission: float,
                                        gdp_index: float) -> float:
        """
        计算GDP的CO2强度
        公式: GDP的CO2强度 = CO2排放量 / (基准GDP * GDP指数)
        对应: 行18
        """
        gdp = self.base_gdp * gdp_index
        if gdp == 0:
            return 0.0
        return co2_emission / gdp
    
    def calculate_gdp_co2_intensity_decline_rate(self, current_intensity: float,
                                                  previous_intensity: float,
                                                  years: int = 5) -> float:
        """
        计算单位GDP的CO2强度下降率（年化）
        公式: 年下降率 = 1 - (当期/上期)^(1/年数)
        对应: 行19
        """
        if previous_intensity == 0:
            return 0.0
        return 1 - (current_intensity / previous_intensity) ** (1 / years)
    
    def calculate_decline_from_base_year(self, current_intensity: float,
                                         base_intensity: float) -> float:
        """
        计算比基准年下降幅度
        公式: 下降幅度 = 1 - 当期强度/基准年强度
        对应: 行20
        """
        if base_intensity == 0:
            return 0.0
        return 1 - current_intensity / base_intensity
    
    def calculate_energy_intensity_per_gdp(self, energy_consumption: float,
                                           gdp_index: float) -> float:
        """
        计算GDP的能耗强度
        公式: GDP的能耗强度 = 能源消费量 / (基准GDP * GDP指数)
        对应: 行21
        """
        gdp = self.base_gdp * gdp_index
        if gdp == 0:
            return 0.0
        return energy_consumption / gdp
    
    def calculate_energy_intensity_5year_decline(self, current_intensity: float,
                                                  previous_intensity: float) -> float:
        """
        计算5年GDP能源强度下降幅度
        公式: 5年下降幅度 = 1 - 当期强度/上期强度
        对应: 行22
        """
        if previous_intensity == 0:
            return 0.0
        return 1 - current_intensity / previous_intensity
    
    def calculate_co2_intensity_5year_decline(self, current_intensity: float,
                                               previous_intensity: float) -> float:
        """
        计算5年GDP的CO2强度下降幅度
        公式: 5年下降幅度 = 1 - 当期强度/上期强度
        对应: 行23
        """
        if previous_intensity == 0:
            return 0.0
        return 1 - current_intensity / previous_intensity
    
    def calculate_energy_intensity_annual_decline(self, current_intensity: float,
                                                   previous_intensity: float,
                                                   years: int = 5) -> float:
        """
        计算单位GDP能耗强度年下降率
        公式: 年下降率 = 1 - (当期/上期)^(1/年数)
        对应: 行24
        """
        if previous_intensity == 0:
            return 0.0
        return 1 - (current_intensity / previous_intensity) ** (1 / years)
    
    # ==================== CO2下降相关计算 ====================
    
    def calculate_co2_annual_decline_rate(self, current_co2: float,
                                          previous_co2: float,
                                          years: int = 5) -> float:
        """
        计算二氧化碳年下降率
        公式: 年下降率 = (当期/上期)^(1/年数) - 1
        对应: 行25
        """
        if previous_co2 == 0:
            return 0.0
        return (current_co2 / previous_co2) ** (1 / years) - 1
    
    def calculate_co2_5year_decline_rate(self, current_co2: float,
                                         previous_co2: float) -> float:
        """
        计算二氧化碳五年累计下降率
        公式: 5年下降率 = 当期/上期 - 1
        对应: 行26
        """
        if previous_co2 == 0:
            return 0.0
        return current_co2 / previous_co2 - 1
    
    def calculate_co2_5year_absolute_decline(self, current_co2: float,
                                              previous_co2: float) -> float:
        """
        计算二氧化碳五年绝对下降量
        公式: 绝对下降量 = 当期 - 上期
        对应: 行27
        """
        return current_co2 - previous_co2
    
    # ==================== 部门汇总计算 ====================
    
    def calculate_sector_total(self, sector_values: List[float]) -> float:
        """
        计算部门总量
        公式: 总量 = SUM(各部门)
        对应: 行40, 行48, 行56, 行65, 行69
        """
        return sum(v for v in sector_values if v is not None)
    
    def calculate_power_coal_ratio(self, power_coal: float, 
                                   total_coal: float) -> float:
        """
        计算电煤占比
        公式: 电煤占比 = 电力煤炭 / 煤炭总量
        对应: 行42
        """
        if total_coal == 0:
            return 0.0
        return power_coal / total_coal
    
    # ==================== 非化石能源计算 ====================
    
    def calculate_biomass_total(self, industry: float, building: float,
                                transport: float, power: float,
                                other: float, hydrogen: float) -> float:
        """
        计算生物质总量
        公式: 生物质总量 = 工业 + 建筑 + 交通 + 电力 + 其他 + 氢能
        对应: 行65
        """
        return sum([industry, building, transport, power, other, hydrogen])
    
    def calculate_non_fossil_total(self, biomass_total: float, hydro: float,
                                   nuclear: float, wind_solar: float) -> float:
        """
        计算非化石能源总量
        公式: 非化石总量 = 生物质总量 + 水能 + 核能 + 风光
        对应: 行69
        """
        return biomass_total + hydro + nuclear + wind_solar
