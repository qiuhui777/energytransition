# -*- coding: utf-8 -*-
"""碳排放轨迹分析器"""

import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import TrajectoryVariables
from .formulas import TrajectoryFormulas


@dataclass
class SectorEmissionData:
    """部门排放数据"""
    coal: List[float] = field(default_factory=list)      # 来自煤炭
    oil: List[float] = field(default_factory=list)       # 来自石油
    gas: List[float] = field(default_factory=list)       # 来自天然气
    electricity: List[float] = field(default_factory=list)  # 来自电力
    hydrogen: List[float] = field(default_factory=list)  # 来自氢能


@dataclass
class IndustryEmissionData(SectorEmissionData):
    """工业部门排放数据"""
    process_co2: List[float] = field(default_factory=list)  # 工业过程CO2
    ccs: List[float] = field(default_factory=list)          # 工业CCS


@dataclass
class PowerEmissionData:
    """电力部门排放数据"""
    coal: List[float] = field(default_factory=list)         # 来自煤炭
    gas: List[float] = field(default_factory=list)          # 来自天然气
    fossil_ccs: List[float] = field(default_factory=list)   # 化石能源CCS
    biomass_ccs: List[float] = field(default_factory=list)  # 生物质CCS


@dataclass
class CCSData:
    """CCS数据"""
    coal_power: List[float] = field(default_factory=list)   # 煤电CCS
    gas_power: List[float] = field(default_factory=list)    # 气电CCS
    biomass: List[float] = field(default_factory=list)      # 生物质CCS
    industry: List[float] = field(default_factory=list)     # 工业CCS
    daccs: List[float] = field(default_factory=list)        # DACCS


@dataclass
class OtherEmissionData:
    """其他排放数据"""
    coal: List[float] = field(default_factory=list)         # 煤炭消费
    oil: List[float] = field(default_factory=list)          # 石油消费
    gas: List[float] = field(default_factory=list)          # 天然气消费
    non_co2: List[float] = field(default_factory=list)      # 非二氧化碳
    carbon_sink: List[float] = field(default_factory=list)  # 碳汇


