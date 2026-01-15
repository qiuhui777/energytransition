# -*- coding: utf-8 -*-
"""工业结果计算器"""

import csv
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ...base import BaseCalculator
from .variables import IndustryVariables
from .formulas import IndustryFormulas


@dataclass
class IndustryData:
    """工业结果数据结构"""
    # 消费总量输入数据 (行15-21)
    consumption: Dict[str, List[float]] = field(default_factory=dict)
    # 氢调整 (行25)
    hydrogen_adjusted: List[float] = field(default_factory=list)
    # 氢原始 (行26)
    hydrogen_original: List[float] = field(default_factory=list)
    # 年份列表
    years: List[str] = field(default_factory=list)


class IndustryCalculator(BaseCalculator):
    """工业结果计算器"""
    
    def __init__(self):
        super().__init__()
        self.variables = IndustryVariables()
        self.formulas = IndustryFormulas()
        self.industry_data = IndustryData()
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.industry_data.years = data.get('years', [])
        self.industry_data.consumption = data.get('consumption', {})
        self.industry_data.hydrogen_adjusted = data.get('hydrogen_adjusted', [])
        self.industry_data.hydrogen_original = data.get('hydrogen_original', [])
    
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据"""
        # 第一列是项目名称，后续列是各年份数据
        df.columns = ['项目'] + list(df.columns[1:])
        self.industry_data.years = [str(c) for c in df.columns[1:]]
        
        # 消费总量映射
        consumption_keys = ['煤', '油', '气', '电', '生物质', '热']
        consumption_data = {k: [] for k in consumption_keys}
        hydrogen_adjusted = []
        hydrogen_original = []
        
        for _, row in df.iterrows():
            item_name = str(row['项目']).strip() if pd.notna(row['项目']) else ''
            
            # 解析数据
            values = [self.safe_float(row[col]) for col in df.columns[1:]]
            
            # 直接匹配能源类型
            if item_name in consumption_keys:
                consumption_data[item_name] = values
            elif '氢调整' in item_name:
                hydrogen_adjusted = values
            elif '氢原始' in item_name:
                hydrogen_original = values
        
        self.industry_data.consumption = consumption_data
        self.industry_data.hydrogen_adjusted = hydrogen_adjusted
        self.industry_data.hydrogen_original = hydrogen_original
    
    def calculate(self) -> Dict[str, Any]:
        """执行所有计算"""
        years = self.industry_data.years
        num_years = len(years)
        
        results = {
            'years': years,
            'primary_consumption': {  # 一次消费
                '煤炭': [],
                '石油': [],
                '天然气': [],
                '生物质': [],
                '合计': []
            },
            'consumption_structure': {  # 消费结构
                '煤': [],
                '油': [],
                '气': [],
                '电': [],
                '其他': []
            },
            'consumption_total': {  # 消费总量
                '煤': [],
                '油': [],
                '气': [],
                '电': [],
                '氢': [],
                '生物质': [],
                '热': [],
                '合计': []
            },
            'electricity_kwh': []  # 用电量
        }
        
        consumption = self.industry_data.consumption
        
        for i in range(num_years):
            # 获取各能源消费量
            coal = consumption.get('煤', [0]*num_years)[i] if i < len(consumption.get('煤', [])) else 0
            oil = consumption.get('油', [0]*num_years)[i] if i < len(consumption.get('油', [])) else 0
            gas = consumption.get('气', [0]*num_years)[i] if i < len(consumption.get('气', [])) else 0
            electricity = consumption.get('电', [0]*num_years)[i] if i < len(consumption.get('电', [])) else 0
            biomass = consumption.get('生物质', [0]*num_years)[i] if i < len(consumption.get('生物质', [])) else 0
            heat = consumption.get('热', [0]*num_years)[i] if i < len(consumption.get('热', [])) else 0
            
            # 计算氢 (行19 = 行25 + 行26)
            h2_adj = self.industry_data.hydrogen_adjusted[i] if i < len(self.industry_data.hydrogen_adjusted) else 0
            h2_orig = self.industry_data.hydrogen_original[i] if i < len(self.industry_data.hydrogen_original) else 0
            hydrogen = self.formulas.calculate_hydrogen_total(h2_adj, h2_orig)
            
            # 消费总量各项
            results['consumption_total']['煤'].append(round(coal, 4))
            results['consumption_total']['油'].append(round(oil, 4))
            results['consumption_total']['气'].append(round(gas, 4))
            results['consumption_total']['电'].append(round(electricity, 4))
            results['consumption_total']['氢'].append(round(hydrogen, 4))
            results['consumption_total']['生物质'].append(round(biomass, 4))
            results['consumption_total']['热'].append(round(heat, 4))
            
            # 计算消费总量合计 (行14)
            total = self.formulas.calculate_consumption_total(
                coal, oil, gas, electricity, hydrogen, biomass, heat
            )
            results['consumption_total']['合计'].append(round(total, 4))
            
            # 一次消费 (行2-5来自消费总量)
            results['primary_consumption']['煤炭'].append(round(coal, 4))
            results['primary_consumption']['石油'].append(round(oil, 4))
            results['primary_consumption']['天然气'].append(round(gas, 4))
            results['primary_consumption']['生物质'].append(round(biomass, 4))
            
            # 一次消费合计 (行1)
            primary_total = self.formulas.calculate_primary_consumption_total(
                coal, oil, gas, biomass
            )
            results['primary_consumption']['合计'].append(round(primary_total, 4))
            
            # 消费结构占比 (行8-12)
            coal_ratio = self.formulas.calculate_structure_ratio(coal, total)
            oil_ratio = self.formulas.calculate_structure_ratio(oil, total)
            gas_ratio = self.formulas.calculate_structure_ratio(gas, total)
            elec_ratio = self.formulas.calculate_structure_ratio(electricity, total)
            other_ratio = self.formulas.calculate_other_ratio(
                coal_ratio, oil_ratio, gas_ratio, elec_ratio
            )
            
            results['consumption_structure']['煤'].append(round(coal_ratio, 6))
            results['consumption_structure']['油'].append(round(oil_ratio, 6))
            results['consumption_structure']['气'].append(round(gas_ratio, 6))
            results['consumption_structure']['电'].append(round(elec_ratio, 6))
            results['consumption_structure']['其他'].append(round(other_ratio, 6))
            
            # 用电量 (行23)
            elec_kwh = self.formulas.calculate_electricity_kwh(electricity)
            results['electricity_kwh'].append(round(elec_kwh, 4))
        
        return results
    
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['项目'] + years
        
        # 一次消费
        rows.append(['一次消费(亿tce)'] + [''] * len(years))
        for key in ['煤炭', '石油', '天然气', '生物质', '合计']:
            rows.append([key] + results['primary_consumption'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 消费结构（转换为百分比格式）
        rows.append(['消费结构'] + [''] * len(years))
        for key in ['煤', '油', '气', '电', '其他']:
            # 将小数转换为百分比字符串
            pct_values = [f"{v*100:.2f}%" for v in results['consumption_structure'][key]]
            rows.append([key] + pct_values)
        
        rows.append([''] * (len(years) + 1))
        
        # 消费总量
        rows.append(['消费总量(亿tce)'] + [''] * len(years))
        for key in ['煤', '油', '气', '电', '氢', '生物质', '热', '合计']:
            rows.append([key] + results['consumption_total'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 用电量
        rows.append(['用电量(亿kWh)'] + results['electricity_kwh'])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 90)
        print("工业结果计算")
        print("=" * 90)
        
        # 打印表头
        header = f"{'项目':<20}" + "".join([f"{y:>12}" for y in years])
        print(header)
        print("-" * 90)
        
        # 一次消费
        print("一次消费(亿tce)")
        for key in ['煤炭', '石油', '天然气', '生物质', '合计']:
            values = results['primary_consumption'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 消费结构
        print("消费结构")
        for key in ['煤', '油', '气', '电', '其他']:
            values = results['consumption_structure'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4%}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 消费总量
        print("消费总量(亿tce)")
        for key in ['煤', '油', '气', '电', '氢', '生物质', '热', '合计']:
            values = results['consumption_total'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 用电量
        values = results['electricity_kwh']
        row = f"{'用电量(亿kWh)':<20}" + "".join([f"{v:>12.4f}" for v in values])
        print(row)
        
        print("=" * 90)
