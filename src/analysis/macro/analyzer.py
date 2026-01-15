# -*- coding: utf-8 -*-
"""宏观测算参考分析器"""

import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import MacroVariables
from .formulas import MacroFormulas


@dataclass
class MacroInputData:
    """宏观测算参考输入数据"""
    # 年份列表
    years: List[str] = field(default_factory=list)
    
    # GDP年增长率（输入）
    gdp_growth_rate: List[float] = field(default_factory=list)
    
    # 5年GDP能源强度下降幅度（输入）
    energy_intensity_decline: List[float] = field(default_factory=list)
    
    # CO2排放因子
    emission_factors: Dict[str, float] = field(default_factory=lambda: {
        '煤': 2.66, '油': 2.12, '气': 1.63
    })
    
    # 基准年数据
    base_year_energy: float = 0.0  # 基准年能源消费量
    base_year_co2: float = 0.0     # 基准年CO2排放量


@dataclass
class SectorData:
    """部门数据（来自各模块计算结果）"""
    # 煤炭消费（亿tce）
    coal: Dict[str, List[float]] = field(default_factory=dict)
    # 石油消费（亿tce）
    oil: Dict[str, List[float]] = field(default_factory=dict)
    # 天然气消费（亿tce）
    gas: Dict[str, List[float]] = field(default_factory=dict)
    # 非化石能源（亿tce）
    non_fossil: Dict[str, List[float]] = field(default_factory=dict)


