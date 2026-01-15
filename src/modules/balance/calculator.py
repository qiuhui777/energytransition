# -*- coding: utf-8 -*-
"""能源平衡表计算器"""

import csv
import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass, field

from ...base import BaseCalculator
from .variables import BalanceVariables
from .formulas import BalanceFormulas


@dataclass
class BalanceData:
    """能源平衡表数据结构"""
    sector_consumption: Dict[str, Dict[str, float]] = field(default_factory=dict)
    electricity: Dict[str, float] = field(default_factory=dict)
    heating: Dict[str, float] = field(default_factory=dict)


class BalanceCalculator(BaseCalculator):
    """能源平衡表计算器"""
    
    def __init__(self):
        super().__init__()
        self.variables = BalanceVariables()
        self.formulas = BalanceFormulas()
        self.balance_data = BalanceData()
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.balance_data.sector_consumption = data.get('sectors', {})
        self.balance_data.electricity = data.get('electricity', {})
        self.balance_data.heating = data.get('heating', {})
    
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据"""
        df.columns = ['行业'] + list(df.columns[1:])
        
        for _, row in df.iterrows():
            sector_name = str(row['行业']).strip().replace('\xa0', '').strip()
            
            if sector_name in self.variables.SECTORS:
                self.balance_data.sector_consumption[sector_name] = {
                    '煤': self.safe_float(row.get('煤', 0)),
                    '油': self.safe_float(row.get('油', 0)),
                    '气': self.safe_float(row.get('气', 0)),
                    '电': self.safe_float(row.get('电', 0))
                }
            elif sector_name == '电力':
                self.balance_data.electricity = {
                    '煤': self.safe_float(row.get('煤', 0)),
                    '油': self.safe_float(row.get('油', 0)),
                    '气': self.safe_float(row.get('气', 0))
                }
            elif sector_name == '供热':
                self.balance_data.heating = {
                    '煤': self.safe_float(row.get('煤', 0)),
                    '油': self.safe_float(row.get('油', 0)),
                    '气': self.safe_float(row.get('气', 0))
                }
    
    def calculate(self) -> Dict[str, Any]:
        """执行所有计算"""
        results = {
            'sector_data': {},
            'terminal_total': {},
            'electricity': {},
            'heating': {},
            'primary_consumption': {}
        }
        
        # 1. 计算各行业的电量
        for sector, values in self.balance_data.sector_consumption.items():
            electricity_value = values.get('电', 0)
            electricity_quantity = self.formulas.calculate_electricity_quantity(electricity_value)
            
            results['sector_data'][sector] = {
                '煤': values.get('煤', 0),
                '油': values.get('油', 0),
                '气': values.get('气', 0),
                '电': electricity_value,
                '电量': round(electricity_quantity, 4)
            }
        
        # 2. 计算终端总和
        for energy_type in ['煤', '油', '气', '电', '电量']:
            if energy_type == '电量':
                values = [results['sector_data'].get(s, {}).get('电量', 0) 
                         for s in self.variables.SECTORS]
            else:
                values = [self.balance_data.sector_consumption.get(s, {}).get(energy_type, 0) 
                         for s in self.variables.SECTORS]
            
            results['terminal_total'][energy_type] = round(
                self.formulas.calculate_terminal_total(values), 4
            )
        
        # 3. 复制电力和供热数据
        results['electricity'] = self.balance_data.electricity.copy()
        results['heating'] = self.balance_data.heating.copy()
        
        # 4. 计算一次消费（仅煤、油、气）
        for energy_type in ['煤', '油', '气']:
            terminal = results['terminal_total'].get(energy_type, 0)
            elec = self.balance_data.electricity.get(energy_type, 0)
            heat = self.balance_data.heating.get(energy_type, 0)
            
            results['primary_consumption'][energy_type] = round(
                self.formulas.calculate_primary_consumption(terminal, elec, heat), 4
            )
        
        return results
    
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        rows = []
        headers = ['项目', '煤', '油', '气', '电', '电量']
        
        for sector in self.variables.SECTORS:
            data = results['sector_data'].get(sector, {})
            rows.append([sector, data.get('煤', ''), data.get('油', ''), 
                        data.get('气', ''), data.get('电', ''), data.get('电量', '')])
        
        rows.append([''] * 6)
        tt = results['terminal_total']
        rows.append(['终端总和', tt.get('煤', ''), tt.get('油', ''), 
                    tt.get('气', ''), tt.get('电', ''), tt.get('电量', '')])
        
        rows.append([''] * 6)
        elec = results['electricity']
        rows.append(['电力', elec.get('煤', ''), elec.get('油', ''), elec.get('气', ''), '', ''])
        
        heat = results['heating']
        rows.append(['供热', heat.get('煤', ''), heat.get('油', ''), heat.get('气', ''), '', ''])
        
        pc = results['primary_consumption']
        rows.append(['一次消费', pc.get('煤', ''), pc.get('油', ''), pc.get('气', ''), '', ''])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        print("\n" + "=" * 70)
        print("2019年能源平衡表计算结果")
        print("=" * 70)
        
        print(f"\n{'项目':<25} {'煤':>10} {'油':>10} {'气':>10} {'电':>10} {'电量':>10}")
        print("-" * 70)
        
        for sector in self.variables.SECTORS:
            data = results['sector_data'].get(sector, {})
            print(f"{sector:<25} {data.get('煤', 0):>10.2f} {data.get('油', 0):>10.2f} "
                  f"{data.get('气', 0):>10.2f} {data.get('电', 0):>10.2f} {data.get('电量', 0):>10.4f}")
        
        print("-" * 70)
        tt = results['terminal_total']
        print(f"{'终端总和':<25} {tt.get('煤', 0):>10.2f} {tt.get('油', 0):>10.2f} "
              f"{tt.get('气', 0):>10.2f} {tt.get('电', 0):>10.2f} {tt.get('电量', 0):>10.4f}")
        
        print("-" * 70)
        elec = results['electricity']
        print(f"{'电力':<25} {elec.get('煤', 0):>10.2f} {elec.get('油', 0):>10.2f} "
              f"{elec.get('气', 0):>10.2f} {'-':>10} {'-':>10}")
        
        heat = results['heating']
        print(f"{'供热':<25} {heat.get('煤', 0):>10.2f} {heat.get('油', 0):>10.2f} "
              f"{heat.get('气', 0):>10.2f} {'-':>10} {'-':>10}")
        
        pc = results['primary_consumption']
        print(f"{'一次消费':<25} {pc.get('煤', 0):>10.2f} {pc.get('油', 0):>10.2f} "
              f"{pc.get('气', 0):>10.2f} {'-':>10} {'-':>10}")
        
        print("=" * 70)
