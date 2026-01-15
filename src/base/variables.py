# -*- coding: utf-8 -*-
"""变量定义基类"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class BaseVariables:
    """变量定义基类，各模块继承此类定义自己的变量"""
    
    # 能源类型（通用）
    ENERGY_TYPES: List[str] = field(default_factory=lambda: ['煤', '油', '气', '电', '电量'])
    
    # 电量转换系数
    ELECTRICITY_CONVERSION_FACTOR: float = 1.229
