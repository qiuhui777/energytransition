# -*- coding: utf-8 -*-
"""计算器基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd
import json


class BaseCalculator(ABC):
    """计算器基类，各模块继承此类实现自己的计算逻辑"""
    
    def __init__(self):
        self.data = {}
        self.results = {}
    
    def load_from_csv(self, filepath: str) -> None:
        """从CSV文件加载数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_dataframe(df)
    
    def load_from_json(self, filepath: str) -> None:
        """从JSON文件加载数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.load_from_dict(data)
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.data = data
    
    @abstractmethod
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据，子类必须实现"""
        pass
    
    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """执行计算，子类必须实现"""
        pass
    
    @abstractmethod
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """导出结果到CSV，子类必须实现"""
        pass
    
    @abstractmethod
    def print_results(self, results: dict) -> None:
        """打印结果，子类必须实现"""
        pass
    
    @staticmethod
    def safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value) or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
