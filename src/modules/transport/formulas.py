# -*- coding: utf-8 -*-
"""交通结果公式定义"""

from ...base import BaseFormulas


class TransportFormulas(BaseFormulas):
    """交通结果计算公式"""
    
    def calculate_primary_consumption_total(self, coal: float, oil: float, 
                                            gas: float, biomass: float) -> float:
        """
        计算一次消费总量
        公式: 一次消费 = 煤炭 + 石油 + 天然气 + 生物质
        对应: B1 = SUM(B2:B5)
        """
        return self.calculate_sum([coal, oil, gas, biomass])
    
    def calculate_consumption_total(self, coal: float, oil: float, gas: float,
                                    electricity: float, hydrogen: float,
                                    biomass: float, heat: float) -> float:
        """
        计算消费总量
        公式: 消费总量 = SUM(煤 + 油 + 气 + 电 + 氢 + 生物质 + 热)
        对应: B14 = SUM(B15:B21)
        """
        return self.calculate_sum([coal, oil, gas, electricity, hydrogen, biomass, heat])
    
    def calculate_structure_ratio(self, value: float, total: float) -> float:
        """
        计算消费结构占比
        公式: 占比 = 单项 / 消费总量
        对应: B8 = B15/B14, B9 = B16/B14, etc.
        """
        if total == 0:
            return 0.0
        return value / total
    
    def calculate_other_ratio(self, coal_ratio: float, oil_ratio: float,
                              gas_ratio: float, electricity_ratio: float) -> float:
        """
        计算其他占比
        公式: 其他 = 1 - (煤 + 油 + 气 + 电)
        对应: B12 = 1 - SUM(B8:B11)
        """
        return 1 - self.calculate_sum([coal_ratio, oil_ratio, gas_ratio, electricity_ratio])
    
    def calculate_electricity_kwh(self, electricity_tce: float) -> float:
        """
        计算用电量(亿kWh)
        公式: 用电量 = 电(亿tce) / 1.229
        对应: B23 = B18 / 1.229
        """
        return self.calculate_electricity_quantity(electricity_tce)
    
    def calculate_carbon_emission_total(self, road: float, aviation: float,
                                        railway: float, waterway: float) -> float:
        """
        计算碳排放合计
        公式: 合计 = 道路运输 + 民航运输 + 铁路运输 + 水路运输
        对应: B39 = SUM(B35:B38)
        """
        return self.calculate_sum([road, aviation, railway, waterway])
