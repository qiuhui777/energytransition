# -*- coding: utf-8 -*-
"""建筑结果计算器"""

import csv
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ...base import BaseCalculator
from .variables import BuildingVariables
from .formulas import BuildingFormulas


@dataclass
class BuildingData:
    """建筑结果数据结构"""
    # 消费总量输入数据 (行15-21)
    consumption: Dict[str, List[float]] = field(default_factory=dict)
    # 数据中心用电量 (行26)
    data_center_kwh: List[float] = field(default_factory=list)
    # 建筑面积数据 (行31-33)
    building_area: Dict[str, List[float]] = field(default_factory=dict)
    # 人口数据 (行42-43)
    population: Dict[str, List[float]] = field(default_factory=dict)
    # 年份列表
    years: List[str] = field(default_factory=list)


class BuildingCalculator(BaseCalculator):
    """建筑结果计算器"""
    
    def __init__(self):
        super().__init__()
        self.variables = BuildingVariables()
        self.formulas = BuildingFormulas()
        self.building_data = BuildingData()
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.building_data.years = data.get('years', [])
        self.building_data.consumption = data.get('consumption', {})
        self.building_data.data_center_kwh = data.get('data_center_kwh', [])
        self.building_data.building_area = data.get('building_area', {})
        self.building_data.population = data.get('population', {})
    
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据"""
        # 第一列是项目名称，后续列是各年份数据
        df.columns = ['项目'] + list(df.columns[1:])
        self.building_data.years = [str(c) for c in df.columns[1:]]
        
        # 消费总量映射
        consumption_keys = ['煤', '油', '气', '电', '氢', '生物质', '热']
        consumption_data = {k: [] for k in consumption_keys}
        
        # 建筑面积映射
        area_keys = ['城镇住宅', '农村住宅', '公共建筑']
        area_data = {k: [] for k in area_keys}
        
        # 人口映射
        population_keys = ['城市人口', '农村人口']
        population_data = {k: [] for k in population_keys}
        
        data_center_kwh = []
        
        for _, row in df.iterrows():
            item_name = str(row['项目']).strip() if pd.notna(row['项目']) else ''
            
            # 解析数据
            values = [self.safe_float(row[col]) for col in df.columns[1:]]
            
            # 匹配消费总量能源类型
            if item_name in consumption_keys:
                consumption_data[item_name] = values
            # 匹配建筑面积类型
            elif item_name in area_keys:
                area_data[item_name] = values
            # 匹配人口类型
            elif item_name in population_keys:
                population_data[item_name] = values
            # 匹配数据中心用电量
            elif item_name == '数据中心':
                data_center_kwh = values
        
        self.building_data.consumption = consumption_data
        self.building_data.data_center_kwh = data_center_kwh
        self.building_data.building_area = area_data
        self.building_data.population = population_data
    
    def calculate(self) -> Dict[str, Any]:
        """执行所有计算"""
        years = self.building_data.years
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
            'building_area': {  # 建筑面积
                '城镇住宅': [],
                '农村住宅': [],
                '公共建筑': [],
                '合计': []
            },
            'per_capita_area': {  # 人均建筑面积
                '城镇住宅': [],
                '农村住宅': [],
                '公共建筑': []
            },
            'population': {  # 人口
                '城市人口': [],
                '农村人口': []
            }
        }
        
        consumption = self.building_data.consumption
        area = self.building_data.building_area
        pop = self.building_data.population
        data_center = self.building_data.data_center_kwh
        
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
            
            # 用电量 (行23) = 电/1.229 + 数据中心
            dc_kwh = data_center[i] if i < len(data_center) else 0
            elec_kwh = self.formulas.calculate_electricity_kwh(electricity, dc_kwh)
            results['electricity_kwh'].append(round(elec_kwh, 4))
            
            # 建筑面积
            urban_res = area.get('城镇住宅', [0]*num_years)[i] if i < len(area.get('城镇住宅', [])) else 0
            rural_res = area.get('农村住宅', [0]*num_years)[i] if i < len(area.get('农村住宅', [])) else 0
            public_bld = area.get('公共建筑', [0]*num_years)[i] if i < len(area.get('公共建筑', [])) else 0
            
            results['building_area']['城镇住宅'].append(round(urban_res, 4))
            results['building_area']['农村住宅'].append(round(rural_res, 4))
            results['building_area']['公共建筑'].append(round(public_bld, 4))
            
            area_total = self.formulas.calculate_building_area_total(urban_res, rural_res, public_bld)
            results['building_area']['合计'].append(round(area_total, 4))
            
            # 人口
            urban_pop = pop.get('城市人口', [0]*num_years)[i] if i < len(pop.get('城市人口', [])) else 0
            rural_pop = pop.get('农村人口', [0]*num_years)[i] if i < len(pop.get('农村人口', [])) else 0
            
            results['population']['城市人口'].append(round(urban_pop, 4))
            results['population']['农村人口'].append(round(rural_pop, 4))
            
            # 人均建筑面积（通过公式计算）
            # 人均_城镇住宅 = 城镇住宅 / (城市人口 / 10^4)
            pc_urban = self.formulas.calculate_per_capita_urban_residential(urban_res, urban_pop)
            # 人均_农村住宅 = 农村住宅 / (农村人口 / 10^4)
            pc_rural = self.formulas.calculate_per_capita_rural_residential(rural_res, rural_pop)
            # 人均_公共建筑 = 公共建筑 / (城市人口 / 10^4)
            pc_public = self.formulas.calculate_per_capita_public_building(public_bld, urban_pop)
            
            results['per_capita_area']['城镇住宅'].append(round(pc_urban, 4))
            results['per_capita_area']['农村住宅'].append(round(pc_rural, 4))
            results['per_capita_area']['公共建筑'].append(round(pc_public, 4))
        
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
        
        # 建筑面积
        rows.append(['建筑面积(亿m2)'] + [''] * len(years))
        for key in ['城镇住宅', '农村住宅', '公共建筑', '合计']:
            rows.append([key] + results['building_area'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 人均建筑面积
        rows.append(['人均建筑面积(m2)'] + [''] * len(years))
        for key in ['城镇住宅', '农村住宅', '公共建筑']:
            rows.append([key] + results['per_capita_area'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 人口
        rows.append(['人口(万人)'] + [''] * len(years))
        for key in ['城市人口', '农村人口']:
            rows.append([key] + results['population'][key])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 90)
        print("建筑结果计算")
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
        
        # 建筑面积
        print("建筑面积(亿m2)")
        for key in ['城镇住宅', '农村住宅', '公共建筑', '合计']:
            values = results['building_area'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 人均建筑面积
        print("人均建筑面积(m2)")
        for key in ['城镇住宅', '农村住宅', '公共建筑']:
            values = results['per_capita_area'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 90)
        
        # 人口
        print("人口(万人)")
        for key in ['城市人口', '农村人口']:
            values = results['population'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("=" * 90)
