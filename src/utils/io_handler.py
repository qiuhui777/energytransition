# -*- coding: utf-8 -*-
"""输入输出处理器"""

import os
import csv
import json
import pandas as pd
from typing import Dict, Any


class IOHandler:
    """输入输出处理器"""
    
    @staticmethod
    def ensure_dir(filepath: str) -> None:
        """确保目录存在"""
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    @staticmethod
    def read_csv(filepath: str) -> pd.DataFrame:
        """读取CSV文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        return pd.read_csv(filepath, encoding='utf-8')
    
    @staticmethod
    def read_json(filepath: str) -> Dict[str, Any]:
        """读取JSON文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_csv(data: list, filepath: str, headers: list = None) -> None:
        """写入CSV文件"""
        IOHandler.ensure_dir(filepath)
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            writer.writerows(data)
        print(f"结果已导出到: {filepath}")
    
    @staticmethod
    def write_json(data: dict, filepath: str) -> None:
        """写入JSON文件"""
        IOHandler.ensure_dir(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"结果已导出到: {filepath}")
