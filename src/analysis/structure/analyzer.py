# -*- coding: utf-8 -*-
"""能源结构分析器"""

import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import StructureVariables
from .formulas import StructureFormulas


@dataclass
class SectorEnergyData:
    """部门能源数据"""
    coal: List[float] = field(default_factory=list)
    oil: List[float] = field(default_factory=list)
    gas: List[float] = field(default_factory=list)
    electricity: List[float] = field(default_factory=list)
    hydrogen: List[float] = field(default_factory=list)
    biomass: List[float] = field(default_factory=list)


@dataclass
class PowerEnergyData:
    """电力部门能源数据"""
    coal: List[float] = field(default_factory=list)
    oil: List[float] = field(default_factory=list)
    gas: List[float] = field(default_factory=list)
    wind: List[float] = field(default_factory=list)
    solar: List[float] = field(default_factory=list)
    hydro: List[float] = field(default_factory=list)
    nuclear: List[float] = field(default_factory=list)
    biomass: List[float] = field(default_factory=list)


@dataclass
class HydrogenEnergyData:
    """氢能部门能源数据"""
    electricity: List[float] = field(default_factory=list)
    biomass: List[float] = field(default_factory=list)
    coal: List[float] = field(default_factory=list)


class StructureAnalyzer:
    """能源结构分析器"""
    
    def __init__(self):
        self.variables = StructureVariables()
        self.formulas = StructureFormulas()
        self.years: List[str] = []
        
        # 各部门能源数据
        self.industry = SectorEnergyData()
        self.building = SectorEnergyData()
        self.transport = SectorEnergyData()
        self.other = SectorEnergyData()
        self.power = PowerEnergyData()
        self.hydrogen = HydrogenEnergyData()
        
        # 模块结果
        self.module_results: Dict[str, Dict] = {}
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_input_dataframe(df)
    
    def _parse_input_dataframe(self, df: pd.DataFrame) -> None:
        """解析输入数据"""
        # CSV格式: 能源类型,部门,2020,2025,...
        self.years = [str(c) for c in df.columns[2:] if str(c) != 'nan']
        num_years = len(self.years)
        
        for _, row in df.iterrows():
            energy_type = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            sector = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            values = [self._safe_float(row.iloc[i]) for i in range(2, 2 + num_years)]
            
            self._assign_data(energy_type, sector, values)
    
    def _assign_data(self, energy_type: str, sector: str, values: List[float]) -> None:
        """分配数据到对应结构"""
        if sector == '工业':
            self._assign_sector_data(self.industry, energy_type, values)
        elif sector == '建筑':
            self._assign_sector_data(self.building, energy_type, values)
        elif sector == '交通':
            self._assign_sector_data(self.transport, energy_type, values)
        elif sector == '其他':
            self._assign_sector_data(self.other, energy_type, values)
        elif sector == '电力':
            self._assign_power_data(energy_type, values)
        elif sector == '氢能':
            self._assign_hydrogen_data(energy_type, values)
    
    def _assign_sector_data(self, sector_data: SectorEnergyData, 
                            energy_type: str, values: List[float]) -> None:
        """分配部门数据"""
        if energy_type == '煤炭':
            sector_data.coal = values
        elif energy_type == '石油':
            sector_data.oil = values
        elif energy_type == '天然气':
            sector_data.gas = values
        elif energy_type == '电力':
            sector_data.electricity = values
        elif energy_type == '氢能':
            sector_data.hydrogen = values
        elif energy_type == '生物质':
            sector_data.biomass = values
    
    def _assign_power_data(self, energy_type: str, values: List[float]) -> None:
        """分配电力部门数据"""
        if energy_type == '煤炭':
            self.power.coal = values
        elif energy_type == '石油':
            self.power.oil = values
        elif energy_type == '天然气':
            self.power.gas = values
        elif energy_type == '风电':
            self.power.wind = values
        elif energy_type == '光伏':
            self.power.solar = values
        elif energy_type == '水电':
            self.power.hydro = values
        elif energy_type == '核电':
            self.power.nuclear = values
        elif energy_type == '生物质':
            self.power.biomass = values
    
    def _assign_hydrogen_data(self, energy_type: str, values: List[float]) -> None:
        """分配氢能部门数据"""
        if energy_type == '电力':
            self.hydrogen.electricity = values
        elif energy_type == '生物质':
            self.hydrogen.biomass = values
        elif energy_type == '煤炭':
            self.hydrogen.coal = values
    
    def load_module_results(self, module_name: str, results: dict) -> None:
        """加载模块计算结果"""
        self.module_results[module_name] = results
    
    def load_from_modules(self) -> None:
        """从已加载的模块结果提取数据"""
        # 从数据模板结果提取
        if 'template' in self.module_results:
            tpl = self.module_results['template']
            self.years = tpl.get('years', self.years)
            
            # 工业
            ind = tpl.get('industry', {}).get('energy', {})
            self.industry.coal = ind.get('煤炭', [])
            self.industry.oil = ind.get('石油', [])
            self.industry.gas = ind.get('天然气', [])
            elec = ind.get('电力', [])
            self.industry.electricity = [v * self.formulas.electricity_conversion for v in elec]
            self.industry.hydrogen = ind.get('氢能', [])
            self.industry.biomass = ind.get('生物质', [])
            
            # 建筑
            bld = tpl.get('building', {}).get('energy', {})
            self.building.coal = bld.get('煤炭', [])
            self.building.oil = bld.get('石油', [])
            self.building.gas = bld.get('天然气', [])
            elec = bld.get('电力', [])
            self.building.electricity = [v * self.formulas.electricity_conversion for v in elec]
            self.building.hydrogen = bld.get('氢能', [])
            self.building.biomass = bld.get('生物质', [])
            
            # 交通
            trn = tpl.get('transport', {}).get('energy', {})
            self.transport.coal = trn.get('煤炭', [])
            self.transport.oil = trn.get('石油', [])
            self.transport.gas = trn.get('天然气', [])
            elec = trn.get('电力', [])
            self.transport.electricity = [v * self.formulas.electricity_conversion for v in elec]
            self.transport.hydrogen = trn.get('氢能', [])
            self.transport.biomass = trn.get('生物质', [])
            
            # 电力
            pwr = tpl.get('power', {})
            pwr_energy = pwr.get('energy', {})
            self.power.coal = pwr_energy.get('煤炭', [])
            self.power.oil = pwr_energy.get('石油', [])
            self.power.gas = pwr_energy.get('天然气', [])
            
            pwr_nf = pwr.get('non_fossil', {})
            self.power.wind = pwr_nf.get('风能', [])
            self.power.solar = pwr_nf.get('太阳能', [])
            self.power.hydro = pwr_nf.get('水能', [])
            self.power.nuclear = pwr_nf.get('核能', [])
            self.power.biomass = pwr_nf.get('生物质能', [])
    
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
        """执行能源结构计算"""
        num_years = len(self.years)
        
        results = {
            'years': self.years,
            # 终端消费
            'terminal': {
                'industry': {'total': [], 'coal': [], 'oil': [], 'gas': [], 
                            'electricity': [], 'hydrogen': [], 'biomass': []},
                'building': {'total': [], 'coal': [], 'oil': [], 'gas': [],
                            'electricity': [], 'hydrogen': [], 'biomass': []},
                'transport': {'total': [], 'coal': [], 'oil': [], 'gas': [],
                             'electricity': [], 'hydrogen': [], 'biomass': []},
                'other': {'total': [], 'coal': [], 'oil': [], 'gas': [],
                         'electricity': [], 'hydrogen': [], 'biomass': []},
                'total': []
            },
            # 电气化率
            'electrification': {
                'industry': [], 'building': [], 'transport': [], 'terminal': []
            },
            # 氢能
            'hydrogen': {
                'total': [], 'ratio': []
            },
            # 一次能源
            'primary': {
                'coal': [], 'oil': [], 'gas': [], 'non_fossil': [], 'total': [],
                'wind': [], 'solar': [], 'hydro': [], 'nuclear': [], 'biomass': []
            },
            # 能源结构占比
            'structure': {
                'coal_ratio': [], 'oil_ratio': [], 'gas_ratio': [], 'non_fossil_ratio': []
            },
            # 终端能源结构
            'terminal_structure': {
                'coal': [], 'oil': [], 'gas': [], 'biomass': [], 'hydrogen': [], 'electricity': []
            },
            # 生物质汇总
            'biomass_total': []
        }
        
        for i in range(num_years):
            # ========== 终端消费计算 ==========
            # 工业
            ind_coal = self._get_value(self.industry.coal, i)
            ind_oil = self._get_value(self.industry.oil, i)
            ind_gas = self._get_value(self.industry.gas, i)
            ind_elec = self._get_value(self.industry.electricity, i)
            ind_h2 = self._get_value(self.industry.hydrogen, i)
            ind_bio = self._get_value(self.industry.biomass, i)
            ind_total = self.formulas.calculate_sector_total(
                ind_coal, ind_oil, ind_gas, ind_elec, ind_h2, ind_bio)
            
            results['terminal']['industry']['coal'].append(round(ind_coal, 4))
            results['terminal']['industry']['oil'].append(round(ind_oil, 4))
            results['terminal']['industry']['gas'].append(round(ind_gas, 4))
            results['terminal']['industry']['electricity'].append(round(ind_elec, 4))
            results['terminal']['industry']['hydrogen'].append(round(ind_h2, 4))
            results['terminal']['industry']['biomass'].append(round(ind_bio, 4))
            results['terminal']['industry']['total'].append(round(ind_total, 4))
            
            # 建筑
            bld_coal = self._get_value(self.building.coal, i)
            bld_oil = self._get_value(self.building.oil, i)
            bld_gas = self._get_value(self.building.gas, i)
            bld_elec = self._get_value(self.building.electricity, i)
            bld_h2 = self._get_value(self.building.hydrogen, i)
            bld_bio = self._get_value(self.building.biomass, i)
            bld_total = self.formulas.calculate_sector_total(
                bld_coal, bld_oil, bld_gas, bld_elec, bld_h2, bld_bio)
            
            results['terminal']['building']['coal'].append(round(bld_coal, 4))
            results['terminal']['building']['oil'].append(round(bld_oil, 4))
            results['terminal']['building']['gas'].append(round(bld_gas, 4))
            results['terminal']['building']['electricity'].append(round(bld_elec, 4))
            results['terminal']['building']['hydrogen'].append(round(bld_h2, 4))
            results['terminal']['building']['biomass'].append(round(bld_bio, 4))
            results['terminal']['building']['total'].append(round(bld_total, 4))
            
            # 交通
            trn_coal = self._get_value(self.transport.coal, i)
            trn_oil = self._get_value(self.transport.oil, i)
            trn_gas = self._get_value(self.transport.gas, i)
            trn_elec = self._get_value(self.transport.electricity, i)
            trn_h2 = self._get_value(self.transport.hydrogen, i)
            trn_bio = self._get_value(self.transport.biomass, i)
            trn_total = self.formulas.calculate_sector_total(
                trn_coal, trn_oil, trn_gas, trn_elec, trn_h2, trn_bio)
            
            results['terminal']['transport']['coal'].append(round(trn_coal, 4))
            results['terminal']['transport']['oil'].append(round(trn_oil, 4))
            results['terminal']['transport']['gas'].append(round(trn_gas, 4))
            results['terminal']['transport']['electricity'].append(round(trn_elec, 4))
            results['terminal']['transport']['hydrogen'].append(round(trn_h2, 4))
            results['terminal']['transport']['biomass'].append(round(trn_bio, 4))
            results['terminal']['transport']['total'].append(round(trn_total, 4))
            
            # 其他
            oth_coal = self._get_value(self.other.coal, i)
            oth_oil = self._get_value(self.other.oil, i)
            oth_gas = self._get_value(self.other.gas, i)
            oth_elec = self._get_value(self.other.electricity, i)
            oth_h2 = self._get_value(self.other.hydrogen, i)
            oth_bio = self._get_value(self.other.biomass, i)
            oth_total = self.formulas.calculate_sector_total(
                oth_coal, oth_oil, oth_gas, oth_elec, oth_h2, oth_bio)
            
            results['terminal']['other']['coal'].append(round(oth_coal, 4))
            results['terminal']['other']['oil'].append(round(oth_oil, 4))
            results['terminal']['other']['gas'].append(round(oth_gas, 4))
            results['terminal']['other']['electricity'].append(round(oth_elec, 4))
            results['terminal']['other']['hydrogen'].append(round(oth_h2, 4))
            results['terminal']['other']['biomass'].append(round(oth_bio, 4))
            results['terminal']['other']['total'].append(round(oth_total, 4))
            
            # 终端总消费
            terminal_total = self.formulas.calculate_terminal_total(
                ind_total, bld_total, trn_total, oth_total)
            results['terminal']['total'].append(round(terminal_total, 4))
            
            # ========== 电气化率计算 ==========
            ind_elec_rate = self.formulas.calculate_electrification_rate(ind_elec, ind_total)
            bld_elec_rate = self.formulas.calculate_electrification_rate(bld_elec, bld_total)
            trn_elec_rate = self.formulas.calculate_electrification_rate(trn_elec, trn_total)
            
            total_elec = ind_elec + bld_elec + trn_elec + oth_elec
            terminal_elec_rate = self.formulas.calculate_electrification_rate(total_elec, terminal_total)
            
            results['electrification']['industry'].append(round(ind_elec_rate * 100, 2))
            results['electrification']['building'].append(round(bld_elec_rate * 100, 2))
            results['electrification']['transport'].append(round(trn_elec_rate * 100, 2))
            results['electrification']['terminal'].append(round(terminal_elec_rate * 100, 2))
            
            # ========== 氢能计算 ==========
            h2_total = self.formulas.calculate_total_hydrogen(ind_h2, bld_h2, trn_h2)
            h2_ratio = self.formulas.calculate_hydrogen_ratio(h2_total, terminal_total)
            
            results['hydrogen']['total'].append(round(h2_total, 4))
            results['hydrogen']['ratio'].append(round(h2_ratio * 100, 2))
            
            # ========== 一次能源计算 ==========
            # 电力部门能源
            pwr_coal = self._get_value(self.power.coal, i)
            pwr_oil = self._get_value(self.power.oil, i)
            pwr_gas = self._get_value(self.power.gas, i)
            pwr_wind = self._get_value(self.power.wind, i)
            pwr_solar = self._get_value(self.power.solar, i)
            pwr_hydro = self._get_value(self.power.hydro, i)
            pwr_nuclear = self._get_value(self.power.nuclear, i)
            pwr_biomass = self._get_value(self.power.biomass, i)
            
            # 氢能部门能源
            h2_elec = self._get_value(self.hydrogen.electricity, i)
            h2_bio = self._get_value(self.hydrogen.biomass, i)
            h2_coal = self._get_value(self.hydrogen.coal, i)
            
            # 一次能源煤炭
            primary_coal = self.formulas.calculate_primary_coal(
                ind_coal, bld_coal, trn_coal, pwr_coal, h2_coal, oth_coal)
            
            # 一次能源石油
            primary_oil = self.formulas.calculate_primary_oil(
                ind_oil, bld_oil, trn_oil, pwr_oil, oth_oil)
            
            # 一次能源天然气
            primary_gas = self.formulas.calculate_primary_gas(
                ind_gas, bld_gas, trn_gas, pwr_gas, oth_gas)
            
            # 一次能源非化石
            primary_non_fossil = self.formulas.calculate_primary_non_fossil(
                pwr_wind, pwr_solar, pwr_hydro, pwr_nuclear, pwr_biomass)
            
            # 一次能源总量
            primary_total = self.formulas.calculate_total_primary_energy(
                primary_coal, primary_oil, primary_gas, primary_non_fossil)
            
            results['primary']['coal'].append(round(primary_coal, 4))
            results['primary']['oil'].append(round(primary_oil, 4))
            results['primary']['gas'].append(round(primary_gas, 4))
            results['primary']['non_fossil'].append(round(primary_non_fossil, 4))
            results['primary']['total'].append(round(primary_total, 4))
            results['primary']['wind'].append(round(pwr_wind, 4))
            results['primary']['solar'].append(round(pwr_solar, 4))
            results['primary']['hydro'].append(round(pwr_hydro, 4))
            results['primary']['nuclear'].append(round(pwr_nuclear, 4))
            results['primary']['biomass'].append(round(pwr_biomass, 4))
            
            # ========== 能源结构占比 ==========
            coal_ratio = self.formulas.calculate_energy_ratio(primary_coal, primary_total)
            oil_ratio = self.formulas.calculate_energy_ratio(primary_oil, primary_total)
            gas_ratio = self.formulas.calculate_energy_ratio(primary_gas, primary_total)
            non_fossil_ratio = self.formulas.calculate_energy_ratio(primary_non_fossil, primary_total)
            
            results['structure']['coal_ratio'].append(round(coal_ratio, 2))
            results['structure']['oil_ratio'].append(round(oil_ratio, 2))
            results['structure']['gas_ratio'].append(round(gas_ratio, 2))
            results['structure']['non_fossil_ratio'].append(round(non_fossil_ratio, 2))
            
            # ========== 终端能源结构 ==========
            term_coal = ind_coal + bld_coal + trn_coal + oth_coal
            term_oil = ind_oil + bld_oil + trn_oil + oth_oil
            term_gas = ind_gas + bld_gas + trn_gas + oth_gas
            term_bio = ind_bio + bld_bio + trn_bio + oth_bio
            term_h2 = ind_h2 + bld_h2 + trn_h2 + oth_h2
            term_elec = ind_elec + bld_elec + trn_elec + oth_elec
            
            results['terminal_structure']['coal'].append(round(term_coal, 4))
            results['terminal_structure']['oil'].append(round(term_oil, 4))
            results['terminal_structure']['gas'].append(round(term_gas, 4))
            results['terminal_structure']['biomass'].append(round(term_bio, 4))
            results['terminal_structure']['hydrogen'].append(round(term_h2, 4))
            results['terminal_structure']['electricity'].append(round(term_elec, 4))
            
            # ========== 生物质汇总 ==========
            bio_total = self.formulas.calculate_total_biomass(
                ind_bio, bld_bio, trn_bio, pwr_biomass, h2_bio)
            results['biomass_total'].append(round(bio_total, 4))
        
        return results

    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['类别', '项目', '单位'] + years
        
        # 终端消费
        rows.append(['终端消费', '', ''] + [''] * len(years))
        rows.append(['', '工业总消费', '亿tce'] + [f"{v:.4f}" for v in results['terminal']['industry']['total']])
        rows.append(['', '建筑总消费', '亿tce'] + [f"{v:.4f}" for v in results['terminal']['building']['total']])
        rows.append(['', '交通总消费', '亿tce'] + [f"{v:.4f}" for v in results['terminal']['transport']['total']])
        rows.append(['', '其他部门消费', '亿tce'] + [f"{v:.4f}" for v in results['terminal']['other']['total']])
        rows.append(['', '终端总消费', '亿tce'] + [f"{v:.4f}" for v in results['terminal']['total']])
        
        rows.append([''] * (3 + len(years)))
        
        # 电气化率
        rows.append(['电气化率', '', ''] + [''] * len(years))
        rows.append(['', '工业电气化率', '%'] + [f"{v:.2f}" for v in results['electrification']['industry']])
        rows.append(['', '建筑电气化率', '%'] + [f"{v:.2f}" for v in results['electrification']['building']])
        rows.append(['', '交通电气化率', '%'] + [f"{v:.2f}" for v in results['electrification']['transport']])
        rows.append(['', '终端电气化率', '%'] + [f"{v:.2f}" for v in results['electrification']['terminal']])
        
        rows.append([''] * (3 + len(years)))
        
        # 氢能
        rows.append(['氢能', '', ''] + [''] * len(years))
        rows.append(['', '氢能总消费', '亿tce'] + [f"{v:.4f}" for v in results['hydrogen']['total']])
        rows.append(['', '氢能占比', '%'] + [f"{v:.2f}" for v in results['hydrogen']['ratio']])
        
        rows.append([''] * (3 + len(years)))
        
        # 一次能源
        rows.append(['一次能源', '', ''] + [''] * len(years))
        rows.append(['', '煤', '亿tce'] + [f"{v:.4f}" for v in results['primary']['coal']])
        rows.append(['', '油', '亿tce'] + [f"{v:.4f}" for v in results['primary']['oil']])
        rows.append(['', '气', '亿tce'] + [f"{v:.4f}" for v in results['primary']['gas']])
        rows.append(['', '非化石', '亿tce'] + [f"{v:.4f}" for v in results['primary']['non_fossil']])
        rows.append(['', '总能源消费', '亿tce'] + [f"{v:.4f}" for v in results['primary']['total']])
        
        rows.append([''] * (3 + len(years)))
        
        # 非化石细分
        rows.append(['非化石细分', '', ''] + [''] * len(years))
        rows.append(['', '风', '亿tce'] + [f"{v:.4f}" for v in results['primary']['wind']])
        rows.append(['', '光', '亿tce'] + [f"{v:.4f}" for v in results['primary']['solar']])
        rows.append(['', '水', '亿tce'] + [f"{v:.4f}" for v in results['primary']['hydro']])
        rows.append(['', '核', '亿tce'] + [f"{v:.4f}" for v in results['primary']['nuclear']])
        rows.append(['', '生物质', '亿tce'] + [f"{v:.4f}" for v in results['primary']['biomass']])
        
        rows.append([''] * (3 + len(years)))
        
        # 能源结构占比
        rows.append(['能源结构占比', '', ''] + [''] * len(years))
        rows.append(['', '煤炭', '%'] + [f"{v:.2f}" for v in results['structure']['coal_ratio']])
        rows.append(['', '石油', '%'] + [f"{v:.2f}" for v in results['structure']['oil_ratio']])
        rows.append(['', '天然气', '%'] + [f"{v:.2f}" for v in results['structure']['gas_ratio']])
        rows.append(['', '非化石能源', '%'] + [f"{v:.2f}" for v in results['structure']['non_fossil_ratio']])
        
        rows.append([''] * (3 + len(years)))
        
        # 终端能源结构
        rows.append(['终端能源结构', '', ''] + [''] * len(years))
        rows.append(['', '煤', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['coal']])
        rows.append(['', '油', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['oil']])
        rows.append(['', '气', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['gas']])
        rows.append(['', '生物质', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['biomass']])
        rows.append(['', '氢', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['hydrogen']])
        rows.append(['', '电', '亿tce'] + [f"{v:.4f}" for v in results['terminal_structure']['electricity']])
        
        rows.append([''] * (3 + len(years)))
        
        # 生物质汇总
        rows.append(['生物质汇总', '', ''] + [''] * len(years))
        rows.append(['', '生物质总消费', '亿tce'] + [f"{v:.4f}" for v in results['biomass_total']])
        
        # 写入CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")

    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 80)
        print("能源结构分析结果")
        print("=" * 80)
        
        # 终端消费
        print("\n【终端消费（亿tce）】")
        print(f"{'项目':<15}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        for sector, name in [('industry', '工业'), ('building', '建筑'), 
                             ('transport', '交通'), ('other', '其他')]:
            print(f"{name:<15}", end='')
            for v in results['terminal'][sector]['total']:
                print(f"{v:>10.2f}", end='')
            print()
        
        print(f"{'终端总消费':<15}", end='')
        for v in results['terminal']['total']:
            print(f"{v:>10.2f}", end='')
        print()
        
        # 电气化率
        print("\n【电气化率（%）】")
        print(f"{'项目':<15}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        for sector, name in [('industry', '工业'), ('building', '建筑'), 
                             ('transport', '交通'), ('terminal', '终端')]:
            print(f"{name:<15}", end='')
            for v in results['electrification'][sector]:
                print(f"{v:>10.2f}", end='')
            print()
        
        # 氢能
        print("\n【氢能】")
        print(f"{'氢能总消费(亿tce)':<18}", end='')
        for v in results['hydrogen']['total']:
            print(f"{v:>10.4f}", end='')
        print()
        print(f"{'氢能占比(%)':<18}", end='')
        for v in results['hydrogen']['ratio']:
            print(f"{v:>10.2f}", end='')
        print()
        
        # 一次能源
        print("\n【一次能源（亿tce）】")
        print(f"{'项目':<15}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        for key, name in [('coal', '煤'), ('oil', '油'), ('gas', '气'), 
                          ('non_fossil', '非化石'), ('total', '总计')]:
            print(f"{name:<15}", end='')
            for v in results['primary'][key]:
                print(f"{v:>10.2f}", end='')
            print()
        
        # 能源结构占比
        print("\n【能源结构占比（%）】")
        print(f"{'项目':<15}", end='')
        for year in years:
            print(f"{year:>10}", end='')
        print()
        
        for key, name in [('coal_ratio', '煤炭'), ('oil_ratio', '石油'), 
                          ('gas_ratio', '天然气'), ('non_fossil_ratio', '非化石')]:
            print(f"{name:<15}", end='')
            for v in results['structure'][key]:
                print(f"{v:>10.2f}", end='')
            print()