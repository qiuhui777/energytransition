# -*- coding: utf-8 -*-
"""情景数据一览表计算公式定义

基于temp11.xlsx中的情景数据一览表计算公式sheet定义所有计算逻辑
"""

from typing import List, Optional


class ScenarioSummaryFormulas:
    """情景数据一览表计算公式"""
    
    def __init__(self):
        pass
    
    # ==================== 能源相关CO2排放量计算 (行10) ====================
    def calculate_energy_co2_emission(
        self,
        industry_co2: float,
        building_co2: float,
        transport_co2: float,
        power_co2: float,
        other_co2: float,
        other_emission: float  # 碳排放轨迹!C37+C32+C39 对应的其他排放
    ) -> float:
        """
        计算能源相关CO2排放量
        公式: SUM(工业+建筑+交通+电力+其它) + 其他排放
        对应Excel: SUM('情景数据一览表'!C11:'情景数据一览表'!C15)+'情景数据一览表'!C21
        """
        return industry_co2 + building_co2 + transport_co2 + power_co2 + other_co2 + other_emission
    
    # ==================== 其它部门排放计算 (行21) ====================
    def calculate_other_emission(
        self,
        trajectory_37: float,  # 碳排放轨迹!C37
        trajectory_32: float,  # 碳排放轨迹!C32
        trajectory_39: float   # 碳排放轨迹!C39
    ) -> float:
        """
        计算其它部门排放
        公式: 碳排放轨迹!C37 + 碳排放轨迹!C32 + 碳排放轨迹!C39
        """
        return trajectory_37 + trajectory_32 + trajectory_39
    
    # ==================== 温室气体排放总量计算 (行20) ====================
    def calculate_total_ghg_emission(
        self,
        industry_co2: float,
        building_co2: float,
        transport_co2: float,
        power_co2: float,
        other_co2: float,
        methane: float,
        n2o: float,
        f_gas: float,
        industrial_process: float,
        other_emission: float
    ) -> float:
        """
        计算温室气体排放总量
        公式: SUM(C11:C19) + C21
        """
        return (industry_co2 + building_co2 + transport_co2 + power_co2 + 
                other_co2 + methane + n2o + f_gas + industrial_process + other_emission)
    
    # ==================== 单位能耗CO2强度计算 (行24) ====================
    def calculate_co2_intensity_per_energy(
        self,
        energy_co2: float,
        energy_consumption: float
    ) -> float:
        """
        计算单位能耗CO2强度
        公式: 能源相关CO2排放量 / 能源消费量
        对应Excel: '情景数据一览表'!C10/'情景数据一览表'!C5
        单位: kgCO2/kgce (由于输入单位为亿tCO2和亿tce，结果直接为kgCO2/kgce)
        """
        if energy_consumption == 0:
            return 0.0
        return energy_co2 / energy_consumption
    
    # ==================== 人均温室气体排放量计算 (行25) ====================
    def calculate_ghg_per_capita(
        self,
        total_ghg: float,
        population: float
    ) -> float:
        """
        计算人均温室气体排放量
        公式: 温室气体排放总量 / 人口
        对应Excel: '情景数据一览表'!C20/'情景数据一览表'!C2
        单位: tCO2e/人 (亿tCO2e / 亿人 = tCO2e/人)
        """
        if population == 0:
            return 0.0
        return total_ghg / population
    
    # ==================== 能源消费年增长率计算 (行26) ====================
    def calculate_energy_growth_rate(
        self,
        current_energy: float,
        previous_energy: float,
        years_interval: int = 5
    ) -> float:
        """
        计算能源消费年增长率
        公式: (当期能源消费/上期能源消费 - 1) / 年数间隔 * 100
        对应Excel: ('情景数据一览表'!D5/'情景数据一览表'!C5-1)/5*100
        """
        if previous_energy == 0:
            return 0.0
        return ((current_energy / previous_energy) - 1) / years_interval * 100
    
    # ==================== CO2排放年增长率计算 (行27) ====================
    def calculate_co2_growth_rate(
        self,
        current_co2: float,
        previous_co2: float,
        years_interval: int = 5
    ) -> float:
        """
        计算CO2排放年增长率
        公式: (当期CO2排放/上期CO2排放 - 1) / 年数间隔 * 100
        对应Excel: ('情景数据一览表'!D10/'情景数据一览表'!C10-1)/5*100
        """
        if previous_co2 == 0:
            return 0.0
        return ((current_co2 / previous_co2) - 1) / years_interval * 100
    
    # ==================== 单位GDP能耗强度年下降率计算 (行28) ====================
    def calculate_gdp_energy_intensity_decline(
        self,
        current_energy: float,
        previous_energy: float,
        current_gdp: float,
        previous_gdp: float,
        years_interval: int = 5
    ) -> float:
        """
        计算单位GDP能耗强度年下降率
        公式: (1 - (当期能源*上期GDP)/(当期GDP*上期能源)) / 年数间隔 * 100
        对应Excel: (1-('情景数据一览表'!D5*'情景数据一览表'!C4)/('情景数据一览表'!D4*'情景数据一览表'!C5))/5*100
        """
        if current_gdp == 0 or previous_energy == 0:
            return 0.0
        ratio = (current_energy * previous_gdp) / (current_gdp * previous_energy)
        return (1 - ratio) / years_interval * 100
    
    # ==================== 单位GDP CO2强度年下降率计算 (行29) ====================
    def calculate_gdp_co2_intensity_decline(
        self,
        current_co2: float,
        previous_co2: float,
        current_gdp: float,
        previous_gdp: float,
        years_interval: int = 5
    ) -> float:
        """
        计算单位GDP CO2强度年下降率
        公式: (1 - (当期CO2*上期GDP)/(当期GDP*上期CO2)) / 年数间隔 * 100
        对应Excel: (1-('情景数据一览表'!D10*'情景数据一览表'!C4)/('情景数据一览表'!D4*'情景数据一览表'!C10))/5*100
        """
        if current_gdp == 0 or previous_co2 == 0:
            return 0.0
        ratio = (current_co2 * previous_gdp) / (current_gdp * previous_co2)
        return (1 - ratio) / years_interval * 100
    
    # ==================== 单位能耗CO2强度年下降率计算 (行30) ====================
    def calculate_energy_co2_intensity_decline(
        self,
        current_co2: float,
        previous_co2: float,
        current_energy: float,
        previous_energy: float,
        years_interval: int = 5
    ) -> float:
        """
        计算单位能耗CO2强度年下降率
        公式: (1 - (当期CO2*上期能源)/(当期能源*上期CO2)) / 年数间隔 * 100
        对应Excel: (1-('情景数据一览表'!D10*'情景数据一览表'!C5)/('情景数据一览表'!D5*'情景数据一览表'!C10))/5*100
        """
        if current_energy == 0 or previous_co2 == 0:
            return 0.0
        ratio = (current_co2 * previous_energy) / (current_energy * previous_co2)
        return (1 - ratio) / years_interval * 100
    
    # ==================== 5年GDP能源强度下降幅度计算 (行31) ====================
    def calculate_gdp_energy_intensity_5y_decline(
        self,
        current_energy: float,
        previous_energy: float,
        current_gdp: float,
        previous_gdp: float
    ) -> float:
        """
        计算5年GDP能源强度下降幅度
        公式: (1 - (当期能源*上期GDP)/(当期GDP*上期能源)) * 100
        对应Excel: (1-('情景数据一览表'!D5*'情景数据一览表'!C4)/('情景数据一览表'!D4*'情景数据一览表'!C5))*100
        """
        if current_gdp == 0 or previous_energy == 0:
            return 0.0
        ratio = (current_energy * previous_gdp) / (current_gdp * previous_energy)
        return (1 - ratio) * 100
    
    # ==================== 5年GDP CO2强度下降幅度计算 (行32) ====================
    def calculate_gdp_co2_intensity_5y_decline(
        self,
        current_co2: float,
        previous_co2: float,
        current_gdp: float,
        previous_gdp: float
    ) -> float:
        """
        计算5年GDP CO2强度下降幅度
        公式: (1 - (当期CO2*上期GDP)/(当期GDP*上期CO2)) * 100
        对应Excel: (1-('情景数据一览表'!D10*'情景数据一览表'!C4)/('情景数据一览表'!D4*'情景数据一览表'!C10))*100
        """
        if current_gdp == 0 or previous_co2 == 0:
            return 0.0
        ratio = (current_co2 * previous_gdp) / (current_gdp * previous_co2)
        return (1 - ratio) * 100
    
    # ==================== 能源消费弹性计算 (行33) ====================
    def calculate_energy_elasticity(
        self,
        energy_growth_rate: float,
        gdp_growth_rate: float
    ) -> float:
        """
        计算能源消费弹性
        公式: 能源消费年增长率 / GDP年增长率
        对应Excel: '情景数据一览表'!D26/'情景数据一览表'!D3
        """
        if gdp_growth_rate == 0:
            return 0.0
        return energy_growth_rate / gdp_growth_rate
    
    # ==================== 温室气体净排放计算 (行23) ====================
    def calculate_net_ghg_emission(
        self,
        total_ghg: float,
        ccs_amount: float,
        carbon_sink: float
    ) -> float:
        """
        计算温室气体净排放
        公式: 温室气体排放总量 - 碳捕集埋存量 - 碳汇量
        注：根据实际情况，可能需要调整计算逻辑
        """
        return total_ghg - ccs_amount - carbon_sink
    
    # ==================== 2030年相对2025年下降比例计算 (N10) ====================
    def calculate_2030_decline_ratio(
        self,
        value_2030: float,
        baseline: float = 110
    ) -> float:
        """
        计算2030年相对基准的下降比例
        公式: (110 - 2030年值) / 110
        对应Excel: (110-'情景数据一览表'!F10)/110
        """
        return (baseline - value_2030) / baseline
