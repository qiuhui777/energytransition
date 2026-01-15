# -*- coding: utf-8 -*-
"""能源平衡表公式定义"""

from ...base import BaseFormulas


class BalanceFormulas(BaseFormulas):
    """2019年能源平衡表公式"""
    
    def calculate_terminal_total(self, sector_values: list) -> float:
        """
        计算终端总和
        公式: 终端总和 = SUM(农业 + 工业 + 建筑业 + 交通运输 + 批发零售 + 其他 + 居民生活)
        """
        return self.calculate_sum(sector_values)
    
    def calculate_primary_consumption(self, terminal_total: float, 
                                       electricity: float, 
                                       heating: float) -> float:
        """
        计算一次消费
        公式: 一次消费 = 终端总和 + 电力 + 供热
        """
        return self.calculate_sum([terminal_total, electricity, heating])
