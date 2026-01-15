# -*- coding: utf-8 -*-
"""配置加载器"""

import os
import json
from typing import Dict, Any


class ConfigLoader:
    """配置文件加载器"""
    
    DEFAULT_CONFIG = {
        "modules": {
            "balance": {
                "enabled": True,
                "input_type": "csv",
                "input_csv_file": "data/input/energy_balance_input.csv",
                "input_json_file": "data/input/energy_balance_input.json",
                "output_csv_file": "data/output/energy_balance_output.csv"
            },
            "industry": {
                "enabled": False,
                "input_type": "csv",
                "input_csv_file": "data/input/industry_input.csv",
                "output_csv_file": "data/output/industry_output.csv"
            },
            "transport": {
                "enabled": False,
                "input_type": "csv",
                "input_csv_file": "data/input/transport_input.csv",
                "output_csv_file": "data/output/transport_output.csv"
            },
            "building": {
                "enabled": False,
                "input_type": "csv",
                "input_csv_file": "data/input/building_input.csv",
                "output_csv_file": "data/output/building_output.csv"
            },
            "power": {
                "enabled": False,
                "input_type": "csv",
                "input_csv_file": "data/input/power_input.csv",
                "output_csv_file": "data/output/power_output.csv"
            }
        }
    }
    
    def __init__(self, config_file: str = 'config/config.json'):
        self.config_file = config_file
        self.config = {}
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        print(f"已加载配置文件: {self.config_file}")
        return self.config
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print(f"已创建默认配置文件: {self.config_file}")
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """获取指定模块的配置"""
        return self.config.get('modules', {}).get(module_name, {})
    
    def get_enabled_modules(self) -> list:
        """获取所有启用的模块名称"""
        modules = self.config.get('modules', {})
        return [name for name, cfg in modules.items() if cfg.get('enabled', False)]
