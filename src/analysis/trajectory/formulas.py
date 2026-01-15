# -*- coding: utf-8 -*-
"""碳排放轨迹计算公式定义"""

from typing import List, Dict


class TrajectoryFormulas:
    """碳排放轨迹计算公式"""
    
    def __init__(self):
        # 排放因子（吨CO2/吨标煤）
        self.emission_factors = {
            '煤': 2.66,
            '油': 1.73,
            '气': 1.56
        }
    
    # ==================== 工业部门排放计算 ====================
    
    def calculate_industry_total_with_indirect(
        self, coal: float, oil: float, gas: float, 
        process_co2: float, electricity: float, hydrogen: float, ccs: float
    ) -> float:
        """
        计算工业部门总排放（含间接排放）
        公式: 工业总排放 = 来自煤炭 + 来自石油 + 来自天然气 + 工业过程CO2 + 来自电力 + 来自氢能 - 工业CCS
        对应Excel: SUM(C2:C8) 即 C21
        """
        return coal + oil + gas + process_co2 + electricity + hydrogen - ccs
    
    def calculate_industry_total_direct(
        self, coal: float, oil: float, gas: float, 
        process_co2: float, electricity: float
    ) -> float:
        """
        计算工业部门总排放（不含间接电力排放）
        公式: 工业总排放 = 来自煤炭 + 来自石油 + 来自天然气 + 工业过程CO2 - 来自电力
        对应Excel: C21 - C6 即 C25
        """
        return coal + oil + gas + process_co2 - electricity
    
    def calculate_industry_emission(
        self, coal: float, oil: float, gas: float, hydrogen: float, ccs: float
    ) -> float:
        """
        计算工业排放（用于汇总）
        公式: 工业排放 = 工业直接排放 + 工业CCS
        对应Excel: C31 + C32 即 C30
        """
        direct = coal + oil + gas + hydrogen
        return direct + ccs
    
    def calculate_industry_direct(
        self, coal: float, oil: float, gas: float, hydrogen: float
    ) -> float:
        """
        计算工业直接排放
        公式: 工业直接排放 = 来自煤炭 + 来自石油 + 来自天然气 + 来自氢能
        对应Excel: C2 + C3 + C4 + C7 即 C31
        """
        return coal + oil + gas + hydrogen
    
    # ==================== 建筑部门排放计算 ====================
    
    def calculate_building_total_with_indirect(
        self, coal: float, oil: float, gas: float, electricity: float
    ) -> float:
        """
        计算建筑部门总排放（含间接排放）
        公式: 建筑总排放 = 来自煤炭 + 来自石油 + 来自天然气 + 来自电力
        对应Excel: SUM(C9:C12) 即 C22
        """
        return coal + oil + gas + electricity
    
    def calculate_building_total_direct(
        self, coal: float, oil: float, gas: float, electricity: float
    ) -> float:
        """
        计算建筑部门总排放（不含间接电力排放）
        公式: 建筑总排放 = SUM(C9:C12) - C12
        对应Excel: C22 - C12 即 C26
        """
        return coal + oil + gas
    
    def calculate_building_emission(
        self, coal: float, oil: float, gas: float
    ) -> float:
        """
        计算建筑排放（用于汇总）
        公式: 建筑排放 = 来自煤炭 + 来自石油 + 来自天然气
        对应Excel: SUM(C9:C11) 即 C33
        """
        return coal + oil + gas
    
    # ==================== 交通部门排放计算 ====================
    
    def calculate_transport_total_with_indirect(
        self, coal: float, oil: float, gas: float, electricity: float
    ) -> float:
        """
        计算交通部门总排放（含间接排放）
        公式: 交通总排放 = 来自煤炭 + 来自石油 + 来自天然气 + 来自电力
        对应Excel: SUM(C13:C16) 即 C23
        """
        return coal + oil + gas + electricity
    
    def calculate_transport_total_direct(
        self, coal: float, oil: float, gas: float, electricity: float
    ) -> float:
        """
        计算交通部门总排放（不含间接电力排放）
        公式: 交通总排放 = SUM(C13:C16) - C16
        对应Excel: C23 - C16 即 C27
        """
        return coal + oil + gas
    
    def calculate_transport_emission(
        self, coal: float, oil: float, gas: float
    ) -> float:
        """
        计算交通排放（用于汇总）
        公式: 交通排放 = 来自煤炭 + 来自石油 + 来自天然气
        对应Excel: SUM(C13:C15) 即 C34
        """
        return coal + oil + gas
    
    # ==================== 电力部门排放计算 ====================
    
    def calculate_power_total_with_indirect(
        self, coal: float, gas: float, fossil_ccs: float, biomass_ccs: float
    ) -> float:
        """
        计算电力部门总排放（含间接排放）
        公式: 电力总排放 = 来自煤炭 + 来自天然气 - 化石能源CCS - 生物质CCS
        对应Excel: SUM(C17:C20) 即 C24
        """
        return coal + gas - fossil_ccs - biomass_ccs
    
    def calculate_power_total_direct(
        self, coal: float, gas: float, fossil_ccs: float, biomass_ccs: float
    ) -> float:
        """
        计算电力部门总排放（不含CCS）
        公式: 电力总排放 = C24
        对应Excel: C24 即 C28
        """
        return coal + gas - fossil_ccs - biomass_ccs
    
    def calculate_power_emission(
        self, direct: float, ccs: float
    ) -> float:
        """
        计算电力排放（用于汇总）
        公式: 电力排放 = 电力直接排放 + 电力CCS
        对应Excel: C36 + C37 即 C35
        """
        return direct + ccs
    
    def calculate_power_direct(
        self, coal: float, gas: float
    ) -> float:
        """
        计算电力直接排放
        公式: 电力直接排放 = 来自煤炭 + 来自天然气
        对应Excel: C17 + C18 即 C36
        """
        return coal + gas
    
    def calculate_power_ccs(
        self, fossil_ccs: float, biomass_ccs: float
    ) -> float:
        """
        计算电力CCS
        公式: 电力CCS = 化石能源CCS + 生物质CCS (取负值)
        对应Excel: C19 + C20 即 C37
        """
        return -(fossil_ccs + biomass_ccs)
    
    # ==================== 其他排放计算 ====================
    
    def calculate_other_emission(
        self, coal: float, oil: float, gas: float
    ) -> float:
        """
        计算其他排放
        公式: 其他排放 = 煤 * 2.66 + 油 * 1.73 + 气 * 1.56
        对应Excel: 能源消费结构!C31*2.66 + 能源消费结构!C32*1.73 + 能源消费结构!C33*1.56 即 C38
        """
        return (coal * self.emission_factors['煤'] + 
                oil * self.emission_factors['油'] + 
                gas * self.emission_factors['气'])
    
    # ==================== 汇总计算 ====================
    
    def calculate_energy_related_co2(
        self, industry: float, building: float, transport: float, 
        power: float, other: float, daccs: float
    ) -> float:
        """
        计算能源相关CO2
        公式: 能源相关CO2 = 工业排放 + 建筑排放 + 交通排放 + 电力排放 + 其他排放 + DACCS
        对应Excel: C30 + C33 + C34 + C35 + C38 + C39 即 C40
        """
        return industry + building + transport + power + other + daccs
    
    def calculate_total_co2(
        self, energy_co2: float, process_co2: float
    ) -> float:
        """
        计算二氧化碳排放
        公式: 二氧化碳排放 = 能源相关CO2 + 工业过程
        对应Excel: C40 + C41 即 C42
        """
        return energy_co2 + process_co2
    
    def calculate_ghg_emission(
        self, co2: float, non_co2: float
    ) -> float:
        """
        计算温室气体排放
        公式: 温室气体排放 = 二氧化碳排放 + 非二氧化碳
        对应Excel: C42 + C43 即 C44
        """
        return co2 + non_co2
    
    def calculate_net_ghg_emission(
        self, ghg: float, carbon_sink: float
    ) -> float:
        """
        计算温室气体净排放
        公式: 温室气体净排放 = 温室气体排放 + 碳汇（碳汇为负值）
        对应Excel: C44 + C45 即 C46
        """
        return ghg + carbon_sink
    
    # ==================== CCS计算 ====================
    
    def calculate_total_ccs(
        self, coal_ccs: float, gas_ccs: float, biomass_ccs: float, 
        industry_ccs: float, daccs: float
    ) -> float:
        """
        计算总CCS
        公式: 总CCS = 煤电CCS + 气电CCS + 生物质CCS + 工业CCS + DACCS
        对应Excel: SUM(F50:F54) 即 F55
        """
        return coal_ccs + gas_ccs + biomass_ccs + industry_ccs + daccs
    
    # ==================== 中和分析计算 ====================
    
    def calculate_sector_neutrality_change(
        self, target_value: float, base_value: float
    ) -> float:
        """
        计算部门中和变化量
        公式: 变化量 = 目标值 - 基准值
        对应Excel: D67 - C67 即 E67
        """
        return target_value - base_value
    
    # ==================== 燃烧排放计算 ====================
    
    def calculate_combustion_emission(
        self, coal: float, oil: float, gas: float, hydrogen: float
    ) -> float:
        """
        计算燃烧排放
        公式: 燃烧排放 = 来自煤炭 + 来自石油 + 来自天然气 + 来自氢能
        对应Excel: C31 即 C76
        """
        return coal + oil + gas + hydrogen
