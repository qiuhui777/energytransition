# -*- coding: utf-8 -*-
"""统计表格分析器

从其他模块读取计算结果，进行汇总分析，生成统计报表
"""

import csv
import os
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import StatisticsVariables
from .formulas import StatisticsFormulas


class StatisticsAnalyzer:
    """统计表格分析器"""
    
    def __init__(self):
        self.variables = StatisticsVariables()
        self.formulas = StatisticsFormulas()
        
        # 数据源
        self.structure_data: Dict[str, Any] = {}
        self.trajectory_data: Dict[str, Any] = {}
        self.template_data: Dict[str, Any] = {}
        self.macro_data: Dict[str, Any] = {}
        
        # 计算结果
        self.results: Dict[str, Any] = {}
    
    # ==================== 数据加载 ====================
    
    def load_from_csv(self, data_dir: str = 'data/output') -> None:
        """从CSV文件加载所有数据源"""
        self.structure_data = self._load_structure_csv(
            os.path.join(data_dir, 'structure_output.csv'))
        self.trajectory_data = self._load_trajectory_csv(
            os.path.join(data_dir, 'trajectory_output.csv'))
        self.template_data = self._load_template_csv(
            os.path.join(data_dir, 'template_output.csv'))
        self.macro_data = self._load_macro_csv(
            os.path.join(data_dir, 'macro_output.csv'))

    def _load_structure_csv(self, filepath: str) -> Dict[str, Any]:
        """加载能源消费结构数据"""
        data = {'years': [], 'items': {}}
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}")
            return data
        
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['类别', '项目', '单位']]
        data['years'] = year_cols
        
        for _, row in df.iterrows():
            category = str(row.get('类别', '')).strip()
            item = str(row.get('项目', '')).strip()
            if not item or item == 'nan':
                continue
            
            key = f"{category}_{item}" if category and category != 'nan' else item
            values = [self._safe_float(row.get(y)) for y in year_cols]
            data['items'][key] = values
        
        return data
    
    def _load_trajectory_csv(self, filepath: str) -> Dict[str, Any]:
        """加载碳排放轨迹数据"""
        data = {'years': [], 'items': {}}
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}")
            return data
        
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['部门', '项目', '单位']]
        data['years'] = year_cols
        
        current_section = ''
        for _, row in df.iterrows():
            section = str(row.get('部门', '')).strip()
            item = str(row.get('项目', '')).strip()
            
            if section and section != 'nan':
                current_section = section
            
            if not item or item == 'nan':
                continue
            
            key = f"{current_section}_{item}" if current_section else item
            values = [self._safe_float(row.get(y)) for y in year_cols]
            data['items'][key] = values
        
        return data

    def _load_template_csv(self, filepath: str) -> Dict[str, Any]:
        """加载数据模板数据"""
        data = {'years': [], 'items': {}}
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}")
            return data
        
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['部门', '类别', '项目', '单位']]
        data['years'] = year_cols
        
        current_dept = ''
        current_cat = ''
        for _, row in df.iterrows():
            dept = str(row.get('部门', '')).strip()
            cat = str(row.get('类别', '')).strip()
            item = str(row.get('项目', '')).strip()
            
            if dept and dept != 'nan':
                current_dept = dept
            if cat and cat != 'nan':
                current_cat = cat
            
            if not item or item == 'nan':
                continue
            
            key = f"{current_dept}_{current_cat}_{item}"
            values = [self._safe_float(row.get(y)) for y in year_cols]
            data['items'][key] = values
        
        return data
    
    def _load_macro_csv(self, filepath: str) -> Dict[str, Any]:
        """加载宏观测算参考数据"""
        data = {'years': [], 'items': {}}
        if not os.path.exists(filepath):
            print(f"警告: 文件不存在 {filepath}")
            return data
        
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c != '项目']
        data['years'] = year_cols
        
        for _, row in df.iterrows():
            item = str(row.get('项目', '')).strip()
            if not item or item == 'nan':
                continue
            
            values = [self._safe_float(row.get(y)) for y in year_cols]
            data['items'][item] = values
        
        return data

    def load_from_modules(self, structure_results: Dict = None,
                          trajectory_results: Dict = None,
                          template_results: Dict = None,
                          macro_results: Dict = None) -> None:
        """从其他模块的计算结果加载数据"""
        if structure_results:
            self.structure_data = structure_results
        if trajectory_results:
            self.trajectory_data = trajectory_results
        if template_results:
            self.template_data = template_results
        if macro_results:
            self.macro_data = macro_results

    # ==================== 辅助函数 ====================
    
    @staticmethod
    def _safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value) or value == '' or str(value) == 'nan':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_year_index(self, years: List[str], target_year: str) -> int:
        """获取年份索引"""
        try:
            return years.index(target_year)
        except ValueError:
            for i, y in enumerate(years):
                if str(y).strip() == str(target_year).strip():
                    return i
            return -1
    
    def _get_value_by_year(self, data: Dict, key: str, year: str) -> float:
        """根据年份获取数据值"""
        items = data.get('items', {})
        years = data.get('years', [])
        
        if key not in items:
            return 0.0
        
        idx = self._get_year_index(years, year)
        if idx < 0 or idx >= len(items[key]):
            return 0.0
        
        return self._safe_float(items[key][idx])
    
    def _get_values_by_years(self, data: Dict, key: str, 
                             target_years: List[str]) -> List[float]:
        """根据多个年份获取数据值"""
        return [self._get_value_by_year(data, key, y) for y in target_years]

    # ==================== 计算方法 ====================
    
    def calculate(self) -> Dict[str, Any]:
        """执行统计表格计算"""
        self.results = {
            'energy_structure': self._calc_energy_structure(),
            'co2_emission': self._calc_co2_emission(),
            'co2_detail': self._calc_co2_detail(),
            'sector_emission': self._calc_sector_emission(),
            'electrification': self._calc_electrification(),
            'electricity': self._calc_electricity(),
            'macro': self._calc_macro(),
        }
        return self.results
    
    def _calc_energy_structure(self) -> Dict[str, Any]:
        """计算第一部分：能源消费量/能源结构（3年份）"""
        years = self.variables.YEARS_3COL
        result = {'years': years, 'items': {}}
        
        result['items']['能源消费量'] = self._get_values_by_years(
            self.structure_data, '总能源消费', years)
        result['items']['煤炭占比'] = self._get_values_by_years(
            self.structure_data, '煤炭', years)
        result['items']['石油占比'] = self._get_values_by_years(
            self.structure_data, '石油', years)
        result['items']['天然气占比'] = self._get_values_by_years(
            self.structure_data, '天然气', years)
        result['items']['非化石能源占比'] = self._get_values_by_years(
            self.structure_data, '非化石能源', years)
        
        return result

    def _calc_co2_emission(self) -> Dict[str, Any]:
        """计算第二部分：CO2排放量/二氧化碳排放结构（3年份）"""
        years = self.variables.YEARS_3COL
        result = {'years': years, 'items': {}}
        
        industry = self._get_values_by_years(self.trajectory_data, '汇总_工业排放', years)
        building = self._get_values_by_years(self.trajectory_data, '汇总_建筑排放', years)
        transport = self._get_values_by_years(self.trajectory_data, '汇总_交通排放', years)
        power = self._get_values_by_years(self.trajectory_data, '汇总_电力排放', years)
        other = self._get_values_by_years(self.trajectory_data, '汇总_其他排放', years)
        daccs = self._get_values_by_years(self.trajectory_data, '汇总_DACCS', years)
        industrial_process = self._get_values_by_years(self.trajectory_data, '汇总_工业过程', years)
        non_co2 = self._get_values_by_years(self.trajectory_data, '汇总_非二氧化碳', years)
        carbon_sink = self._get_values_by_years(self.trajectory_data, '汇总_碳汇', years)
        
        energy_net = []
        for i in range(len(years)):
            val = self.formulas.calc_energy_net_emission(
                industry[i], building[i], transport[i], power[i], other[i], daccs[i])
            energy_net.append(round(val, 4))
        
        co2_total = []
        for i in range(len(years)):
            val = self.formulas.calc_co2_total(energy_net[i], industrial_process[i])
            co2_total.append(round(val, 4))
        
        ghg_net = []
        for i in range(len(years)):
            val = self.formulas.calc_ghg_net_emission(
                energy_net[i], industrial_process[i], non_co2[i], carbon_sink[i])
            ghg_net.append(round(val, 4))
        
        result['items']['CO2排放量'] = co2_total
        result['items']['能源净排放'] = energy_net
        result['items']['工业含CCS'] = [round(v, 4) for v in industry]
        result['items']['建筑'] = [round(v, 4) for v in building]
        result['items']['交通'] = [round(v, 4) for v in transport]
        result['items']['电力含CCS'] = [round(v, 4) for v in power]
        result['items']['其他'] = [round(v, 4) for v in other]
        result['items']['DACCS'] = [round(v, 4) for v in daccs]
        result['items']['工业过程'] = [round(v, 4) for v in industrial_process]
        result['items']['非二氧化碳'] = [round(v, 4) for v in non_co2]
        result['items']['碳汇'] = [round(v, 4) for v in carbon_sink]
        result['items']['温室气体净排放'] = ghg_net
        
        return result

    def _calc_co2_detail(self) -> Dict[str, Any]:
        """计算第三部分：CO2排放详细（6年份）"""
        years = self.variables.YEARS_6COL
        result = {'years': years, 'items': {}}
        
        energy_net = self._get_values_by_years(self.trajectory_data, '汇总_能源相关CO2', years)
        industry_ccs = self._get_values_by_years(self.trajectory_data, '汇总_工业CCS', years)
        power_ccs = self._get_values_by_years(self.trajectory_data, '汇总_电力CCS', years)
        daccs = self._get_values_by_years(self.trajectory_data, '汇总_DACCS', years)
        industrial_process = self._get_values_by_years(self.trajectory_data, '汇总_工业过程', years)
        carbon_sink = self._get_values_by_years(self.trajectory_data, '汇总_碳汇', years)
        non_co2 = self._get_values_by_years(self.trajectory_data, '汇总_非二氧化碳', years)
        
        ccs_total = [round(abs(industry_ccs[i]) + abs(power_ccs[i]) + abs(daccs[i]), 4) for i in range(len(years))]
        energy_gross = [round(energy_net[i] + ccs_total[i], 4) for i in range(len(years))]
        co2_gross = [round(self.formulas.calc_co2_gross(energy_net[i], industrial_process[i]), 4) for i in range(len(years))]
        co2_net = [round(self.formulas.calc_co2_net(co2_gross[i], carbon_sink[i]), 4) for i in range(len(years))]
        ghg_net = [round(self.formulas.calc_ghg_net(co2_net[i], non_co2[i]), 4) for i in range(len(years))]
        
        result['items']['能源净排放'] = [round(v, 4) for v in energy_net]
        result['items']['CCS'] = ccs_total
        result['items']['能源总排放'] = energy_gross
        result['items']['工业过程'] = [round(v, 4) for v in industrial_process]
        result['items']['CO2总排放'] = co2_gross
        result['items']['林业碳汇'] = [round(v, 4) for v in carbon_sink]
        result['items']['CO2净排放'] = co2_net
        result['items']['非二氧化碳'] = [round(v, 4) for v in non_co2]
        result['items']['温室气体净排放'] = ghg_net
        
        return result

    def _calc_sector_emission(self) -> Dict[str, Any]:
        """计算第四部分：能源净排放分部门（6年份）"""
        years = self.variables.YEARS_6COL
        result = {'years': years, 'items': {}}
        
        industry = self._get_values_by_years(self.trajectory_data, '汇总_工业排放', years)
        building = self._get_values_by_years(self.trajectory_data, '汇总_建筑排放', years)
        transport = self._get_values_by_years(self.trajectory_data, '汇总_交通排放', years)
        power = self._get_values_by_years(self.trajectory_data, '汇总_电力排放', years)
        other = self._get_values_by_years(self.trajectory_data, '汇总_其他排放', years)
        daccs = self._get_values_by_years(self.trajectory_data, '汇总_DACCS', years)
        
        energy_net = [round(self.formulas.calc_sector_energy_net(
            industry[i], building[i], transport[i], power[i], other[i], daccs[i]), 4) for i in range(len(years))]
        
        result['items']['能源净排放'] = energy_net
        result['items']['工业含CCS'] = [round(v, 4) for v in industry]
        result['items']['建筑'] = [round(v, 4) for v in building]
        result['items']['交通'] = [round(v, 4) for v in transport]
        result['items']['电力含CCS'] = [round(v, 4) for v in power]
        result['items']['其他'] = [round(v, 4) for v in other]
        result['items']['DACCS'] = [round(v, 4) for v in daccs]
        
        return result

    def _calc_electrification(self) -> Dict[str, Any]:
        """计算第五部分：电气化率（5年份）"""
        years = self.variables.YEARS_5COL
        result = {'years': years, 'items': {}}
        
        result['items']['工业电气化率'] = self._get_values_by_years(self.structure_data, '工业电气化率', years)
        result['items']['建筑电气化率'] = self._get_values_by_years(self.structure_data, '建筑电气化率', years)
        result['items']['交通电气化率'] = self._get_values_by_years(self.structure_data, '交通电气化率', years)
        result['items']['终端电气化率'] = self._get_values_by_years(self.structure_data, '终端电气化率', years)
        
        return result
    
    def _calc_electricity(self) -> Dict[str, Any]:
        """计算第六部分：用电量（5年份）"""
        years = self.variables.YEARS_5COL
        result = {'years': years, 'items': {}}
        
        industry = self._get_values_by_years(self.template_data, '工业部门_终端能源消费量_电力', years)
        building = self._get_values_by_years(self.template_data, '建筑部门_终端能源消费量_电力', years)
        transport = self._get_values_by_years(self.template_data, '交通部门_终端能源消费量_电力', years)
        other = [0.0] * len(years)
        hydrogen = self._get_values_by_years(self.template_data, '氢能_氢能供给_电制氢', years)
        
        total = [round(self.formulas.calc_electricity_total(
            industry[i], building[i], transport[i], other[i], hydrogen[i]), 4) for i in range(len(years))]
        
        result['items']['工业用电量'] = [round(v, 4) for v in industry]
        result['items']['建筑用电量'] = [round(v, 4) for v in building]
        result['items']['交通用电量'] = [round(v, 4) for v in transport]
        result['items']['其他用电量'] = [round(v, 4) for v in other]
        result['items']['电制氢用电量'] = [round(v, 4) for v in hydrogen]
        result['items']['消费总量'] = total
        
        return result

    def _calc_macro(self) -> Dict[str, Any]:
        """计算第七部分：宏观指标（8年份）"""
        years = self.variables.YEARS_8COL
        result = {'years': years, 'items': {}}
        
        gdp_growth = self._get_values_by_years(self.macro_data, 'GDP年增长率', years)
        result['items']['GDP年增长率'] = [round(self.formulas.convert_to_percent(v), 2) for v in gdp_growth]
        result['items']['GDP指数'] = [round(v, 4) for v in self._get_values_by_years(self.macro_data, 'GDP指数', years)]
        result['items']['能源消费量'] = [round(v, 4) for v in self._get_values_by_years(self.macro_data, '能源消费量', years)]
        result['items']['煤炭占比'] = [round(v, 2) for v in self._get_values_by_years(self.macro_data, '煤炭占比', years)]
        result['items']['石油占比'] = [round(v, 2) for v in self._get_values_by_years(self.macro_data, '石油占比', years)]
        result['items']['天然气占比'] = [round(v, 2) for v in self._get_values_by_years(self.macro_data, '天然气占比', years)]
        result['items']['非化石占比'] = [round(v, 2) for v in self._get_values_by_years(self.macro_data, '非化石占比', years)]
        result['items']['单位能耗CO2强度'] = [round(v, 4) for v in self._get_values_by_years(self.macro_data, '单位能耗CO2强度', years)]
        
        co2_intensity_decline = self._get_values_by_years(self.macro_data, '单位能耗CO2强度年下降率', years)
        result['items']['单位能耗CO2强度年下降率'] = [round(self.formulas.convert_to_percent(v), 2) for v in co2_intensity_decline]
        result['items']['CO2排放量'] = [round(v, 4) for v in self._get_values_by_years(self.macro_data, 'CO2排放量', years)]
        
        gdp_energy_decline = self._get_values_by_years(self.macro_data, '单位GDP能耗强度年下降率', years)
        result['items']['单位GDP能耗强度年下降率'] = [round(self.formulas.convert_to_percent(v), 2) for v in gdp_energy_decline]
        
        gdp_co2_decline = self._get_values_by_years(self.macro_data, '单位GDP的CO2强度下降率', years)
        result['items']['单位GDP的CO2强度年下降率'] = [round(self.formulas.convert_to_percent(v), 2) for v in gdp_co2_decline]
        
        decline_2005 = self._get_values_by_years(self.macro_data, '比2005年下降幅度', years)
        result['items']['比2005年下降幅度'] = [round(self.formulas.convert_to_percent(v), 2) for v in decline_2005]
        
        return result

    # ==================== 导出方法 ====================
    
    def export_to_csv(self, filepath: str = 'data/output/statistics_output.csv') -> None:
        """将计算结果导出为CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        rows = []
        
        # 第一部分：能源消费量/能源结构
        section = self.results.get('energy_structure', {})
        years = section.get('years', [])
        rows.append(['温室气体中和', '', ''] + years)
        rows.append(['能源消费量/亿tce', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源消费量', [])])
        rows.append(['能源结构', '煤炭/%', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('煤炭占比', [])])
        rows.append(['', '石油/%', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('石油占比', [])])
        rows.append(['', '天然气/%', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('天然气占比', [])])
        rows.append(['', '非化石能源/%', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('非化石能源占比', [])])
        rows.append([''] * (3 + len(years)))
        
        # 第二部分：CO2排放量/二氧化碳排放结构
        section = self.results.get('co2_emission', {})
        years = section.get('years', [])
        rows.append(['CO2排放量/亿吨', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('CO2排放量', [])])
        rows.append(['二氧化碳排放结构', '能源净排放', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源净排放', [])])
        rows.append(['', '工业（含CCS）', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('工业含CCS', [])])
        rows.append(['', '建筑', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('建筑', [])])
        rows.append(['', '交通', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('交通', [])])
        rows.append(['', '电力（含CCS）', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('电力含CCS', [])])
        rows.append(['', '其他', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('其他', [])])
        rows.append(['', 'DACCS', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('DACCS', [])])
        rows.append(['', '工业过程', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('工业过程', [])])
        rows.append(['非二氧化碳/亿吨', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('非二氧化碳', [])])
        rows.append(['碳汇/亿吨', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('碳汇', [])])
        rows.append(['温室气体净排放/亿吨', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('温室气体净排放', [])])
        rows.append([''] * (3 + len(years)))

        # 第三部分：CO2排放详细
        section = self.results.get('co2_detail', {})
        years = section.get('years', [])
        rows.append(['CO2排放', '', ''] + years)
        rows.append(['', '能源净排放', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源净排放', [])])
        rows.append(['', '其中：CCS', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('CCS', [])])
        rows.append(['', '能源总排放', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源总排放', [])])
        rows.append(['', '工业过程', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('工业过程', [])])
        rows.append(['CO2总排放', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('CO2总排放', [])])
        rows.append(['林业碳汇', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('林业碳汇', [])])
        rows.append(['CO2净排放', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('CO2净排放', [])])
        rows.append(['非二氧化碳', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('非二氧化碳', [])])
        rows.append(['温室气体净排放', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('温室气体净排放', [])])
        rows.append([''] * (3 + len(years)))
        
        # 第四部分：能源净排放分部门
        section = self.results.get('sector_emission', {})
        years = section.get('years', [])
        rows.append(['单位（亿吨CO2)', '', ''] + years)
        rows.append(['能源净排放', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源净排放', [])])
        rows.append(['其中', '工业(含CCS)', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('工业含CCS', [])])
        rows.append(['', '建筑', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('建筑', [])])
        rows.append(['', '交通', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('交通', [])])
        rows.append(['', '电力(含CCS)', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('电力含CCS', [])])
        rows.append(['', '其他', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('其他', [])])
        rows.append(['', 'DACCS', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('DACCS', [])])
        rows.append([''] * (3 + len(years)))

        # 第五部分：电气化率
        section = self.results.get('electrification', {})
        years = section.get('years', [])
        rows.append(['电气化率', '', ''] + years)
        rows.append(['', '工业', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('工业电气化率', [])])
        rows.append(['', '建筑', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('建筑电气化率', [])])
        rows.append(['', '交通', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('交通电气化率', [])])
        rows.append(['', '终端', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('终端电气化率', [])])
        rows.append([''] * (3 + len(years)))
        
        # 第六部分：用电量
        section = self.results.get('electricity', {})
        years = section.get('years', [])
        rows.append(['用电量(万亿kWh)', '', ''] + years)
        rows.append(['', '工业', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('工业用电量', [])])
        rows.append(['', '建筑', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('建筑用电量', [])])
        rows.append(['', '交通', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('交通用电量', [])])
        rows.append(['', '其他', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('其他用电量', [])])
        rows.append(['', '电制氢', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('电制氢用电量', [])])
        rows.append(['', '消费总量', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('消费总量', [])])
        rows.append([''] * (3 + len(years)))
        
        # 第七部分：宏观指标
        section = self.results.get('macro', {})
        years = section.get('years', [])
        rows.append(['项目（单位）', '', ''] + years)
        rows.append(['GDP年增长率(%)', '', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('GDP年增长率', [])])
        rows.append(['GDP指数', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('GDP指数', [])])
        rows.append(['能源消费量(亿tce)', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('能源消费量', [])])
        rows.append(['能源结构', '煤炭(%)', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('煤炭占比', [])])
        rows.append(['', '石油(%)', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('石油占比', [])])
        rows.append(['', '天然气(%)', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('天然气占比', [])])
        rows.append(['', '非化石(%)', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('非化石占比', [])])
        rows.append(['单位能耗CO2强度(kgCO2/kgce)', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('单位能耗CO2强度', [])])
        rows.append(['单位能耗CO2强度年下降率(%/年)', '', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('单位能耗CO2强度年下降率', [])])
        rows.append(['CO2排放量(亿tCO2)', '', ''] + [f"{v:.4f}" for v in section.get('items', {}).get('CO2排放量', [])])
        rows.append(['单位GDP能耗强度年下降率(%/年)', '', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('单位GDP能耗强度年下降率', [])])
        rows.append(['单位GDP的CO2强度年下降率(%/年)', '', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('单位GDP的CO2强度年下降率', [])])
        rows.append(['比2005年下降幅度', '', ''] + [f"{v:.2f}" for v in section.get('items', {}).get('比2005年下降幅度', [])])
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"统计表格结果已导出到: {filepath}")

    def print_results(self) -> None:
        """打印计算结果"""
        print("\n" + "=" * 100)
        print("统计表格分析结果")
        print("=" * 100)
        
        # 第一部分：能源消费量/能源结构
        section = self.results.get('energy_structure', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【温室气体中和 - 能源消费结构】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['能源消费量', '煤炭占比', '石油占比', '天然气占比', '非化石能源占比']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.2f}", end='')
            print()
        
        # 第二部分：CO2排放量
        section = self.results.get('co2_emission', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【CO2排放量/二氧化碳排放结构】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['CO2排放量', '能源净排放', '工业含CCS', '建筑', '交通', 
                     '电力含CCS', '其他', 'DACCS', '工业过程', '非二氧化碳', 
                     '碳汇', '温室气体净排放']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.2f}", end='')
            print()

        # 第三部分：CO2排放详细
        section = self.results.get('co2_detail', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【CO2排放详细】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['能源净排放', 'CCS', '能源总排放', '工业过程', 'CO2总排放',
                     '林业碳汇', 'CO2净排放', '非二氧化碳', '温室气体净排放']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.2f}", end='')
            print()
        
        # 第四部分：能源净排放分部门
        section = self.results.get('sector_emission', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【能源净排放分部门（亿吨CO2）】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['能源净排放', '工业含CCS', '建筑', '交通', '电力含CCS', '其他', 'DACCS']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.2f}", end='')
            print()
        
        # 第五部分：电气化率
        section = self.results.get('electrification', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【电气化率（%）】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['工业电气化率', '建筑电气化率', '交通电气化率', '终端电气化率']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.2f}", end='')
            print()

        # 第六部分：用电量
        section = self.results.get('electricity', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【用电量（万亿kWh）】")
        print(f"{'项目':<20}", end='')
        for y in years:
            print(f"{y:>12}", end='')
        print()
        
        for name in ['工业用电量', '建筑用电量', '交通用电量', '其他用电量', 
                     '电制氢用电量', '消费总量']:
            print(f"{name:<20}", end='')
            for v in items.get(name, []):
                print(f"{v:>12.4f}", end='')
            print()
        
        # 第七部分：宏观指标
        section = self.results.get('macro', {})
        years = section.get('years', [])
        items = section.get('items', {})
        
        print("\n【宏观指标】")
        print(f"{'项目':<30}", end='')
        for y in years:
            print(f"{y:>10}", end='')
        print()
        
        for name in ['GDP年增长率', 'GDP指数', '能源消费量', '煤炭占比', '石油占比',
                     '天然气占比', '非化石占比', '单位能耗CO2强度', 
                     '单位能耗CO2强度年下降率', 'CO2排放量', '单位GDP能耗强度年下降率',
                     '单位GDP的CO2强度年下降率', '比2005年下降幅度']:
            print(f"{name:<30}", end='')
            for v in items.get(name, []):
                print(f"{v:>10.2f}", end='')
            print()
