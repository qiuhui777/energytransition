# -*- coding: utf-8 -*-
"""能源平衡表变量定义"""

from dataclasses import dataclass, field
from typing import List, Dict
from ...base import BaseVariables


@dataclass
class BalanceVariables(BaseVariables):
    """2019年能源平衡表变量定义"""
    
    # 终端消费行业（行3-9）
    SECTORS: List[str] = field(default_factory=lambda: [
        '农业',
        '工业', 
        '建筑业',
        '交通运输、仓储和邮政业',
        '批发和零售业、住宿和餐饮业',
        '其他',
        '居民生活'
    ])
    
    # 汇总行
    SUMMARY_ROWS: List[str] = field(default_factory=lambda: [
        '终端总和',
        '电力',
        '供热',
        '一次消费'
    ])
