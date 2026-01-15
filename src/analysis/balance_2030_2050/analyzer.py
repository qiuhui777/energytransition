# -*- coding: utf-8 -*-
"""2030年和2050年平衡表分析器"""

import csv
import os
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import BalanceVariables
from .formulas import BalanceFormulas


@dataclass
class SectorBalanceData:
    """部门平衡数据结构"""
    # 电力消费
    electricity_twh: float = 0.0      # 电量/万亿千瓦时
    electricity_tce: float = 0.0      # 电热当量/亿tce
    
    # 氢能消费
    hydrogen: float = 0.0             # 氢能消费/亿tce
    
    # 一次能源消费
    coal: float = 0.0                 # 煤炭/亿tce
    oil: float = 0.0                  # 石油/亿tce
    gas: float = 0.0                  # 天然气/亿tce
    non_fossil: float = 0.0           # 非化石能源/亿tce
    primary_subtotal: float = 0.0     # 一次能源小计/亿tce
    
    # 终端能源消费
    terminal_energy: float = 0.0      # 终端能源消费/亿tce
    terminal_structure: float = 0.0   # 终端消费结构/%
    
    # CO2排放
    co2_emission: float = 0.0         # CO2直接排放/亿吨


@dataclass
class YearBalanceData:
    """年度平衡数据结构"""
    year: str = ''
    
    # 终端部门数据
    industry: SectorBalanceData = field(default_factory=SectorBalanceData)
    building: SectorBalanceData = field(default_factory=SectorBalanceData)
    transport: SectorBalanceData = field(default_factory=SectorBalanceData)
    other: SectorBalanceData = field(default_factory=SectorBalanceData)
    terminal_total: SectorBalanceData = field(default_factory=SectorBalanceData)
    
    # 供应部门数据
    hydrogen_supply: SectorBalanceData = field(default_factory=SectorBalanceData)
    power_supply: SectorBalanceData = field(default_factory=SectorBalanceData)
    
    # 一次能源消费汇总
    primary_energy_total: SectorBalanceData = field(default_factory=SectorBalanceData)
    primary_structure: Dict[str, float] = field(default_factory=dict)
    
    # 碳排放汇总
    process_co2: float = 0.0          # 工业过程CO2
    non_co2: float = 0.0              # 非二氧化碳
    ccs: float = 0.0                  # CCS
    carbon_sink: float = 0.0          # 碳汇
    energy_related_co2: float = 0.0   # 能源相关CO2
    ghg_emission: float = 0.0         # 温室气体排放


