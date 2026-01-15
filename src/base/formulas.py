# -*- coding: utf-8 -*-
"""公式基类"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseFormulas(ABC):
    """公式基类，各模块继承此类实现自己的公式"""
    
    def __init__(self, conversion_factor: float = 1.229):
        self.conversion_factor = conversion_factor
    
    def calculate_electricity_quantity(self, electricity_standard_coal: float) -> float:
        """
        计算电量（从标煤转换）
        公式: 电量 = 电(标煤) / 1.229
        """
        if electricity_standard_coal is None or pd.isna(electricity_standard_coal):
            return 0.0
        return electricity_standard_coal / self.conversion_factor
    
    def calculate_sum(self, values: list) -> float:
        """计算求和"""
        valid_values = [v for v in values if v is not None and not pd.isna(v)]
        return sum(valid_values)