class MacroAnalyzer:
    """宏观测算参考分析器"""
    
    def __init__(self):
        self.variables = MacroVariables()
        self.formulas = MacroFormulas()
        self.input_data = MacroInputData()
        self.sector_data = SectorData()
        self.module_results: Dict[str, Dict] = {}
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_input_dataframe(df)
    
    def load_input_from_dict(self, data: dict) -> None:
        """从字典加载输入数据"""
        self.input_data.years = data.get('years', [])
        self.input_data.gdp_growth_rate = data.get('gdp_growth_rate', [])
        self.input_data.energy_intensity_decline = data.get('energy_intensity_decline', [])
        self.input_data.emission_factors = data.get('emission_factors', 
                                                     self.input_data.emission_factors)
        self.input_data.base_year_energy = data.get('base_year_energy', 0.0)
        self.input_data.base_year_co2 = data.get('base_year_co2', 0.0)
    
    def _parse_input_dataframe(self, df: pd.DataFrame) -> None:
        """解析输入数据DataFrame"""
        df.columns = ['项目'] + list(df.columns[1:])
        self.input_data.years = [str(c) for c in df.columns[1:]]
        
        for _, row in df.iterrows():
            item_name = str(row['项目']).strip() if pd.notna(row['项目']) else ''
            values = [self._safe_float(row[col]) for col in df.columns[1:]]
            
            if item_name == 'GDP年增长率':
                self.input_data.gdp_growth_rate = values
            elif item_name == '5年GDP能源强度下降幅度':
                self.input_data.energy_intensity_decline = values
            elif item_name == '煤排放因子':
                self.input_data.emission_factors['煤'] = values[0] if values else 2.66
            elif item_name == '油排放因子':
                self.input_data.emission_factors['油'] = values[0] if values else 2.12
            elif item_name == '气排放因子':
                self.input_data.emission_factors['气'] = values[0] if values else 1.63
            elif item_name == '基准年能源消费量':
                self.input_data.base_year_energy = values[0] if values else 0.0
            elif item_name == '基准年CO2排放量':
                self.input_data.base_year_co2 = values[0] if values else 0.0
    
    def load_module_results(self, module_name: str, results: dict) -> None:
        """
        加载模块计算结果
        Args:
            module_name: 模块名称 ('industry', 'building', 'transport', 'power')
            results: 模块计算结果字典
        """
        self.module_results[module_name] = results
    
    def load_sector_data_from_modules(self) -> None:
        """从已加载的模块结果中提取部门数据"""
        years = self.input_data.years
        num_years = len(years)
        
        # 初始化部门数据
        sectors = ['工业', '建筑', '交通', '电力', '制氢', '其他']
        self.sector_data.coal = {s: [0.0] * num_years for s in sectors}
        self.sector_data.oil = {s: [0.0] * num_years for s in sectors}
        self.sector_data.gas = {s: [0.0] * num_years for s in sectors}
        self.sector_data.non_fossil = {
            '工业-生物质': [0.0] * num_years,
            '建筑-生物质': [0.0] * num_years,
            '交通-生物质': [0.0] * num_years,
            '电力-生物质': [0.0] * num_years,
            '其他-生物质': [0.0] * num_years,
            '氢能-生物质': [0.0] * num_years,
            '电力-水能': [0.0] * num_years,
            '电力-核能': [0.0] * num_years,
            '电力-风光': [0.0] * num_years
        }
        
        # 从工业模块提取数据
        if 'industry' in self.module_results:
            industry = self.module_results['industry']
            if 'primary_consumption' in industry:
                pc = industry['primary_consumption']
                self.sector_data.coal['工业'] = pc.get('煤炭', [0.0] * num_years)
                self.sector_data.oil['工业'] = pc.get('石油', [0.0] * num_years)
                self.sector_data.gas['工业'] = pc.get('天然气', [0.0] * num_years)
                self.sector_data.non_fossil['工业-生物质'] = pc.get('生物质', [0.0] * num_years)
        
        # 从建筑模块提取数据
        if 'building' in self.module_results:
            building = self.module_results['building']
            if 'primary_consumption' in building:
                pc = building['primary_consumption']
                self.sector_data.coal['建筑'] = pc.get('煤炭', [0.0] * num_years)
                self.sector_data.oil['建筑'] = pc.get('石油', [0.0] * num_years)
                self.sector_data.gas['建筑'] = pc.get('天然气', [0.0] * num_years)
                self.sector_data.non_fossil['建筑-生物质'] = pc.get('生物质', [0.0] * num_years)
        
        # 从交通模块提取数据
        if 'transport' in self.module_results:
            transport = self.module_results['transport']
            if 'primary_consumption' in transport:
                pc = transport['primary_consumption']
                self.sector_data.coal['交通'] = pc.get('煤炭', [0.0] * num_years)
                self.sector_data.oil['交通'] = pc.get('石油', [0.0] * num_years)
                self.sector_data.gas['交通'] = pc.get('天然气', [0.0] * num_years)
                self.sector_data.non_fossil['交通-生物质'] = pc.get('生物质', [0.0] * num_years)
        
        # 从电力模块提取数据（如果有能源消耗数据）
        # 注意：电力模块的能源消耗数据结构可能不同，需要根据实际情况调整
    
    def load_sector_data_from_csv(self, filepath: str) -> None:
        """从CSV文件加载部门数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_sector_dataframe(df)
    
    def _parse_sector_dataframe(self, df: pd.DataFrame) -> None:
        """解析部门数据DataFrame"""
        df.columns = ['能源类型', '部门'] + list(df.columns[2:])
        years = [str(c) for c in df.columns[2:]]
        num_years = len(years)
        
        if not self.input_data.years:
            self.input_data.years = years
        
        # 初始化
        sectors = ['工业', '建筑', '交通', '电力', '制氢', '其他']
        self.sector_data.coal = {s: [0.0] * num_years for s in sectors}
        self.sector_data.oil = {s: [0.0] * num_years for s in sectors}
        self.sector_data.gas = {s: [0.0] * num_years for s in sectors}
        self.sector_data.non_fossil = {
            '工业-生物质': [0.0] * num_years,
            '建筑-生物质': [0.0] * num_years,
            '交通-生物质': [0.0] * num_years,
            '电力-生物质': [0.0] * num_years,
            '其他-生物质': [0.0] * num_years,
            '氢能-生物质': [0.0] * num_years,
            '电力-水能': [0.0] * num_years,
            '电力-核能': [0.0] * num_years,
            '电力-风光': [0.0] * num_years
        }
        
        current_energy = None
        for _, row in df.iterrows():
            energy_type = str(row['能源类型']).strip() if pd.notna(row['能源类型']) else ''
            sector = str(row['部门']).strip() if pd.notna(row['部门']) else ''
            values = [self._safe_float(row[col]) for col in df.columns[2:]]
            
            if energy_type in ['煤炭', '煤']:
                current_energy = 'coal'
            elif energy_type in ['石油', '油']:
                current_energy = 'oil'
            elif energy_type in ['天然气', '气']:
                current_energy = 'gas'
            elif energy_type == '非化石':
                current_energy = 'non_fossil'
            
            if current_energy == 'coal' and sector in sectors:
                self.sector_data.coal[sector] = values
            elif current_energy == 'oil' and sector in sectors:
                self.sector_data.oil[sector] = values
            elif current_energy == 'gas' and sector in sectors:
                self.sector_data.gas[sector] = values
            elif current_energy == 'non_fossil':
                if sector in self.sector_data.non_fossil:
                    self.sector_data.non_fossil[sector] = values
    
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
        """执行宏观测算分析"""
        years = self.input_data.years
        num_years = len(years)
        
        results = {
            'years': years,
            # 宏观指标
            'macro_indicators': {
                'GDP年增长率': [],
                'GDP指数': [],
                '一次能源指数': [],
                '二氧化碳指数': [],
                '能源消费弹性': [],
                '能源消费年增长率': [],
                '能源消费量': [],
            },
            # 能源结构
            'energy_structure': {
                '煤炭占比': [],
                '石油占比': [],
                '天然气占比': [],
                '非化石占比': [],
            },
            # CO2相关
            'co2_indicators': {
                '单位能耗CO2强度': [],
                '单位能耗CO2强度年下降率': [],
                'CO2排放量': [],
                'CO2排放增长率': [],
                'GDP的CO2强度': [],
                '单位GDP的CO2强度下降率': [],
                '比2005年下降幅度': [],
            },
            # GDP强度相关
            'gdp_intensity': {
                'GDP的能耗强度': [],
                '5年GDP能源强度下降幅度': [],
                '5年GDP的CO2强度下降幅度': [],
                '单位GDP能耗强度年下降率': [],
            },
            # CO2下降相关
            'co2_decline': {
                '二氧化碳年下降率': [],
                '二氧化碳五年累计下降率': [],
                '二氧化碳五年绝对下降量': [],
                '碳捕集量': [],
            },
            # 部门煤炭消费
            'coal_by_sector': {
                '工业': [], '建筑': [], '交通': [], '电力': [],
                '制氢': [], '其他': [], '总量': [], '电煤占比': []
            },
            # 部门石油消费
            'oil_by_sector': {
                '工业': [], '建筑': [], '交通': [], '电力': [],
                '其他': [], '总量': []
            },
            # 部门天然气消费
            'gas_by_sector': {
                '工业': [], '建筑': [], '交通': [], '电力': [],
                '其他': [], '总量': []
            },
            # 非化石能源
            'non_fossil': {
                '工业-生物质': [], '建筑-生物质': [], '交通-生物质': [],
                '电力-生物质': [], '其他-生物质': [], '氢能-生物质': [],
                '生物质总量': [], '电力-水能': [], '电力-核能': [],
                '电力-风光': [], '总量': []
            }
        }
        
        # 计算GDP指数
        gdp_indices = self.formulas.calculate_gdp_index(
            self.input_data.gdp_growth_rate,
            base_index=1.0
        )
        
        # 存储上一期数据用于计算增长率
        prev_energy = self.input_data.base_year_energy
        prev_co2 = self.input_data.base_year_co2
        prev_co2_intensity_gdp = None
        prev_energy_intensity_gdp = None
        base_co2_intensity_gdp = None
        
        for i in range(num_years):
            # GDP年增长率
            gdp_rate = self._get_value(self.input_data.gdp_growth_rate, i)
            results['macro_indicators']['GDP年增长率'].append(round(gdp_rate, 4))
            
            # GDP指数
            gdp_index = gdp_indices[i] if i < len(gdp_indices) else 1.0
            results['macro_indicators']['GDP指数'].append(round(gdp_index, 4))
            
            # 计算各部门能源消费
            # 煤炭
            coal_industry = self._get_value(self.sector_data.coal.get('工业', []), i)
            coal_building = self._get_value(self.sector_data.coal.get('建筑', []), i)
            coal_transport = self._get_value(self.sector_data.coal.get('交通', []), i)
            coal_power = self._get_value(self.sector_data.coal.get('电力', []), i)
            coal_hydrogen = self._get_value(self.sector_data.coal.get('制氢', []), i)
            coal_other = self._get_value(self.sector_data.coal.get('其他', []), i)
            coal_total = self.formulas.calculate_sector_total([
                coal_industry, coal_building, coal_transport, 
                coal_power, coal_hydrogen, coal_other
            ])
            
            results['coal_by_sector']['工业'].append(round(coal_industry, 4))
            results['coal_by_sector']['建筑'].append(round(coal_building, 4))
            results['coal_by_sector']['交通'].append(round(coal_transport, 4))
            results['coal_by_sector']['电力'].append(round(coal_power, 4))
            results['coal_by_sector']['制氢'].append(round(coal_hydrogen, 4))
            results['coal_by_sector']['其他'].append(round(coal_other, 4))
            results['coal_by_sector']['总量'].append(round(coal_total, 4))
            
            # 电煤占比
            power_coal_ratio = self.formulas.calculate_power_coal_ratio(coal_power, coal_total)
            results['coal_by_sector']['电煤占比'].append(round(power_coal_ratio, 4))
            
            # 石油
            oil_industry = self._get_value(self.sector_data.oil.get('工业', []), i)
            oil_building = self._get_value(self.sector_data.oil.get('建筑', []), i)
            oil_transport = self._get_value(self.sector_data.oil.get('交通', []), i)
            oil_power = self._get_value(self.sector_data.oil.get('电力', []), i)
            oil_other = self._get_value(self.sector_data.oil.get('其他', []), i)
            oil_total = self.formulas.calculate_sector_total([
                oil_industry, oil_building, oil_transport, oil_power, oil_other
            ])
            
            results['oil_by_sector']['工业'].append(round(oil_industry, 4))
            results['oil_by_sector']['建筑'].append(round(oil_building, 4))
            results['oil_by_sector']['交通'].append(round(oil_transport, 4))
            results['oil_by_sector']['电力'].append(round(oil_power, 4))
            results['oil_by_sector']['其他'].append(round(oil_other, 4))
            results['oil_by_sector']['总量'].append(round(oil_total, 4))
            
            # 天然气
            gas_industry = self._get_value(self.sector_data.gas.get('工业', []), i)
            gas_building = self._get_value(self.sector_data.gas.get('建筑', []), i)
            gas_transport = self._get_value(self.sector_data.gas.get('交通', []), i)
            gas_power = self._get_value(self.sector_data.gas.get('电力', []), i)
            gas_other = self._get_value(self.sector_data.gas.get('其他', []), i)
            gas_total = self.formulas.calculate_sector_total([
                gas_industry, gas_building, gas_transport, gas_power, gas_other
            ])
            
            results['gas_by_sector']['工业'].append(round(gas_industry, 4))
            results['gas_by_sector']['建筑'].append(round(gas_building, 4))
            results['gas_by_sector']['交通'].append(round(gas_transport, 4))
            results['gas_by_sector']['电力'].append(round(gas_power, 4))
            results['gas_by_sector']['其他'].append(round(gas_other, 4))
            results['gas_by_sector']['总量'].append(round(gas_total, 4))
            
            # 非化石能源
            nf = self.sector_data.non_fossil
            bio_industry = self._get_value(nf.get('工业-生物质', []), i)
            bio_building = self._get_value(nf.get('建筑-生物质', []), i)
            bio_transport = self._get_value(nf.get('交通-生物质', []), i)
            bio_power = self._get_value(nf.get('电力-生物质', []), i)
            bio_other = self._get_value(nf.get('其他-生物质', []), i)
            bio_hydrogen = self._get_value(nf.get('氢能-生物质', []), i)
            hydro = self._get_value(nf.get('电力-水能', []), i)
            nuclear = self._get_value(nf.get('电力-核能', []), i)
            wind_solar = self._get_value(nf.get('电力-风光', []), i)
            
            biomass_total = self.formulas.calculate_biomass_total(
                bio_industry, bio_building, bio_transport, 
                bio_power, bio_other, bio_hydrogen
            )
            non_fossil_total = self.formulas.calculate_non_fossil_total(
                biomass_total, hydro, nuclear, wind_solar
            )
            
            results['non_fossil']['工业-生物质'].append(round(bio_industry, 4))
            results['non_fossil']['建筑-生物质'].append(round(bio_building, 4))
            results['non_fossil']['交通-生物质'].append(round(bio_transport, 4))
            results['non_fossil']['电力-生物质'].append(round(bio_power, 4))
            results['non_fossil']['其他-生物质'].append(round(bio_other, 4))
            results['non_fossil']['氢能-生物质'].append(round(bio_hydrogen, 4))
            results['non_fossil']['生物质总量'].append(round(biomass_total, 4))
            results['non_fossil']['电力-水能'].append(round(hydro, 4))
            results['non_fossil']['电力-核能'].append(round(nuclear, 4))
            results['non_fossil']['电力-风光'].append(round(wind_solar, 4))
            results['non_fossil']['总量'].append(round(non_fossil_total, 4))
            
            # 能源消费总量
            energy_consumption = self.formulas.calculate_energy_consumption(
                coal_total, oil_total, gas_total, non_fossil_total
            )
            results['macro_indicators']['能源消费量'].append(round(energy_consumption, 4))
            
            # 能源结构占比
            coal_ratio = self.formulas.calculate_energy_structure_ratio(coal_total, energy_consumption)
            oil_ratio = self.formulas.calculate_energy_structure_ratio(oil_total, energy_consumption)
            gas_ratio = self.formulas.calculate_energy_structure_ratio(gas_total, energy_consumption)
            non_fossil_ratio = self.formulas.calculate_non_fossil_ratio(coal_ratio, oil_ratio, gas_ratio)
            
            results['energy_structure']['煤炭占比'].append(round(coal_ratio, 2))
            results['energy_structure']['石油占比'].append(round(oil_ratio, 2))
            results['energy_structure']['天然气占比'].append(round(gas_ratio, 2))
            results['energy_structure']['非化石占比'].append(round(non_fossil_ratio, 2))
            
            # 一次能源指数
            base_energy = self.input_data.base_year_energy if self.input_data.base_year_energy > 0 else energy_consumption
            energy_index = self.formulas.calculate_energy_index(energy_consumption, base_energy)
            results['macro_indicators']['一次能源指数'].append(round(energy_index, 4))
            
            # 能源消费弹性
            energy_elasticity = self.formulas.calculate_energy_elasticity(energy_index, gdp_index)
            results['macro_indicators']['能源消费弹性'].append(round(energy_elasticity, 4))
            
            # 能源消费年增长率
            energy_growth = self.formulas.calculate_energy_growth_rate(energy_consumption, prev_energy)
            results['macro_indicators']['能源消费年增长率'].append(round(energy_growth, 4))
            
            # CO2排放量
            emission_factors = self.input_data.emission_factors
            co2_emission = self.formulas.calculate_co2_emission(
                energy_consumption, coal_ratio, oil_ratio, gas_ratio,
                emission_factors.get('煤', 2.66),
                emission_factors.get('油', 2.12),
                emission_factors.get('气', 1.63)
            )
            results['co2_indicators']['CO2排放量'].append(round(co2_emission, 4))
            
            # 二氧化碳指数
            base_co2 = self.input_data.base_year_co2 if self.input_data.base_year_co2 > 0 else co2_emission
            co2_index = self.formulas.calculate_co2_index(co2_emission, base_co2)
            results['macro_indicators']['二氧化碳指数'].append(round(co2_index, 4))
            
            # 单位能耗CO2强度
            co2_intensity_energy = self.formulas.calculate_co2_intensity_per_energy(
                co2_emission, energy_consumption
            )
            results['co2_indicators']['单位能耗CO2强度'].append(round(co2_intensity_energy, 4))
            
            # CO2排放增长率
            co2_growth = self.formulas.calculate_co2_growth_rate(co2_emission, prev_co2)
            results['co2_indicators']['CO2排放增长率'].append(round(co2_growth, 4))
            
            # GDP的CO2强度
            co2_intensity_gdp = self.formulas.calculate_co2_intensity_per_gdp(co2_emission, gdp_index)
            results['co2_indicators']['GDP的CO2强度'].append(round(co2_intensity_gdp, 4))
            
            # 保存基准年CO2强度
            if i == 0:
                base_co2_intensity_gdp = co2_intensity_gdp
            
            # 单位GDP的CO2强度下降率
            if prev_co2_intensity_gdp is not None:
                co2_intensity_decline = self.formulas.calculate_gdp_co2_intensity_decline_rate(
                    co2_intensity_gdp, prev_co2_intensity_gdp
                )
            else:
                co2_intensity_decline = 0.0
            results['co2_indicators']['单位GDP的CO2强度下降率'].append(round(co2_intensity_decline, 4))
            
            # 比2005年下降幅度
            if base_co2_intensity_gdp is not None:
                decline_from_base = self.formulas.calculate_decline_from_base_year(
                    co2_intensity_gdp, base_co2_intensity_gdp
                )
            else:
                decline_from_base = 0.0
            results['co2_indicators']['比2005年下降幅度'].append(round(decline_from_base, 4))
            
            # GDP的能耗强度
            energy_intensity_gdp = self.formulas.calculate_energy_intensity_per_gdp(
                energy_consumption, gdp_index
            )
            results['gdp_intensity']['GDP的能耗强度'].append(round(energy_intensity_gdp, 4))
            
            # 5年GDP能源强度下降幅度
            if prev_energy_intensity_gdp is not None:
                energy_5year_decline = self.formulas.calculate_energy_intensity_5year_decline(
                    energy_intensity_gdp, prev_energy_intensity_gdp
                )
            else:
                energy_5year_decline = 0.0
            results['gdp_intensity']['5年GDP能源强度下降幅度'].append(round(energy_5year_decline, 4))
            
            # 5年GDP的CO2强度下降幅度
            if prev_co2_intensity_gdp is not None:
                co2_5year_decline = self.formulas.calculate_co2_intensity_5year_decline(
                    co2_intensity_gdp, prev_co2_intensity_gdp
                )
            else:
                co2_5year_decline = 0.0
            results['gdp_intensity']['5年GDP的CO2强度下降幅度'].append(round(co2_5year_decline, 4))
            
            # 单位GDP能耗强度年下降率
            if prev_energy_intensity_gdp is not None:
                energy_annual_decline = self.formulas.calculate_energy_intensity_annual_decline(
                    energy_intensity_gdp, prev_energy_intensity_gdp
                )
            else:
                energy_annual_decline = 0.0
            results['gdp_intensity']['单位GDP能耗强度年下降率'].append(round(energy_annual_decline, 4))
            
            # 单位能耗CO2强度年下降率
            # 需要上一期的单位能耗CO2强度
            if i > 0:
                prev_co2_intensity_energy = results['co2_indicators']['单位能耗CO2强度'][i-1]
                co2_energy_decline = self.formulas.calculate_co2_intensity_decline_rate(
                    co2_intensity_energy, prev_co2_intensity_energy
                )
            else:
                co2_energy_decline = 0.0
            results['co2_indicators']['单位能耗CO2强度年下降率'].append(round(co2_energy_decline, 4))
            
            # CO2下降相关
            co2_annual_decline = self.formulas.calculate_co2_annual_decline_rate(co2_emission, prev_co2)
            co2_5year_rate = self.formulas.calculate_co2_5year_decline_rate(co2_emission, prev_co2)
            co2_absolute_decline = self.formulas.calculate_co2_5year_absolute_decline(co2_emission, prev_co2)
            
            results['co2_decline']['二氧化碳年下降率'].append(round(co2_annual_decline, 4))
            results['co2_decline']['二氧化碳五年累计下降率'].append(round(co2_5year_rate, 4))
            results['co2_decline']['二氧化碳五年绝对下降量'].append(round(co2_absolute_decline, 4))
            results['co2_decline']['碳捕集量'].append(0.0)  # 需要从其他模块获取
            
            # 更新上一期数据
            prev_energy = energy_consumption
            prev_co2 = co2_emission
            prev_co2_intensity_gdp = co2_intensity_gdp
            prev_energy_intensity_gdp = energy_intensity_gdp
        
        return results
    
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['项目'] + years
        
        # 宏观指标
        rows.append(['宏观指标'] + [''] * len(years))
        for key in ['GDP年增长率', 'GDP指数', '一次能源指数', '二氧化碳指数', 
                    '能源消费弹性', '能源消费年增长率', '能源消费量']:
            rows.append([key] + [f"{v:.4f}" for v in results['macro_indicators'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # 能源结构
        rows.append(['能源结构(%)'] + [''] * len(years))
        for key in ['煤炭占比', '石油占比', '天然气占比', '非化石占比']:
            rows.append([key] + [f"{v:.2f}" for v in results['energy_structure'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # CO2指标
        rows.append(['CO2指标'] + [''] * len(years))
        for key in ['单位能耗CO2强度', '单位能耗CO2强度年下降率', 'CO2排放量', 
                    'CO2排放增长率', 'GDP的CO2强度', '单位GDP的CO2强度下降率', '比2005年下降幅度']:
            rows.append([key] + [f"{v:.4f}" for v in results['co2_indicators'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # GDP强度
        rows.append(['GDP强度指标'] + [''] * len(years))
        for key in ['GDP的能耗强度', '5年GDP能源强度下降幅度', '5年GDP的CO2强度下降幅度', 
                    '单位GDP能耗强度年下降率']:
            rows.append([key] + [f"{v:.4f}" for v in results['gdp_intensity'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # CO2下降
        rows.append(['CO2下降指标'] + [''] * len(years))
        for key in ['二氧化碳年下降率', '二氧化碳五年累计下降率', '二氧化碳五年绝对下降量', '碳捕集量']:
            rows.append([key] + [f"{v:.4f}" for v in results['co2_decline'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # 煤炭消费
        rows.append(['煤炭消费(亿tce)'] + [''] * len(years))
        for key in ['工业', '建筑', '交通', '电力', '制氢', '其他', '总量', '电煤占比']:
            rows.append([key] + [f"{v:.4f}" for v in results['coal_by_sector'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # 石油消费
        rows.append(['石油消费(亿tce)'] + [''] * len(years))
        for key in ['工业', '建筑', '交通', '电力', '其他', '总量']:
            rows.append([key] + [f"{v:.4f}" for v in results['oil_by_sector'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # 天然气消费
        rows.append(['天然气消费(亿tce)'] + [''] * len(years))
        for key in ['工业', '建筑', '交通', '电力', '其他', '总量']:
            rows.append([key] + [f"{v:.4f}" for v in results['gas_by_sector'][key]])
        
        rows.append([''] * (len(years) + 1))
        
        # 非化石能源
        rows.append(['非化石能源(亿tce)'] + [''] * len(years))
        for key in ['工业-生物质', '建筑-生物质', '交通-生物质', '电力-生物质', 
                    '其他-生物质', '氢能-生物质', '生物质总量', '电力-水能', 
                    '电力-核能', '电力-风光', '总量']:
            rows.append([key] + [f"{v:.4f}" for v in results['non_fossil'][key]])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 100)
        print("宏观测算参考")
        print("=" * 100)
        
        # 打印表头
        header = f"{'项目':<25}" + "".join([f"{y:>12}" for y in years])
        print(header)
        print("-" * 100)
        
        # 宏观指标
        print("【宏观指标】")
        for key in ['GDP年增长率', 'GDP指数', '一次能源指数', '二氧化碳指数', 
                    '能源消费弹性', '能源消费年增长率', '能源消费量']:
            values = results['macro_indicators'][key]
            row = f"  {key:<23}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 100)
        
        # 能源结构
        print("【能源结构(%)】")
        for key in ['煤炭占比', '石油占比', '天然气占比', '非化石占比']:
            values = results['energy_structure'][key]
            row = f"  {key:<23}" + "".join([f"{v:>12.2f}" for v in values])
            print(row)
        
        print("-" * 100)
        
        # CO2指标
        print("【CO2指标】")
        for key in ['单位能耗CO2强度', 'CO2排放量', 'CO2排放增长率', 
                    'GDP的CO2强度', '单位GDP的CO2强度下降率']:
            values = results['co2_indicators'][key]
            row = f"  {key:<23}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 100)
        
        # GDP强度
        print("【GDP强度指标】")
        for key in ['GDP的能耗强度', '5年GDP能源强度下降幅度', '单位GDP能耗强度年下降率']:
            values = results['gdp_intensity'][key]
            row = f"  {key:<23}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 100)
        
        # 能源消费汇总
        print("【能源消费总量(亿tce)】")
        print(f"  {'煤炭':<23}" + "".join([f"{v:>12.4f}" for v in results['coal_by_sector']['总量']]))
        print(f"  {'石油':<23}" + "".join([f"{v:>12.4f}" for v in results['oil_by_sector']['总量']]))
        print(f"  {'天然气':<23}" + "".join([f"{v:>12.4f}" for v in results['gas_by_sector']['总量']]))
        print(f"  {'非化石':<23}" + "".join([f"{v:>12.4f}" for v in results['non_fossil']['总量']]))
        
        print("=" * 100)