class TrajectoryAnalyzer:
    """碳排放轨迹分析器"""
    
    def __init__(self):
        self.variables = TrajectoryVariables()
        self.formulas = TrajectoryFormulas()
        self.years: List[str] = []
        
        # 部门排放数据
        self.industry = IndustryEmissionData()
        self.building = SectorEmissionData()
        self.transport = SectorEmissionData()
        self.power = PowerEmissionData()
        
        # CCS数据
        self.ccs = CCSData()
        
        # 其他数据
        self.other = OtherEmissionData()
        
        # 模块结果
        self.module_results: Dict[str, Dict] = {}
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_input_dataframe(df)
    
    def _parse_input_dataframe(self, df: pd.DataFrame) -> None:
        """解析输入数据"""
        # CSV格式: 部门,项目,单位,2020,2025,...
        self.years = [str(c) for c in df.columns[3:] if str(c) != 'nan']
        num_years = len(self.years)
        
        current_section = None
        
        for _, row in df.iterrows():
            section = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            item = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            
            # 更新当前部分
            if section in ['工业部门', '建筑部门', '交通部门', '电力部门', 'CCS', '其他']:
                current_section = section
            
            # 获取数值（从第4列开始）
            values = [self._safe_float(row.iloc[i]) for i in range(3, 3 + num_years)]
            
            # 根据部分分配数据
            self._assign_data(current_section, item, values)

    def _assign_data(self, section: str, item: str, values: List[float]) -> None:
        """分配数据到对应结构"""
        if section == '工业部门':
            self._assign_industry_data(item, values)
        elif section == '建筑部门':
            self._assign_building_data(item, values)
        elif section == '交通部门':
            self._assign_transport_data(item, values)
        elif section == '电力部门':
            self._assign_power_data(item, values)
        elif section == 'CCS':
            self._assign_ccs_data(item, values)
        elif section == '其他':
            self._assign_other_data(item, values)
    
    def _assign_industry_data(self, item: str, values: List[float]) -> None:
        """分配工业数据"""
        if item == '来自煤炭':
            self.industry.coal = values
        elif item == '来自石油':
            self.industry.oil = values
        elif item == '来自天然气':
            self.industry.gas = values
        elif item == '工业过程CO2':
            self.industry.process_co2 = values
        elif item == '来自电力':
            self.industry.electricity = values
        elif item == '来自氢能':
            self.industry.hydrogen = values
        elif item == '工业CCS':
            self.industry.ccs = values
    
    def _assign_building_data(self, item: str, values: List[float]) -> None:
        """分配建筑数据"""
        if item == '来自煤炭':
            self.building.coal = values
        elif item == '来自石油':
            self.building.oil = values
        elif item == '来自天然气':
            self.building.gas = values
        elif item == '来自电力':
            self.building.electricity = values
    
    def _assign_transport_data(self, item: str, values: List[float]) -> None:
        """分配交通数据"""
        if item == '来自煤炭':
            self.transport.coal = values
        elif item == '来自石油':
            self.transport.oil = values
        elif item == '来自天然气':
            self.transport.gas = values
        elif item == '来自电力':
            self.transport.electricity = values
    
    def _assign_power_data(self, item: str, values: List[float]) -> None:
        """分配电力数据"""
        if item == '来自煤炭':
            self.power.coal = values
        elif item == '来自天然气':
            self.power.gas = values
        elif item == '化石能源CCS':
            self.power.fossil_ccs = values
        elif item == '生物质CCS':
            self.power.biomass_ccs = values
    
    def _assign_ccs_data(self, item: str, values: List[float]) -> None:
        """分配CCS数据"""
        if item == '煤电CCS':
            self.ccs.coal_power = values
        elif item == '气电CCS':
            self.ccs.gas_power = values
        elif item == '生物质CCS':
            self.ccs.biomass = values
        elif item == '工业CCS':
            self.ccs.industry = values
        elif item == 'DACCS':
            self.ccs.daccs = values
    
    def _assign_other_data(self, item: str, values: List[float]) -> None:
        """分配其他数据"""
        if item == '煤炭消费':
            self.other.coal = values
        elif item == '石油消费':
            self.other.oil = values
        elif item == '天然气消费':
            self.other.gas = values
        elif item == '非二氧化碳':
            self.other.non_co2 = values
        elif item == '碳汇':
            self.other.carbon_sink = values
    
    def load_module_results(self, module_name: str, results: dict) -> None:
        """加载模块计算结果"""
        self.module_results[module_name] = results
    
    def load_from_modules(self) -> None:
        """从已加载的模块结果提取数据"""
        # 从数据模板结果提取
        if 'template' in self.module_results:
            tpl = self.module_results['template']
            self.years = tpl.get('years', self.years)
            
            # 工业部门CO2
            ind_co2 = tpl.get('industry', {}).get('co2', {})
            self.industry.coal = ind_co2.get('来自煤炭', [])
            self.industry.oil = ind_co2.get('来自石油', [])
            self.industry.gas = ind_co2.get('来自天然气', [])
            self.industry.electricity = ind_co2.get('来自电力', [])
            
            # 建筑部门CO2
            bld_co2 = tpl.get('building', {}).get('co2', {})
            self.building.coal = bld_co2.get('来自煤炭', [])
            self.building.oil = bld_co2.get('来自石油', [])
            self.building.gas = bld_co2.get('来自天然气', [])
            self.building.electricity = bld_co2.get('来自电力', [])
            
            # 交通部门CO2
            trn_co2 = tpl.get('transport', {}).get('co2', {})
            self.transport.coal = trn_co2.get('来自煤炭', [])
            self.transport.oil = trn_co2.get('来自石油', [])
            self.transport.gas = trn_co2.get('来自天然气', [])
            self.transport.electricity = trn_co2.get('来自电力', [])
            
            # 电力部门CO2
            pwr_co2 = tpl.get('power', {}).get('co2', {})
            self.power.coal = pwr_co2.get('来自煤炭', [])
            self.power.gas = pwr_co2.get('来自天然气', [])
            self.power.fossil_ccs = pwr_co2.get('化石能源CCS', [])
            self.power.biomass_ccs = pwr_co2.get('生物质CCS', [])
        
        # 从能源结构结果提取
        if 'structure' in self.module_results:
            struct = self.module_results['structure']
            term_struct = struct.get('terminal_structure', {})
            self.other.coal = term_struct.get('coal', [])
            self.other.oil = term_struct.get('oil', [])
            self.other.gas = term_struct.get('gas', [])
        
        # 从电力模块提取CCS数据
        if 'power' in self.module_results:
            pwr = self.module_results['power']
            ccs_data = pwr.get('ccs', {})
            self.ccs.coal_power = ccs_data.get('煤电CCS', [])
            self.ccs.gas_power = ccs_data.get('气电CCS', [])
            self.ccs.biomass = ccs_data.get('生物质CCS', [])
    
    @staticmethod
    def _safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value) or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_value(self, data_list: list, index: int, default: float = 0.0) -> float:
        """安全获取列表值"""
        if index < len(data_list):
            return data_list[index]
        return default

    def calculate(self) -> Dict[str, Any]:
        """执行碳排放轨迹计算"""
        num_years = len(self.years)
        
        results = {
            'years': self.years,
            # 工业部门排放
            'industry': {
                'coal': [], 'oil': [], 'gas': [], 'process_co2': [],
                'electricity': [], 'hydrogen': [], 'ccs': []
            },
            # 建筑部门排放
            'building': {
                'coal': [], 'oil': [], 'gas': [], 'electricity': []
            },
            # 交通部门排放
            'transport': {
                'coal': [], 'oil': [], 'gas': [], 'electricity': []
            },
            # 电力部门排放
            'power': {
                'coal': [], 'gas': [], 'fossil_ccs': [], 'biomass_ccs': []
            },
            # 总排放（含间接排放）
            'total_with_indirect': {
                'industry': [], 'building': [], 'transport': [], 'power': []
            },
            # 总排放（不含间接排放）
            'total_direct': {
                'industry': [], 'building': [], 'transport': [], 'power': []
            },
            # 汇总排放
            'summary': {
                'industry_emission': [],      # 工业排放
                'industry_direct': [],        # 工业直接排放
                'industry_ccs': [],           # 工业CCS
                'building_emission': [],      # 建筑排放
                'transport_emission': [],     # 交通排放
                'power_emission': [],         # 电力排放
                'power_direct': [],           # 电力直接排放
                'power_ccs': [],              # 电力CCS
                'other_emission': [],         # 其他排放
                'daccs': [],                  # DACCS
                'energy_co2': [],             # 能源相关CO2
                'process_co2': [],            # 工业过程
                'total_co2': [],              # 二氧化碳排放
                'non_co2': [],                # 非二氧化碳
                'ghg_emission': [],           # 温室气体排放
                'carbon_sink': [],            # 碳汇
                'net_ghg_emission': []        # 温室气体净排放
            },
            # CCS汇总
            'ccs': {
                'coal_power': [], 'gas_power': [], 'biomass': [],
                'industry': [], 'daccs': [], 'total': []
            },
            # 中和分析
            'neutrality': {
                'energy_co2': [],
                'co2_neutral': [],
                'ghg_neutral': []
            },
            # 燃烧排放
            'combustion': {
                'emission': [], 'industry_ccs': [], 'process_emission': []
            }
        }
        
        for i in range(num_years):
            # ========== 工业部门排放 ==========
            ind_coal = self._get_value(self.industry.coal, i)
            ind_oil = self._get_value(self.industry.oil, i)
            ind_gas = self._get_value(self.industry.gas, i)
            ind_process = self._get_value(self.industry.process_co2, i)
            ind_elec = self._get_value(self.industry.electricity, i)
            ind_h2 = self._get_value(self.industry.hydrogen, i)
            ind_ccs = self._get_value(self.industry.ccs, i)
            
            results['industry']['coal'].append(round(ind_coal, 4))
            results['industry']['oil'].append(round(ind_oil, 4))
            results['industry']['gas'].append(round(ind_gas, 4))
            results['industry']['process_co2'].append(round(ind_process, 4))
            results['industry']['electricity'].append(round(ind_elec, 4))
            results['industry']['hydrogen'].append(round(ind_h2, 4))
            results['industry']['ccs'].append(round(ind_ccs, 4))
            
            # ========== 建筑部门排放 ==========
            bld_coal = self._get_value(self.building.coal, i)
            bld_oil = self._get_value(self.building.oil, i)
            bld_gas = self._get_value(self.building.gas, i)
            bld_elec = self._get_value(self.building.electricity, i)
            
            results['building']['coal'].append(round(bld_coal, 4))
            results['building']['oil'].append(round(bld_oil, 4))
            results['building']['gas'].append(round(bld_gas, 4))
            results['building']['electricity'].append(round(bld_elec, 4))
            
            # ========== 交通部门排放 ==========
            trn_coal = self._get_value(self.transport.coal, i)
            trn_oil = self._get_value(self.transport.oil, i)
            trn_gas = self._get_value(self.transport.gas, i)
            trn_elec = self._get_value(self.transport.electricity, i)
            
            results['transport']['coal'].append(round(trn_coal, 4))
            results['transport']['oil'].append(round(trn_oil, 4))
            results['transport']['gas'].append(round(trn_gas, 4))
            results['transport']['electricity'].append(round(trn_elec, 4))
            
            # ========== 电力部门排放 ==========
            pwr_coal = self._get_value(self.power.coal, i)
            pwr_gas = self._get_value(self.power.gas, i)
            pwr_fossil_ccs = self._get_value(self.power.fossil_ccs, i)
            pwr_bio_ccs = self._get_value(self.power.biomass_ccs, i)
            
            results['power']['coal'].append(round(pwr_coal, 4))
            results['power']['gas'].append(round(pwr_gas, 4))
            results['power']['fossil_ccs'].append(round(pwr_fossil_ccs, 4))
            results['power']['biomass_ccs'].append(round(pwr_bio_ccs, 4))
            
            # ========== 总排放（含间接排放）==========
            ind_total_indirect = self.formulas.calculate_industry_total_with_indirect(
                ind_coal, ind_oil, ind_gas, ind_process, ind_elec, ind_h2, ind_ccs)
            bld_total_indirect = self.formulas.calculate_building_total_with_indirect(
                bld_coal, bld_oil, bld_gas, bld_elec)
            trn_total_indirect = self.formulas.calculate_transport_total_with_indirect(
                trn_coal, trn_oil, trn_gas, trn_elec)
            pwr_total_indirect = self.formulas.calculate_power_total_with_indirect(
                pwr_coal, pwr_gas, pwr_fossil_ccs, pwr_bio_ccs)
            
            results['total_with_indirect']['industry'].append(round(ind_total_indirect, 4))
            results['total_with_indirect']['building'].append(round(bld_total_indirect, 4))
            results['total_with_indirect']['transport'].append(round(trn_total_indirect, 4))
            results['total_with_indirect']['power'].append(round(pwr_total_indirect, 4))
            
            # ========== 总排放（不含间接排放）==========
            ind_total_direct = self.formulas.calculate_industry_total_direct(
                ind_coal, ind_oil, ind_gas, ind_process, ind_elec)
            bld_total_direct = self.formulas.calculate_building_total_direct(
                bld_coal, bld_oil, bld_gas, bld_elec)
            trn_total_direct = self.formulas.calculate_transport_total_direct(
                trn_coal, trn_oil, trn_gas, trn_elec)
            pwr_total_direct = self.formulas.calculate_power_total_direct(
                pwr_coal, pwr_gas, pwr_fossil_ccs, pwr_bio_ccs)
            
            results['total_direct']['industry'].append(round(ind_total_direct, 4))
            results['total_direct']['building'].append(round(bld_total_direct, 4))
            results['total_direct']['transport'].append(round(trn_total_direct, 4))
            results['total_direct']['power'].append(round(pwr_total_direct, 4))
            
            # ========== 汇总排放计算 ==========
            # 工业
            ind_direct_emission = self.formulas.calculate_industry_direct(
                ind_coal, ind_oil, ind_gas, ind_h2)
            ind_emission = self.formulas.calculate_industry_emission(
                ind_coal, ind_oil, ind_gas, ind_h2, ind_ccs)
            
            results['summary']['industry_direct'].append(round(ind_direct_emission, 4))
            results['summary']['industry_ccs'].append(round(ind_ccs, 4))
            results['summary']['industry_emission'].append(round(ind_emission, 4))
            
            # 建筑
            bld_emission = self.formulas.calculate_building_emission(
                bld_coal, bld_oil, bld_gas)
            results['summary']['building_emission'].append(round(bld_emission, 4))
            
            # 交通
            trn_emission = self.formulas.calculate_transport_emission(
                trn_coal, trn_oil, trn_gas)
            results['summary']['transport_emission'].append(round(trn_emission, 4))
            
            # 电力
            pwr_direct_emission = self.formulas.calculate_power_direct(pwr_coal, pwr_gas)
            pwr_ccs = self.formulas.calculate_power_ccs(pwr_fossil_ccs, pwr_bio_ccs)
            pwr_emission = self.formulas.calculate_power_emission(pwr_direct_emission, pwr_ccs)
            
            results['summary']['power_direct'].append(round(pwr_direct_emission, 4))
            results['summary']['power_ccs'].append(round(pwr_ccs, 4))
            results['summary']['power_emission'].append(round(pwr_emission, 4))
            
            # 其他排放
            other_coal = self._get_value(self.other.coal, i)
            other_oil = self._get_value(self.other.oil, i)
            other_gas = self._get_value(self.other.gas, i)
            other_emission = self.formulas.calculate_other_emission(
                other_coal, other_oil, other_gas)
            results['summary']['other_emission'].append(round(other_emission, 4))
            
            # DACCS
            daccs = self._get_value(self.ccs.daccs, i)
            results['summary']['daccs'].append(round(-daccs, 4))  # DACCS为负值
            
            # 能源相关CO2
            energy_co2 = self.formulas.calculate_energy_related_co2(
                ind_emission, bld_emission, trn_emission, pwr_emission, other_emission, -daccs)
            results['summary']['energy_co2'].append(round(energy_co2, 4))
            
            # 工业过程
            results['summary']['process_co2'].append(round(ind_process, 4))
            
            # 二氧化碳排放
            total_co2 = self.formulas.calculate_total_co2(energy_co2, ind_process)
            results['summary']['total_co2'].append(round(total_co2, 4))
            
            # 非二氧化碳
            non_co2 = self._get_value(self.other.non_co2, i)
            results['summary']['non_co2'].append(round(non_co2, 4))
            
            # 温室气体排放
            ghg_emission = self.formulas.calculate_ghg_emission(total_co2, non_co2)
            results['summary']['ghg_emission'].append(round(ghg_emission, 4))
            
            # 碳汇
            carbon_sink = self._get_value(self.other.carbon_sink, i)
            results['summary']['carbon_sink'].append(round(carbon_sink, 4))
            
            # 温室气体净排放
            net_ghg = self.formulas.calculate_net_ghg_emission(ghg_emission, carbon_sink)
            results['summary']['net_ghg_emission'].append(round(net_ghg, 4))
            
            # ========== CCS汇总 ==========
            ccs_coal = self._get_value(self.ccs.coal_power, i)
            ccs_gas = self._get_value(self.ccs.gas_power, i)
            ccs_bio = self._get_value(self.ccs.biomass, i)
            ccs_ind = self._get_value(self.ccs.industry, i)
            
            results['ccs']['coal_power'].append(round(ccs_coal, 4))
            results['ccs']['gas_power'].append(round(ccs_gas, 4))
            results['ccs']['biomass'].append(round(ccs_bio, 4))
            results['ccs']['industry'].append(round(ccs_ind, 4))
            results['ccs']['daccs'].append(round(daccs, 4))
            
            total_ccs = self.formulas.calculate_total_ccs(
                ccs_coal, ccs_gas, ccs_bio, ccs_ind, daccs)
            results['ccs']['total'].append(round(total_ccs, 4))
            
            # ========== 中和分析 ==========
            results['neutrality']['energy_co2'].append(round(energy_co2, 4))
            
            # ========== 燃烧排放 ==========
            combustion = self.formulas.calculate_combustion_emission(
                ind_coal, ind_oil, ind_gas, ind_h2)
            results['combustion']['emission'].append(round(combustion, 4))
            results['combustion']['industry_ccs'].append(round(ind_ccs, 4))
            results['combustion']['process_emission'].append(round(ind_process, 4))
        
        # 计算中和年份
        results['neutrality']['co2_neutral'] = self._find_neutral_year(
            results['summary']['total_co2'])
        results['neutrality']['ghg_neutral'] = self._find_neutral_year(
            results['summary']['net_ghg_emission'])
        
        return results
    
    def _find_neutral_year(self, values: List[float]) -> Optional[str]:
        """找到排放达到零或负值的年份"""
        for i, v in enumerate(values):
            if v <= 0 and i < len(self.years):
                return self.years[i]
        return None

    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['部门', '项目', '单位'] + years
        
        # 工业部门排放
        rows.append(['工业部门', '', ''] + [''] * len(years))
        rows.append(['', '来自煤炭', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['coal']])
        rows.append(['', '来自石油', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['oil']])
        rows.append(['', '来自天然气', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['gas']])
        rows.append(['', '工业过程CO2', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['process_co2']])
        rows.append(['', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['electricity']])
        rows.append(['', '来自氢能', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['hydrogen']])
        rows.append(['', '工业CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['ccs']])
        
        rows.append([''] * (3 + len(years)))
        
        # 建筑部门排放
        rows.append(['建筑部门', '', ''] + [''] * len(years))
        rows.append(['', '来自煤炭', '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['coal']])
        rows.append(['', '来自石油', '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['oil']])
        rows.append(['', '来自天然气', '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['gas']])
        rows.append(['', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['electricity']])
        
        rows.append([''] * (3 + len(years)))
        
        # 交通部门排放
        rows.append(['交通部门', '', ''] + [''] * len(years))
        rows.append(['', '来自煤炭', '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['coal']])
        rows.append(['', '来自石油', '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['oil']])
        rows.append(['', '来自天然气', '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['gas']])
        rows.append(['', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['electricity']])
        
        rows.append([''] * (3 + len(years)))
        
        # 电力部门排放
        rows.append(['电力部门', '', ''] + [''] * len(years))
        rows.append(['', '来自煤炭', '亿吨CO2'] + [f"{v:.4f}" for v in results['power']['coal']])
        rows.append(['', '来自天然气', '亿吨CO2'] + [f"{v:.4f}" for v in results['power']['gas']])
        rows.append(['', '化石能源CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['power']['fossil_ccs']])
        rows.append(['', '生物质CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['power']['biomass_ccs']])
        
        rows.append([''] * (3 + len(years)))
        
        # 总排放（含间接排放）
        rows.append(['总排放（含间接排放）', '', ''] + [''] * len(years))
        rows.append(['', '工业(含工业过程）', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_with_indirect']['industry']])
        rows.append(['', '建筑', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_with_indirect']['building']])
        rows.append(['', '交通', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_with_indirect']['transport']])
        rows.append(['', '电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_with_indirect']['power']])
        
        rows.append([''] * (3 + len(years)))
        
        # 总排放
        rows.append(['总排放', '', ''] + [''] * len(years))
        rows.append(['', '工业(含工业过程）', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_direct']['industry']])
        rows.append(['', '建筑', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_direct']['building']])
        rows.append(['', '交通', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_direct']['transport']])
        rows.append(['', '电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['total_direct']['power']])
        
        rows.append([''] * (3 + len(years)))
        
        # 汇总排放
        rows.append(['汇总', '', ''] + [''] * len(years))
        rows.append(['', '工业排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['industry_emission']])
        rows.append(['', '工业直接排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['industry_direct']])
        rows.append(['', '工业CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['industry_ccs']])
        rows.append(['', '建筑排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['building_emission']])
        rows.append(['', '交通排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['transport_emission']])
        rows.append(['', '电力排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['power_emission']])
        rows.append(['', '电力直接排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['power_direct']])
        rows.append(['', '电力CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['power_ccs']])
        rows.append(['', '其他排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['other_emission']])
        rows.append(['', 'DACCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['daccs']])
        rows.append(['', '能源相关CO2', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['energy_co2']])
        rows.append(['', '工业过程', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['process_co2']])
        rows.append(['', '二氧化碳排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['total_co2']])
        rows.append(['', '非二氧化碳', '亿吨CO2当量'] + [f"{v:.4f}" for v in results['summary']['non_co2']])
        rows.append(['', '温室气体排放', '亿吨CO2当量'] + [f"{v:.4f}" for v in results['summary']['ghg_emission']])
        rows.append(['', '碳汇', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['carbon_sink']])
        rows.append(['', '温室气体净排放', '亿吨CO2当量'] + [f"{v:.4f}" for v in results['summary']['net_ghg_emission']])
        
        rows.append([''] * (3 + len(years)))
        
        # CCS汇总
        rows.append(['CCS汇总', '', ''] + [''] * len(years))
        rows.append(['', '煤电CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['coal_power']])
        rows.append(['', '气电CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['gas_power']])
        rows.append(['', '生物质CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['biomass']])
        rows.append(['', '工业CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['industry']])
        rows.append(['', 'DACCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['daccs']])
        rows.append(['', '总CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['ccs']['total']])
        
        rows.append([''] * (3 + len(years)))
        
        # 中和分析
        rows.append(['中和分析', '', ''] + [''] * len(years))
        rows.append(['', '能源相关CO2', '亿吨CO2'] + [f"{v:.4f}" for v in results['neutrality']['energy_co2']])
        co2_neutral = results['neutrality']['co2_neutral'] or '未达到'
        ghg_neutral = results['neutrality']['ghg_neutral'] or '未达到'
        rows.append(['', '二氧化碳中和年份', '', co2_neutral] + [''] * (len(years) - 1))
        rows.append(['', '温室气体中和年份', '', ghg_neutral] + [''] * (len(years) - 1))
        
        rows.append([''] * (3 + len(years)))
        
        # 燃烧排放
        rows.append(['燃烧排放', '', ''] + [''] * len(years))
        rows.append(['', '燃烧排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['combustion']['emission']])
        rows.append(['', '工业CCS', '亿吨CO2'] + [f"{v:.4f}" for v in results['combustion']['industry_ccs']])
        rows.append(['', '工业过程排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['combustion']['process_emission']])
        
        # 写入CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")

    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 100)
        print("碳排放轨迹分析结果")
        print("=" * 100)
        
        # 总排放（含间接排放）
        print("\n【总排放（含间接排放）（亿吨CO2）】")
        print(f"{'部门':<20}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        for sector, name in [('industry', '工业(含工业过程）'), ('building', '建筑'), 
                             ('transport', '交通'), ('power', '电力')]:
            print(f"{name:<20}", end='')
            for v in results['total_with_indirect'][sector]:
                print(f"{v:>10.2f}", end='')
            print()
        
        # 汇总排放
        print("\n【汇总排放（亿吨CO2）】")
        print(f"{'项目':<20}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        summary_items = [
            ('energy_co2', '能源相关CO2'),
            ('process_co2', '工业过程'),
            ('total_co2', '二氧化碳排放'),
            ('non_co2', '非二氧化碳'),
            ('ghg_emission', '温室气体排放'),
            ('carbon_sink', '碳汇'),
            ('net_ghg_emission', '温室气体净排放')
        ]
        
        for key, name in summary_items:
            print(f"{name:<20}", end='')
            for v in results['summary'][key]:
                print(f"{v:>10.2f}", end='')
            print()
        
        # CCS汇总
        print("\n【CCS汇总（亿吨CO2）】")
        print(f"{'项目':<20}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        ccs_items = [
            ('coal_power', '煤电CCS'),
            ('gas_power', '气电CCS'),
            ('biomass', '生物质CCS'),
            ('industry', '工业CCS'),
            ('daccs', 'DACCS'),
            ('total', '总CCS')
        ]
        
        for key, name in ccs_items:
            print(f"{name:<20}", end='')
            for v in results['ccs'][key]:
                print(f"{v:>10.2f}", end='')
            print()
        
        # 中和分析
        print("\n【中和分析】")
        co2_neutral = results['neutrality']['co2_neutral'] or '未达到'
        ghg_neutral = results['neutrality']['ghg_neutral'] or '未达到'
        print(f"二氧化碳中和年份: {co2_neutral}")
        print(f"温室气体中和年份: {ghg_neutral}")
