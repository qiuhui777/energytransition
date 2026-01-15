# -*- coding: utf-8 -*-
"""2030年和2050年平衡表计算公式定义"""

from typing import Dict, List, Optional


class BalanceFormulas:
    """2030年和2050年平衡表计算公式"""
    
    def __init__(self):
        # 电热当量转换系数
        self.electricity_conversion = 1.229  # 万亿千瓦时 -> 亿tce
        
        # CO2排放因子（亿吨CO2/亿tce）
        self.co2_factors = {
            '煤炭': 2.66,
            '石油': 1.73,
            '天然气': 1.56
        }
    
    # ==================== 电力转换计算 ====================
    
    def calculate_electricity_tce(self, electricity_twh: float) -> float:
        """
        计算电热当量
        公式: 电热当量 = 电量 * 1.229
        对应Excel: E4 = D4 * 1.229
        
        Args:
            electricity_twh: 电量（万亿千瓦时）
        Returns:
            电热当量（亿tce）
        """
        return electricity_twh * self.electricity_conversion
    
    # ==================== 一次能源消费计算 ====================
    
    def calculate_primary_energy_subtotal(
        self, coal: float, oil: float, gas: float, non_fossil: float
    ) -> float:
        """
        计算一次能源消费小计
        公式: 小计 = 煤炭 + 石油 + 天然气 + 非化石能源
        对应Excel: K4 = SUM(G4:J4)
        """
        return coal + oil + gas + non_fossil
    
    # ==================== 终端能源消费计算 ====================
    
    def calculate_terminal_energy(
        self, electricity_tce: float, hydrogen: float,
        coal: float, oil: float, gas: float, non_fossil: float
    ) -> float:
        """
        计算终端能源消费
        公式: 终端能源消费 = 电热当量 + 氢能 + 煤炭 + 石油 + 天然气 + 非化石能源
        对应Excel: L4 = SUM(E4, F4, G4, H4, I4, J4)
        """
        return electricity_tce + hydrogen + coal + oil + gas + non_fossil
    
    # ==================== 终端消费结构计算 ====================
    
    def calculate_terminal_structure(
        self, sector_terminal: float, total_terminal: float
    ) -> float:
        """
        计算终端消费结构占比
        公式: 终端消费结构 = 部门终端能源消费 / 总计终端能源消费
        对应Excel: M4 = L4 / $L$8
        """
        if total_terminal == 0:
            return 0.0
        return sector_terminal / total_terminal
    
    # ==================== CO2直接排放计算 ====================
    
    def calculate_co2_emission(
        self, coal: float, oil: float, gas: float
    ) -> float:
        """
        计算CO2直接排放
        公式: CO2 = 煤炭 * 2.66 + 石油 * 1.73 + 天然气 * 1.56
        对应Excel: N4 = G4*2.66 + H4*1.73 + I4*1.56
        """
        return (coal * self.co2_factors['煤炭'] + 
                oil * self.co2_factors['石油'] + 
                gas * self.co2_factors['天然气'])
    
    # ==================== 汇总计算 ====================
    
    def calculate_sector_sum(self, values: List[float]) -> float:
        """
        计算部门汇总（工业+建筑+交通+其它）
        公式: 总计 = SUM(各部门)
        对应Excel: D8 = SUM(D4:D7)
        """
        return sum(v for v in values if v is not None)
    
    def calculate_electricity_total(
        self, terminal_total: float, hydrogen_supply: float
    ) -> float:
        """
        计算电力供应总量
        公式: 电力供应 = 终端总计 + 氢能供应
        对应Excel: D10 = D8 + D9
        """
        return terminal_total + hydrogen_supply
    
    # ==================== 一次能源消费汇总 ====================
    
    def calculate_primary_energy_total(
        self, terminal_total: float, hydrogen_supply: float, power_supply: float
    ) -> float:
        """
        计算一次能源消费总量
        公式: 一次能源消费 = 终端总计 + 氢能供应 + 电力供应
        对应Excel: G11 = SUM(G8:G10)
        """
        return terminal_total + hydrogen_supply + power_supply
    
    # ==================== 一次能源结构计算 ====================
    
    def calculate_primary_structure(
        self, energy_type: float, total: float
    ) -> float:
        """
        计算一次能源结构占比
        公式: 结构占比 = 能源类型 / 一次能源总计
        对应Excel: G12 = G11 / SUM($G11:$J11)
        """
        if total == 0:
            return 0.0
        return energy_type / total
    
    # ==================== 碳排放汇总计算 ====================
    
    def calculate_total_co2_emission(
        self, terminal_co2: float, hydrogen_co2: float, power_co2: float
    ) -> float:
        """
        计算CO2直接排放总量
        公式: CO2总量 = 终端CO2 + 氢能供应CO2 + 电力供应CO2
        对应Excel: N11 = SUM(N8:N10)
        """
        return terminal_co2 + hydrogen_co2 + power_co2
    
    # ==================== CCS计算 ====================
    
    def calculate_ccs_total(
        self, power_ccs: float, industry_ccs: float, daccs: float
    ) -> float:
        """
        计算CCS总量
        公式: CCS = 电力CCS + 工业CCS + DACCS
        对应Excel: N15 = 碳排放轨迹!C37 + 碳排放轨迹!C32 + 碳排放轨迹!C39
        """
        return power_ccs + industry_ccs + daccs
    
    # ==================== 能源相关CO2计算 ====================
    
    def calculate_energy_related_co2(
        self, total_co2: float, ccs: float
    ) -> float:
        """
        计算能源相关CO2
        公式: 能源相关CO2 = CO2总量 + CCS（CCS为负值）
        对应Excel: N17 = N11 + N15
        """
        return total_co2 + ccs
    
    # ==================== 温室气体排放计算 ====================
    
    def calculate_ghg_emission(
        self, process_co2: float, non_co2: float, energy_co2: float
    ) -> float:
        """
        计算温室气体排放
        公式: 温室气体排放 = 工业过程 + 非二氧化碳 + 能源相关CO2
        对应Excel: N18 = N13 + N14 + N17
        """
        return process_co2 + non_co2 + energy_co2
