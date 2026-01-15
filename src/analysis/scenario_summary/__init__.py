# -*- coding: utf-8 -*-
"""2情景数据一览表模块

该模块用于汇总各分析模块的计算结果，生成情景数据一览表。
数据来源：
- 宏观测算参考 (macro_output.csv)
- 能源消费结构 (structure_output.csv)
- 碳排放轨迹 (trajectory_output.csv)
- 数据模板 (template_output.csv)
"""

from .variables import ScenarioSummaryVariables
from .formulas import ScenarioSummaryFormulas
from .analyzer import ScenarioSummaryAnalyzer

__all__ = [
    'ScenarioSummaryVariables',
    'ScenarioSummaryFormulas', 
    'ScenarioSummaryAnalyzer'
]
