# -*- coding: utf-8 -*-
"""交通结果计算器"""

import csv
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ...base import BaseCalculator
from .variables import TransportVariables
from .formulas import TransportFormulas


@dataclass
class TransportData:
    """交通结果数据结构"""
    # 消费总量输入数据 (行15-21)
    consumption: Dict[str, List[float]] = field(default_factory=dict)
    # 碳排放数据 (行35-38)
    carbon_emission: Dict[str, List[float]] = field(default_factory=dict)
    # 汽车保有量数据 (行53-56)
    vehicle_stock: Dict[str, List[float]] = field(default_factory=dict)
    # 货运周转量数据 (行69-72)
    freight_turnover: Dict[str, List[float]] = field(default_factory=dict)
    # 客运周转量数据 (行76-79)
    passenger_turnover: Dict[str, List[float]] = field(default_factory=dict)
    # 年份列表
    years: List[str] = field(default_factory=list)


class TransportCalculator(BaseCalculator):
    """交通结果计算器"""
    
    def __init__(self):
        super().__init__()
        self.variables = TransportVariables()
        self.formulas = TransportFormulas()
        self.transport_data = TransportData()
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.transport_data.years = data.get('years', [])
        self.transport_data.consumption = data.get('consumption', {})
        self.transport_data.carbon_emission = data.get('carbon_emission', {})
        self.transport_data.vehicle_stock = data.get('vehicle_stock', {})
        self.transport_data.freight_turnover = data.get('freight_turnover', {})
        self.transport_data.passenger_turnover = data.get('passenger_turnover', {})
    
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据"""
        # 第一列是项目名称，后续列是各年份数据
        df.columns = ['项目'] + list(df.columns[1:])
        self.transport_data.years = [str(c) for c in df.columns[1:]]
        
        # 消费总量映射
        consumption_keys = ['煤', '油', '气', '电', '氢', '生物质', '热']
        consumption_data = {k: [] for k in consumption_keys}
        
        # 碳排放映射
        carbon_keys = ['道路运输', '民航运输', '铁路运输', '水路运输']
        carbon_data = {k: [] for k in carbon_keys}
        
        # 汽车保有量映射
        vehicle_keys = ['燃油车', '天然气汽车', '电动车', '燃料电池汽车']
        vehicle_data = {k: [] for k in vehicle_keys}
        
        # 货运周转量映射 (使用前缀区分)
        freight_keys = ['货运_铁路', '货运_道路', '货运_水路', '货运_民航']
        freight_data = {k: [] for k in freight_keys}
        
        # 客运周转量映射 (使用前缀区分)
        passenger_keys = ['客运_铁路', '客运_道路', '客运_水路', '客运_民航']
        passenger_data = {k: [] for k in passenger_keys}
        
        for _, row in df.iterrows():
            item_name = str(row['项目']).strip() if pd.notna(row['项目']) else ''
            
            # 解析数据
            values = [self.safe_float(row[col]) for col in df.columns[1:]]
            
            # 匹配消费总量能源类型
            if item_name in consumption_keys:
                consumption_data[item_name] = values
            # 匹配碳排放运输类型
            elif item_name in carbon_keys:
                carbon_data[item_name] = values
            # 匹配汽车保有量类型
            elif item_name in vehicle_keys:
                vehicle_data[item_name] = values
            # 匹配货运周转量 (带前缀)
            elif item_name in freight_keys:
                freight_data[item_name] = values
            # 匹配客运周转量 (带前缀)
            elif item_name in passenger_keys:
                passenger_data[item_name] = values
        
        self.transport_data.consumption = consumption_data
        self.transport_data.carbon_emission = carbon_data
        self.transport_data.vehicle_stock = vehicle_data
        self.transport_data.freight_turnover = freight_data
        self.transport_data.passenger_turnover = passenger_data
    
    def calculate(self) -> Dict[str, Any]:
        """执行所有计算"""
        years = self.transport_data.years
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
            'electricity_kwh': [],  # 用电量
            'carbon_emission': {  # 碳排放
                '道路运输': [],
                '民航运输': [],
                '铁路运输': [],
                '水路运输': [],
                '合计': []
            }
        }
        
        consumption = self.transport_data.consumption
        carbon = self.transport_data.carbon_emission
        
        for i in range(num_years):
            # 获取各能源消费量
            coal = consumption.get('煤', [0]*num_years)[i] if i < len(consumption.get('煤', [])) else 0
            oil = consumption.get('油', [0]*num_years)[i] if i < len(consumption.get('油', [])) else 0
            gas = consumption.get('气', [0]*num_years)[i] if i < len(consumption.get('气', [])) else 0
            electricity = consumption.get('电', [0]*num_years)[i] if i < len(consumption.get('电', [])) else 0
            hydrogen = consumption.get('氢', [0]*num_years)[i] if i < len(consumption.get('氢', [])) else 0
            biomass = consumption.get('生物质', [0]*num_years)[i] if i < len(consumption.get('生物质', [])) else 0
            heat = consumption.get('热', [0]*num_years)[i] if i < len(consumption.get('热', [])) else 0
            
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
            
            # 碳排放
            road = carbon.get('道路运输', [0]*num_years)[i] if i < len(carbon.get('道路运输', [])) else 0
            aviation = carbon.get('民航运输', [0]*num_years)[i] if i < len(carbon.get('民航运输', [])) else 0
            railway = carbon.get('铁路运输', [0]*num_years)[i] if i < len(carbon.get('铁路运输', [])) else 0
            waterway = carbon.get('水路运输', [0]*num_years)[i] if i < len(carbon.get('水路运输', [])) else 0
            
            results['carbon_emission']['道路运输'].append(round(road, 4))
            results['carbon_emission']['民航运输'].append(round(aviation, 4))
            results['carbon_emission']['铁路运输'].append(round(railway, 4))
            results['carbon_emission']['水路运输'].append(round(waterway, 4))
            
            carbon_total = self.formulas.calculate_carbon_emission_total(
                road, aviation, railway, waterway
            )
            results['carbon_emission']['合计'].append(round(carbon_total, 4))
        
        # 添加汽车保有量、货运周转量、客运周转量数据（直接复制输入数据）
        vehicle = self.transport_data.vehicle_stock
        freight = self.transport_data.freight_turnover
        passenger = self.transport_data.passenger_turnover
        
        results['vehicle_stock'] = {
            '燃油车': vehicle.get('燃油车', []),
            '天然气汽车': vehicle.get('天然气汽车', []),
            '电动车': vehicle.get('电动车', []),
            '燃料电池汽车': vehicle.get('燃料电池汽车', [])
        }
        
        results['freight_turnover'] = {
            '铁路': freight.get('货运_铁路', []),
            '道路': freight.get('货运_道路', []),
            '水路': freight.get('货运_水路', []),
            '民航': freight.get('货运_民航', [])
        }
        
        results['passenger_turnover'] = {
            '铁路': passenger.get('客运_铁路', []),
            '道路': passenger.get('客运_道路', []),
            '水路': passenger.get('客运_水路', []),
            '民航': passenger.get('客运_民航', [])
        }
        
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
        
        rows.append([''] * (len(years) + 1))
        
        # 碳排放
        rows.append(['碳排放(亿吨)'] + [''] * len(years))
        for key in ['道路运输', '民航运输', '铁路运输', '水路运输', '合计']:
            rows.append([key] + results['carbon_emission'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 汽车保有量
        rows.append(['汽车保有量(亿辆)'] + [''] * len(years))
        for key in ['燃油车', '天然气汽车', '电动车', '燃料电池汽车']:
            data = results.get('vehicle_stock', {}).get(key, [])
            rows.append([key] + data if data else [key] + [''] * len(years))
        
        rows.append([''] * (len(years) + 1))
        
        # 货运周转量
        rows.append(['货运周转量(亿吨公里)'] + [''] * len(years))
        for key in ['铁路', '道路', '水路', '民航']:
            data = results.get('freight_turnover', {}).get(key, [])
            rows.append([key] + data if data else [key] + [''] * len(years))
        
        rows.append([''] * (len(years) + 1))
        
        # 客运周转量
        rows.append(['客运周转量(亿人公里)'] + [''] * len(years))
        for key in ['铁路', '道路', '水路', '民航']:
            data = results.get('passenger_turnover', {}).get(key, [])
            rows.append([key] + data if data else [key] + [''] * len(years))
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 90)
        print("交通结果计算")
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
        
        print("-" * 90)
        
        # 碳排放
        print("碳排放(亿吨)")
        for key in ['道路运输', '民航运输', '铁路运输', '水路运输', '合计']:
            values = results['carbon_emission'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 汽车保有量
        print("汽车保有量(亿辆)")
        for key in ['燃油车', '天然气汽车', '电动车', '燃料电池汽车']:
            values = results.get('vehicle_stock', {}).get(key, [])
            if values:
                row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
                print(row)
        
        print("-" * 90)
        
        # 货运周转量
        print("货运周转量(亿吨公里)")
        for key in ['铁路', '道路', '水路', '民航']:
            values = results.get('freight_turnover', {}).get(key, [])
            if values:
                row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
                print(row)
        
        print("-" * 90)
        
        # 客运周转量
        print("客运周转量(亿人公里)")
        for key in ['铁路', '道路', '水路', '民航']:
            values = results.get('passenger_turnover', {}).get(key, [])
            if values:
                row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
                print(row)
        
        print("=" * 90)