class BalanceAnalyzer:
    """2030年和2050年平衡表分析器"""
    
    def __init__(self):
        self.variables = BalanceVariables()
        self.formulas = BalanceFormulas()
        
        # 年度数据存储
        self.year_data: Dict[str, YearBalanceData] = {}
        
        # 输入数据
        self.template_data: Dict = {}      # 数据模板数据
        self.structure_data: Dict = {}     # 能源消费结构数据
        self.trajectory_data: Dict = {}    # 碳排放轨迹数据
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_input_dataframe(df)
    
    def _parse_input_dataframe(self, df: pd.DataFrame) -> None:
        """解析输入数据"""
        # CSV格式: 年份,部门,类别,项目,数值
        current_year = None
        
        for _, row in df.iterrows():
            year = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            sector = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            category = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
            item = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ''
            value = self._safe_float(row.iloc[4]) if len(row) > 4 else 0.0
            
            if year:
                current_year = year
                if current_year not in self.year_data:
                    self.year_data[current_year] = YearBalanceData(year=current_year)
            
            if current_year and sector:
                self._assign_data(current_year, sector, category, item, value)
    
    def _assign_data(self, year: str, sector: str, category: str, 
                     item: str, value: float) -> None:
        """分配数据到对应结构"""
        data = self.year_data[year]
        
        # 获取对应部门数据
        sector_data = None
        if sector == '工业':
            sector_data = data.industry
        elif sector == '建筑':
            sector_data = data.building
        elif sector == '交通':
            sector_data = data.transport
        elif sector == '其它':
            sector_data = data.other
        elif sector == '氢能供应':
            sector_data = data.hydrogen_supply
        elif sector == '电力供应':
            sector_data = data.power_supply
        
        if sector_data is None:
            return
        
        # 分配数据
        if category == '电力消费':
            if item == '电量':
                sector_data.electricity_twh = value
            elif item == '电热当量':
                sector_data.electricity_tce = value
        elif category == '氢能消费':
            sector_data.hydrogen = value
        elif category == '一次能源消费':
            if item == '煤炭':
                sector_data.coal = value
            elif item == '石油':
                sector_data.oil = value
            elif item == '天然气':
                sector_data.gas = value
            elif item == '非化石能源':
                sector_data.non_fossil = value
        elif category == '碳排放':
            if item == '工业过程':
                data.process_co2 = value
            elif item == '非二氧化碳':
                data.non_co2 = value
            elif item == 'CCS':
                data.ccs = value
            elif item == '碳汇':
                data.carbon_sink = value
    
    def load_module_results(self, module_name: str, results: dict) -> None:
        """加载其他模块的计算结果"""
        if module_name == 'template':
            self.template_data = results
        elif module_name == 'structure':
            self.structure_data = results
        elif module_name == 'trajectory':
            self.trajectory_data = results
    
    def load_from_modules(self) -> None:
        """从已加载的模块结果提取数据"""
        years = self.variables.TARGET_YEARS
        
        for year in years:
            if year not in self.year_data:
                self.year_data[year] = YearBalanceData(year=year)
            
            data = self.year_data[year]
            
            # 从数据模板提取电力消费数据
            if self.template_data:
                self._extract_template_data(year, data)
            
            # 从能源消费结构提取能源数据
            if self.structure_data:
                self._extract_structure_data(year, data)
            
            # 从碳排放轨迹提取碳排放数据
            if self.trajectory_data:
                self._extract_trajectory_data(year, data)
    
    def _extract_template_data(self, year: str, data: YearBalanceData) -> None:
        """从数据模板提取数据"""
        years = self.template_data.get('years', [])
        if year not in years:
            return
        
        idx = years.index(year)
        
        # 提取各部门电力消费
        industry_elec = self._get_template_value('industry', 'energy', '电力', idx)
        building_elec = self._get_template_value('building', 'energy', '电力', idx)
        transport_elec = self._get_template_value('transport', 'energy', '电力', idx)
        
        data.industry.electricity_twh = industry_elec
        data.building.electricity_twh = building_elec
        data.transport.electricity_twh = transport_elec
    
    def _extract_structure_data(self, year: str, data: YearBalanceData) -> None:
        """从能源消费结构提取数据"""
        years = self.structure_data.get('years', [])
        if year not in years:
            return
        
        idx = years.index(year)
        
        # 提取工业部门能源数据
        data.industry.hydrogen = self._get_structure_value('industry', '氢能', idx)
        data.industry.coal = self._get_structure_value('industry', '煤炭', idx)
        data.industry.oil = self._get_structure_value('industry', '石油', idx)
        data.industry.gas = self._get_structure_value('industry', '天然气', idx)
        data.industry.non_fossil = self._get_structure_value('industry', '非化石能源', idx)
        
        # 提取建筑部门能源数据
        data.building.hydrogen = self._get_structure_value('building', '氢能', idx)
        data.building.coal = self._get_structure_value('building', '煤炭', idx)
        data.building.oil = self._get_structure_value('building', '石油', idx)
        data.building.gas = self._get_structure_value('building', '天然气', idx)
        data.building.non_fossil = self._get_structure_value('building', '非化石能源', idx)
        
        # 提取交通部门能源数据
        data.transport.hydrogen = self._get_structure_value('transport', '氢能', idx)
        data.transport.coal = self._get_structure_value('transport', '煤炭', idx)
        data.transport.oil = self._get_structure_value('transport', '石油', idx)
        data.transport.gas = self._get_structure_value('transport', '天然气', idx)
        data.transport.non_fossil = self._get_structure_value('transport', '非化石能源', idx)
        
        # 提取其它部门能源数据
        data.other.coal = self._get_structure_value('other', '煤炭', idx)
        data.other.oil = self._get_structure_value('other', '石油', idx)
        data.other.gas = self._get_structure_value('other', '天然气', idx)
        
        # 提取电力供应能源数据
        data.power_supply.coal = self._get_structure_value('power', '煤炭', idx)
        data.power_supply.oil = self._get_structure_value('power', '石油', idx)
        data.power_supply.gas = self._get_structure_value('power', '天然气', idx)
        data.power_supply.non_fossil = self._get_structure_value('power', '非化石能源', idx)
        
        # 提取氢能供应能源数据
        data.hydrogen_supply.coal = self._get_structure_value('hydrogen', '煤炭', idx)
        data.hydrogen_supply.non_fossil = self._get_structure_value('hydrogen', '非化石能源', idx)
    
    def _extract_trajectory_data(self, year: str, data: YearBalanceData) -> None:
        """从碳排放轨迹提取数据"""
        years = self.trajectory_data.get('years', [])
        if year not in years:
            return
        
        idx = years.index(year)
        
        # 提取碳排放数据
        summary = self.trajectory_data.get('summary', {})
        data.process_co2 = self._get_list_value(summary.get('工业过程', []), idx)
        data.non_co2 = self._get_list_value(summary.get('非二氧化碳', []), idx)
        data.carbon_sink = self._get_list_value(summary.get('碳汇', []), idx)
        
        # CCS数据
        ccs_data = self.trajectory_data.get('ccs', {})
        power_ccs = self._get_list_value(ccs_data.get('电力CCS', []), idx)
        industry_ccs = self._get_list_value(ccs_data.get('工业CCS', []), idx)
        daccs = self._get_list_value(ccs_data.get('DACCS', []), idx)
        data.ccs = self.formulas.calculate_ccs_total(power_ccs, industry_ccs, daccs)
    
    def _get_template_value(self, sector: str, category: str, 
                            item: str, idx: int) -> float:
        """从数据模板获取值"""
        try:
            return self.template_data.get(sector, {}).get(category, {}).get(item, [])[idx]
        except (IndexError, KeyError, TypeError):
            return 0.0
    
    def _get_structure_value(self, sector: str, item: str, idx: int) -> float:
        """从能源消费结构获取值"""
        try:
            return self.structure_data.get(sector, {}).get(item, [])[idx]
        except (IndexError, KeyError, TypeError):
            return 0.0
    
    def _get_list_value(self, lst: list, idx: int) -> float:
        """安全获取列表值"""
        if idx < len(lst):
            return lst[idx]
        return 0.0
    
    @staticmethod
    def _safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value) or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def calculate(self) -> Dict[str, Any]:
        """执行2030年和2050年平衡表计算"""
        results = {
            'years': list(self.year_data.keys()),
            'balance_data': {}
        }
        
        for year, data in self.year_data.items():
            year_result = self._calculate_year(data)
            results['balance_data'][year] = year_result
        
        return results
    
    def _calculate_year(self, data: YearBalanceData) -> Dict[str, Any]:
        """计算单个年份的平衡数据"""
        result = {
            'terminal_sectors': {},
            'supply_sectors': {},
            'summary': {}
        }
        
        # ========== 计算终端部门 ==========
        sectors = [
            ('工业', data.industry),
            ('建筑', data.building),
            ('交通', data.transport),
            ('其它', data.other)
        ]
        
        for name, sector in sectors:
            sector_result = self._calculate_sector(sector)
            result['terminal_sectors'][name] = sector_result
        
        # ========== 计算终端总计 ==========
        terminal_total = self._calculate_terminal_total(
            data.industry, data.building, data.transport, data.other
        )
        result['terminal_sectors']['总计'] = terminal_total
        
        # 更新终端消费结构
        total_terminal = terminal_total['终端能源消费']
        for name in ['工业', '建筑', '交通', '其它']:
            sector_terminal = result['terminal_sectors'][name]['终端能源消费']
            result['terminal_sectors'][name]['终端消费结构'] = \
                self.formulas.calculate_terminal_structure(sector_terminal, total_terminal)
        result['terminal_sectors']['总计']['终端消费结构'] = 1.0
        
        # ========== 计算供应部门 ==========
        # 氢能供应
        hydrogen_result = self._calculate_sector(data.hydrogen_supply)
        result['supply_sectors']['氢能供应'] = hydrogen_result
        
        # 电力供应
        power_result = self._calculate_power_supply(
            data.power_supply, terminal_total, hydrogen_result
        )
        result['supply_sectors']['电力供应'] = power_result
        
        # ========== 计算一次能源消费汇总 ==========
        primary_total = self._calculate_primary_total(
            terminal_total, hydrogen_result, power_result
        )
        result['summary']['一次能源消费'] = primary_total
        
        # 计算一次能源结构
        primary_structure = self._calculate_primary_structure(primary_total)
        result['summary']['一次能源结构'] = primary_structure
        
        # ========== 计算碳排放汇总 ==========
        # CO2直接排放总量
        total_co2 = self.formulas.calculate_total_co2_emission(
            terminal_total['CO2直接排放'],
            hydrogen_result['CO2直接排放'],
            power_result['CO2直接排放']
        )
        
        # 工业过程CO2
        result['summary']['工业过程'] = data.process_co2
        
        # 非二氧化碳
        result['summary']['非二氧化碳'] = data.non_co2
        
        # CCS
        result['summary']['CCS'] = data.ccs
        
        # 碳汇
        result['summary']['碳汇'] = data.carbon_sink
        
        # 能源相关CO2
        energy_co2 = self.formulas.calculate_energy_related_co2(total_co2, data.ccs)
        result['summary']['能源相关CO2'] = energy_co2
        
        # 温室气体排放
        ghg = self.formulas.calculate_ghg_emission(
            data.process_co2, data.non_co2, energy_co2
        )
        result['summary']['温室气体排放'] = ghg
        
        return result
    
    def _calculate_sector(self, sector: SectorBalanceData) -> Dict[str, float]:
        """计算单个部门的平衡数据"""
        # 计算电热当量
        electricity_tce = self.formulas.calculate_electricity_tce(sector.electricity_twh)
        
        # 计算一次能源小计
        primary_subtotal = self.formulas.calculate_primary_energy_subtotal(
            sector.coal, sector.oil, sector.gas, sector.non_fossil
        )
        
        # 计算终端能源消费
        terminal_energy = self.formulas.calculate_terminal_energy(
            electricity_tce, sector.hydrogen,
            sector.coal, sector.oil, sector.gas, sector.non_fossil
        )
        
        # 计算CO2直接排放
        co2_emission = self.formulas.calculate_co2_emission(
            sector.coal, sector.oil, sector.gas
        )
        
        return {
            '电量': round(sector.electricity_twh, 4),
            '电热当量': round(electricity_tce, 4),
            '氢能消费': round(sector.hydrogen, 4),
            '煤炭': round(sector.coal, 4),
            '石油': round(sector.oil, 4),
            '天然气': round(sector.gas, 4),
            '非化石能源': round(sector.non_fossil, 4),
            '一次能源小计': round(primary_subtotal, 4),
            '终端能源消费': round(terminal_energy, 4),
            '终端消费结构': 0.0,  # 后续计算
            'CO2直接排放': round(co2_emission, 4)
        }
    
    def _calculate_terminal_total(
        self, industry: SectorBalanceData, building: SectorBalanceData,
        transport: SectorBalanceData, other: SectorBalanceData
    ) -> Dict[str, float]:
        """计算终端部门总计"""
        sectors = [industry, building, transport, other]
        
        # 汇总各项
        total_elec_twh = sum(s.electricity_twh for s in sectors)
        total_elec_tce = self.formulas.calculate_electricity_tce(total_elec_twh)
        total_hydrogen = sum(s.hydrogen for s in sectors)
        total_coal = sum(s.coal for s in sectors)
        total_oil = sum(s.oil for s in sectors)
        total_gas = sum(s.gas for s in sectors)
        total_non_fossil = sum(s.non_fossil for s in sectors)
        
        primary_subtotal = self.formulas.calculate_primary_energy_subtotal(
            total_coal, total_oil, total_gas, total_non_fossil
        )
        
        terminal_energy = self.formulas.calculate_terminal_energy(
            total_elec_tce, total_hydrogen,
            total_coal, total_oil, total_gas, total_non_fossil
        )
        
        co2_emission = self.formulas.calculate_co2_emission(
            total_coal, total_oil, total_gas
        )
        
        return {
            '电量': round(total_elec_twh, 4),
            '电热当量': round(total_elec_tce, 4),
            '氢能消费': round(total_hydrogen, 4),
            '煤炭': round(total_coal, 4),
            '石油': round(total_oil, 4),
            '天然气': round(total_gas, 4),
            '非化石能源': round(total_non_fossil, 4),
            '一次能源小计': round(primary_subtotal, 4),
            '终端能源消费': round(terminal_energy, 4),
            '终端消费结构': 1.0,
            'CO2直接排放': round(co2_emission, 4)
        }
    
    def _calculate_power_supply(
        self, power: SectorBalanceData, 
        terminal_total: Dict[str, float],
        hydrogen_result: Dict[str, float]
    ) -> Dict[str, float]:
        """计算电力供应"""
        # 电力供应的电量 = 终端总计电量 + 氢能供应电量
        total_elec_twh = self.formulas.calculate_electricity_total(
            terminal_total['电量'], hydrogen_result['电量']
        )
        total_elec_tce = self.formulas.calculate_electricity_tce(total_elec_twh)
        
        primary_subtotal = self.formulas.calculate_primary_energy_subtotal(
            power.coal, power.oil, power.gas, power.non_fossil
        )
        
        co2_emission = self.formulas.calculate_co2_emission(
            power.coal, power.oil, power.gas
        )
        
        return {
            '电量': round(total_elec_twh, 4),
            '电热当量': round(total_elec_tce, 4),
            '氢能消费': 0.0,
            '煤炭': round(power.coal, 4),
            '石油': round(power.oil, 4),
            '天然气': round(power.gas, 4),
            '非化石能源': round(power.non_fossil, 4),
            '一次能源小计': round(primary_subtotal, 4),
            '终端能源消费': 0.0,
            '终端消费结构': 0.0,
            'CO2直接排放': round(co2_emission, 4)
        }
    
    def _calculate_primary_total(
        self, terminal_total: Dict[str, float],
        hydrogen_result: Dict[str, float],
        power_result: Dict[str, float]
    ) -> Dict[str, float]:
        """计算一次能源消费总量"""
        total_coal = (terminal_total['煤炭'] + 
                      hydrogen_result['煤炭'] + 
                      power_result['煤炭'])
        total_oil = (terminal_total['石油'] + 
                     hydrogen_result['石油'] + 
                     power_result['石油'])
        total_gas = (terminal_total['天然气'] + 
                     hydrogen_result['天然气'] + 
                     power_result['天然气'])
        total_non_fossil = (terminal_total['非化石能源'] + 
                            hydrogen_result['非化石能源'] + 
                            power_result['非化石能源'])
        
        primary_subtotal = self.formulas.calculate_primary_energy_subtotal(
            total_coal, total_oil, total_gas, total_non_fossil
        )
        
        co2_emission = self.formulas.calculate_co2_emission(
            total_coal, total_oil, total_gas
        )
        
        return {
            '煤炭': round(total_coal, 4),
            '石油': round(total_oil, 4),
            '天然气': round(total_gas, 4),
            '非化石能源': round(total_non_fossil, 4),
            '小计': round(primary_subtotal, 4),
            'CO2直接排放': round(co2_emission, 4)
        }
    
    def _calculate_primary_structure(
        self, primary_total: Dict[str, float]
    ) -> Dict[str, float]:
        """计算一次能源结构"""
        total = primary_total['小计']
        
        return {
            '煤炭': round(self.formulas.calculate_primary_structure(
                primary_total['煤炭'], total), 4),
            '石油': round(self.formulas.calculate_primary_structure(
                primary_total['石油'], total), 4),
            '天然气': round(self.formulas.calculate_primary_structure(
                primary_total['天然气'], total), 4),
            '非化石能源': round(self.formulas.calculate_primary_structure(
                primary_total['非化石能源'], total), 4),
            '合计': 1.0
        }
    
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        rows = []
        headers = ['年份', '类别', '部门/项目', '电量/万亿千瓦时', '电热当量/亿tce',
                   '氢能消费/亿tce', '煤炭/亿tce', '石油/亿tce', '天然气/亿tce',
                   '非化石能源/亿tce', '一次能源小计/亿tce', '终端能源消费/亿tce',
                   '终端消费结构/%', 'CO2直接排放/亿吨']
        
        for year in results['years']:
            year_data = results['balance_data'].get(year, {})
            
            # 终端部门
            rows.append([year, '终端部门', '', '', '', '', '', '', '', '', '', '', '', ''])
            for sector in ['工业', '建筑', '交通', '其它', '总计']:
                sector_data = year_data.get('terminal_sectors', {}).get(sector, {})
                rows.append([
                    '', '', sector,
                    f"{sector_data.get('电量', 0):.4f}",
                    f"{sector_data.get('电热当量', 0):.4f}",
                    f"{sector_data.get('氢能消费', 0):.4f}",
                    f"{sector_data.get('煤炭', 0):.4f}",
                    f"{sector_data.get('石油', 0):.4f}",
                    f"{sector_data.get('天然气', 0):.4f}",
                    f"{sector_data.get('非化石能源', 0):.4f}",
                    f"{sector_data.get('一次能源小计', 0):.4f}",
                    f"{sector_data.get('终端能源消费', 0):.4f}",
                    f"{sector_data.get('终端消费结构', 0):.4f}",
                    f"{sector_data.get('CO2直接排放', 0):.4f}"
                ])
            
            # 供应部门
            for sector in ['氢能供应', '电力供应']:
                sector_data = year_data.get('supply_sectors', {}).get(sector, {})
                rows.append([
                    '', sector, '',
                    f"{sector_data.get('电量', 0):.4f}",
                    f"{sector_data.get('电热当量', 0):.4f}",
                    f"{sector_data.get('氢能消费', 0):.4f}",
                    f"{sector_data.get('煤炭', 0):.4f}",
                    f"{sector_data.get('石油', 0):.4f}",
                    f"{sector_data.get('天然气', 0):.4f}",
                    f"{sector_data.get('非化石能源', 0):.4f}",
                    f"{sector_data.get('一次能源小计', 0):.4f}",
                    '', '', f"{sector_data.get('CO2直接排放', 0):.4f}"
                ])
            
            # 一次能源消费
            primary = year_data.get('summary', {}).get('一次能源消费', {})
            rows.append([
                '', '一次能源消费', '', '', '', '',
                f"{primary.get('煤炭', 0):.4f}",
                f"{primary.get('石油', 0):.4f}",
                f"{primary.get('天然气', 0):.4f}",
                f"{primary.get('非化石能源', 0):.4f}",
                f"{primary.get('小计', 0):.4f}",
                '', '', f"{primary.get('CO2直接排放', 0):.4f}"
            ])
            
            # 一次能源结构
            structure = year_data.get('summary', {}).get('一次能源结构', {})
            rows.append([
                '', '一次能源结构', '', '', '', '',
                f"{structure.get('煤炭', 0):.4f}",
                f"{structure.get('石油', 0):.4f}",
                f"{structure.get('天然气', 0):.4f}",
                f"{structure.get('非化石能源', 0):.4f}",
                f"{structure.get('合计', 0):.4f}",
                '', '', ''
            ])
            
            # 碳排放汇总
            summary = year_data.get('summary', {})
            rows.append(['', '工业过程', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('工业过程', 0):.4f}"])
            rows.append(['', '非二氧化碳', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('非二氧化碳', 0):.4f}"])
            rows.append(['', 'CCS', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('CCS', 0):.4f}"])
            rows.append(['', '碳汇', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('碳汇', 0):.4f}"])
            rows.append(['', '能源相关CO2', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('能源相关CO2', 0):.4f}"])
            rows.append(['', '温室气体排放', '', '', '', '', '', '', '', '', '', '', '',
                        f"{summary.get('温室气体排放', 0):.4f}"])
            
            # 空行分隔
            rows.append([''] * len(headers))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
