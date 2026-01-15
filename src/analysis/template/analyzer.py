# -*- coding: utf-8 -*-
"""数据模板分析器 - 中国碳中和路径数据汇总"""

import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import TemplateVariables
from .formulas import TemplateFormulas


@dataclass
class SectorData:
    """部门数据结构"""
    # 终端能源消费
    coal: List[float] = field(default_factory=list)      # 煤炭
    oil: List[float] = field(default_factory=list)       # 石油
    gas: List[float] = field(default_factory=list)       # 天然气
    electricity: List[float] = field(default_factory=list)  # 电力
    hydrogen: List[float] = field(default_factory=list)  # 氢能
    non_fossil: List[float] = field(default_factory=list)  # 其它非化石能源
    biomass: List[float] = field(default_factory=list)   # 生物质
    
    # CO2排放
    co2_total: List[float] = field(default_factory=list)
    co2_coal: List[float] = field(default_factory=list)
    co2_oil: List[float] = field(default_factory=list)
    co2_gas: List[float] = field(default_factory=list)
    co2_power: List[float] = field(default_factory=list)


@dataclass 
class PowerData:
    """电力部门数据"""
    # 能源消耗
    energy_coal: List[float] = field(default_factory=list)
    energy_oil: List[float] = field(default_factory=list)
    energy_gas: List[float] = field(default_factory=list)
    energy_non_fossil: List[float] = field(default_factory=list)
    
    # 非化石细分
    wind: List[float] = field(default_factory=list)
    solar: List[float] = field(default_factory=list)
    hydro: List[float] = field(default_factory=list)
    nuclear: List[float] = field(default_factory=list)
    biomass: List[float] = field(default_factory=list)
    
    # 装机容量
    capacity: Dict[str, List[float]] = field(default_factory=dict)
    
    # 发电量
    generation: Dict[str, List[float]] = field(default_factory=dict)
    
    # 电力消费
    consumption: Dict[str, List[float]] = field(default_factory=dict)
    
    # CO2排放
    co2_coal: List[float] = field(default_factory=list)
    co2_gas: List[float] = field(default_factory=list)
    co2_total: List[float] = field(default_factory=list)
    fossil_ccs: List[float] = field(default_factory=list)
    biomass_ccs: List[float] = field(default_factory=list)
    net_emission: List[float] = field(default_factory=list)


@dataclass
class HydrogenData:
    """氢能数据"""
    # 供给
    grey: List[float] = field(default_factory=list)      # 灰氢
    blue: List[float] = field(default_factory=list)      # 蓝氢
    biomass: List[float] = field(default_factory=list)   # 生物质制氢
    electrolysis: List[float] = field(default_factory=list)  # 电制氢
    
    # 效率
    electrolysis_eff: List[float] = field(default_factory=list)
    coal_eff: List[float] = field(default_factory=list)
    biomass_eff: List[float] = field(default_factory=list)
    
    # 消费
    elec_consumption: List[float] = field(default_factory=list)
    coal_consumption: List[float] = field(default_factory=list)
    biomass_consumption: List[float] = field(default_factory=list)
    
    # 需求
    demand_industry: List[float] = field(default_factory=list)
    demand_building: List[float] = field(default_factory=list)
    demand_transport: List[float] = field(default_factory=list)


class TemplateAnalyzer:
    """数据模板分析器"""
    
    def __init__(self):
        self.variables = TemplateVariables()
        self.formulas = TemplateFormulas()
        self.years: List[str] = []
        
        # 部门数据
        self.industry = SectorData()
        self.building = SectorData()
        self.transport = SectorData()
        self.power = PowerData()
        self.hydrogen = HydrogenData()
        
        # 非CO2排放
        self.non_co2_by_sector: Dict[str, List[float]] = {}
        self.non_co2_by_gas: Dict[str, List[float]] = {}
        
        # 碳汇
        self.carbon_sink: List[float] = []
        
        # 生物质汇总
        self.biomass_by_sector: Dict[str, List[float]] = {}
        
        # 模块结果
        self.module_results: Dict[str, Dict] = {}
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        self._parse_input_dataframe(df)
    
    def _parse_input_dataframe(self, df: pd.DataFrame) -> None:
        """解析输入数据"""
        # CSV格式: 部门,类别,项目,单位,2020,2025,...
        # 年份从第5列开始（索引4）
        self.years = [str(c) for c in df.columns[4:] if str(c) != 'nan']
        num_years = len(self.years)
        
        current_section = None
        current_subsection = None
        
        for _, row in df.iterrows():
            section = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            subsection = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            item = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ''
            
            # 更新当前部分
            if section in ['工业部门', '建筑部门', '交通部门', '电力部门', '氢能', '生物质']:
                current_section = section
            
            if subsection:
                current_subsection = subsection
            
            # 获取数值（从第5列开始）
            values = [self._safe_float(row.iloc[i]) for i in range(4, 4 + num_years)]
            
            # 根据部分分配数据
            self._assign_data(current_section, current_subsection, item, values)
            self._assign_data(current_section, current_subsection, item, values)
    
    def _assign_data(self, section: str, subsection: str, item: str, 
                     values: List[float]) -> None:
        """分配数据到对应结构"""
        if section == '工业部门':
            self._assign_industry_data(subsection, item, values)
        elif section == '建筑部门':
            self._assign_building_data(subsection, item, values)
        elif section == '交通部门':
            self._assign_transport_data(subsection, item, values)
        elif section == '电力部门':
            self._assign_power_data(subsection, item, values)
        elif section == '氢能':
            self._assign_hydrogen_data(subsection, item, values)
        elif section == '生物质':
            self._assign_biomass_data(item, values)
    
    def _assign_industry_data(self, subsection: str, item: str, 
                               values: List[float]) -> None:
        """分配工业数据"""
        if item == '煤炭':
            self.industry.coal = values
        elif item == '石油':
            self.industry.oil = values
        elif item == '天然气':
            self.industry.gas = values
        elif item == '电力':
            self.industry.electricity = values
        elif item == '氢能':
            self.industry.hydrogen = values
        elif item == '其它非化石能源':
            self.industry.non_fossil = values
        elif '生物质' in item:
            self.industry.biomass = values
    
    def _assign_building_data(self, subsection: str, item: str,
                               values: List[float]) -> None:
        """分配建筑数据"""
        if item == '煤炭':
            self.building.coal = values
        elif item == '石油':
            self.building.oil = values
        elif item == '天然气':
            self.building.gas = values
        elif item == '电力':
            self.building.electricity = values
        elif item == '氢能':
            self.building.hydrogen = values
        elif item == '其它非化石能源':
            self.building.non_fossil = values
        elif '生物质' in item:
            self.building.biomass = values
    
    def _assign_transport_data(self, subsection: str, item: str,
                                values: List[float]) -> None:
        """分配交通数据"""
        if item == '煤炭':
            self.transport.coal = values
        elif item == '石油':
            self.transport.oil = values
        elif item == '天然气':
            self.transport.gas = values
        elif item == '电力':
            self.transport.electricity = values
        elif item == '氢能':
            self.transport.hydrogen = values
        elif item == '其它非化石能源':
            self.transport.non_fossil = values
        elif '生物质' in item:
            self.transport.biomass = values
    
    def _assign_power_data(self, subsection: str, item: str,
                           values: List[float]) -> None:
        """分配电力数据"""
        if subsection == '能源消耗（来自总电力生产）':
            if item == '煤炭':
                self.power.energy_coal = values
            elif item == '石油':
                self.power.energy_oil = values
            elif item == '天然气':
                self.power.energy_gas = values
            elif item == '其它非化石能源':
                self.power.energy_non_fossil = values
        elif subsection == '其中':
            if item == '风能':
                self.power.wind = values
            elif item == '太阳能':
                self.power.solar = values
            elif item == '水能':
                self.power.hydro = values
            elif item == '核能':
                self.power.nuclear = values
            elif item == '生物质能':
                self.power.biomass = values
        elif subsection == '电力装机数据':
            self.power.capacity[item] = values
        elif subsection == '发电量数据':
            self.power.generation[item] = values
        elif subsection == '电力消费数据':
            self.power.consumption[item] = values
        elif subsection == '直接二氧化碳排放量':
            if item == '来自煤炭':
                self.power.co2_coal = values
            elif item == '来自天然气':
                self.power.co2_gas = values
            elif item == '总直接排放':
                self.power.co2_total = values
            elif item == '化石能源CCS':
                self.power.fossil_ccs = values
            elif item == '生物质CCS':
                self.power.biomass_ccs = values
            elif item == '净排放':
                self.power.net_emission = values
    
    def _assign_hydrogen_data(self, subsection: str, item: str,
                               values: List[float]) -> None:
        """分配氢能数据"""
        if subsection == '氢能供给':
            if item == '灰氢':
                self.hydrogen.grey = values
            elif item == '蓝氢':
                self.hydrogen.blue = values
            elif item == '生物质制氢':
                self.hydrogen.biomass = values
            elif item == '电制氢':
                self.hydrogen.electrolysis = values
        elif subsection == '氢能消费':
            if item == '工业':
                self.hydrogen.demand_industry = values
            elif item == '建筑':
                self.hydrogen.demand_building = values
            elif item == '交通':
                self.hydrogen.demand_transport = values
    
    def _assign_biomass_data(self, item: str, values: List[float]) -> None:
        """分配生物质数据"""
        self.biomass_by_sector[item] = values
    
    def load_module_results(self, module_name: str, results: dict) -> None:
        """加载模块计算结果"""
        self.module_results[module_name] = results
    
    def load_from_modules(self) -> None:
        """从已加载的模块结果提取数据"""
        # 从建筑模块提取
        if 'building' in self.module_results:
            bld = self.module_results['building']
            self.years = bld.get('years', self.years)
            pc = bld.get('primary_consumption', {})
            self.building.coal = pc.get('煤炭', [])
            self.building.oil = pc.get('石油', [])
            self.building.gas = pc.get('天然气', [])
            self.building.biomass = pc.get('生物质', [])
            
            ct = bld.get('consumption_total', {})
            self.building.electricity = [v / 1.229 for v in ct.get('电', [])]  # 转换为万亿kWh
            self.building.hydrogen = ct.get('氢', [])
        
        # 从电力模块提取
        if 'power' in self.module_results:
            pwr = self.module_results['power']
            self.years = pwr.get('years', self.years)
            
            # 装机容量
            cap = pwr.get('capacity', {})
            for key in cap:
                self.power.capacity[key] = cap[key]
            
            # 发电量
            gen = pwr.get('generation', {})
            for key in gen:
                self.power.generation[key] = gen[key]
    
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
        """执行数据模板计算"""
        num_years = len(self.years)
        
        results = {
            'years': self.years,
            # 工业部门
            'industry': {
                'energy': {'煤炭': [], '石油': [], '天然气': [], '电力': [], 
                          '氢能': [], '其它非化石能源': [], '生物质': []},
                'co2': {'直接总排放': [], '来自煤炭': [], '来自石油': [], 
                       '来自天然气': [], '来自电力': []}
            },
            # 建筑部门
            'building': {
                'energy': {'煤炭': [], '石油': [], '天然气': [], '电力': [],
                          '氢能': [], '其它非化石能源': [], '生物质': []},
                'co2': {'直接总排放': [], '来自煤炭': [], '来自石油': [],
                       '来自天然气': [], '来自电力': []}
            },
            # 交通部门
            'transport': {
                'energy': {'煤炭': [], '石油': [], '天然气': [], '电力': [],
                          '氢能': [], '其它非化石能源': [], '生物质': []},
                'co2': {'直接总排放': [], '来自煤炭': [], '来自石油': [],
                       '来自天然气': [], '来自电力': []}
            },
            # 电力部门
            'power': {
                'energy': {'煤炭': [], '石油': [], '天然气': [], '其它非化石能源': []},
                'non_fossil': {'风能': [], '太阳能': [], '水能': [], '核能': [], '生物质能': []},
                'capacity': {},
                'generation': {},
                'consumption': {},
                'co2': {'来自煤炭': [], '来自天然气': [], '总直接排放': [],
                       '化石能源CCS': [], '生物质CCS': [], '净排放': []}
            },
            # 氢能
            'hydrogen': {
                'supply': {'灰氢': [], '蓝氢': [], '生物质制氢': [], '电制氢': []},
                'demand': {'工业': [], '建筑': [], '交通': [], '总氢需求': [], '万吨': []},
                'ratio': {'灰氢比例': [], '蓝氢比例': [], '绿氢比例': []}
            },
            # 生物质
            'biomass': {'工业': [], '建筑': [], '交通': [], '电力': [], '氢能': [], '总计': []},
            # 汇总
            'summary': {
                'total_co2': [],
                'total_energy': []
            }
        }
        
        for i in range(num_years):
            # ========== 工业部门 ==========
            ind_coal = self._get_value(self.industry.coal, i)
            ind_oil = self._get_value(self.industry.oil, i)
            ind_gas = self._get_value(self.industry.gas, i)
            ind_elec = self._get_value(self.industry.electricity, i)
            ind_h2 = self._get_value(self.industry.hydrogen, i)
            ind_nf = self._get_value(self.industry.non_fossil, i)
            ind_bio = self._get_value(self.industry.biomass, i)
            
            results['industry']['energy']['煤炭'].append(round(ind_coal, 4))
            results['industry']['energy']['石油'].append(round(ind_oil, 4))
            results['industry']['energy']['天然气'].append(round(ind_gas, 4))
            results['industry']['energy']['电力'].append(round(ind_elec, 4))
            results['industry']['energy']['氢能'].append(round(ind_h2, 4))
            results['industry']['energy']['其它非化石能源'].append(round(ind_nf, 4))
            results['industry']['energy']['生物质'].append(round(ind_bio, 4))
            
            # 工业CO2排放
            ind_co2_coal = self.formulas.calculate_co2_from_coal(ind_coal)
            ind_co2_oil = self.formulas.calculate_co2_from_oil(ind_oil)
            ind_co2_gas = self.formulas.calculate_co2_from_gas(ind_gas)
            ind_co2_total = self.formulas.calculate_direct_co2_total(
                ind_co2_coal, ind_co2_oil, ind_co2_gas)
            
            results['industry']['co2']['来自煤炭'].append(round(ind_co2_coal, 4))
            results['industry']['co2']['来自石油'].append(round(ind_co2_oil, 4))
            results['industry']['co2']['来自天然气'].append(round(ind_co2_gas, 4))
            results['industry']['co2']['直接总排放'].append(round(ind_co2_total, 4))
            
            # ========== 建筑部门 ==========
            bld_coal = self._get_value(self.building.coal, i)
            bld_oil = self._get_value(self.building.oil, i)
            bld_gas = self._get_value(self.building.gas, i)
            bld_elec = self._get_value(self.building.electricity, i)
            bld_h2 = self._get_value(self.building.hydrogen, i)
            bld_nf = self._get_value(self.building.non_fossil, i)
            bld_bio = self._get_value(self.building.biomass, i)
            
            results['building']['energy']['煤炭'].append(round(bld_coal, 4))
            results['building']['energy']['石油'].append(round(bld_oil, 4))
            results['building']['energy']['天然气'].append(round(bld_gas, 4))
            results['building']['energy']['电力'].append(round(bld_elec, 4))
            results['building']['energy']['氢能'].append(round(bld_h2, 4))
            results['building']['energy']['其它非化石能源'].append(round(bld_nf, 4))
            results['building']['energy']['生物质'].append(round(bld_bio, 4))
            
            # 建筑CO2排放
            bld_co2_coal = self.formulas.calculate_co2_from_coal(bld_coal)
            bld_co2_oil = self.formulas.calculate_co2_from_oil(bld_oil)
            bld_co2_gas = self.formulas.calculate_co2_from_gas(bld_gas)
            bld_co2_total = self.formulas.calculate_direct_co2_total(
                bld_co2_coal, bld_co2_oil, bld_co2_gas)
            
            results['building']['co2']['来自煤炭'].append(round(bld_co2_coal, 4))
            results['building']['co2']['来自石油'].append(round(bld_co2_oil, 4))
            results['building']['co2']['来自天然气'].append(round(bld_co2_gas, 4))
            results['building']['co2']['直接总排放'].append(round(bld_co2_total, 4))
            
            # ========== 交通部门 ==========
            trn_coal = self._get_value(self.transport.coal, i)
            trn_oil = self._get_value(self.transport.oil, i)
            trn_gas = self._get_value(self.transport.gas, i)
            trn_elec = self._get_value(self.transport.electricity, i)
            trn_h2 = self._get_value(self.transport.hydrogen, i)
            trn_nf = self._get_value(self.transport.non_fossil, i)
            trn_bio = self._get_value(self.transport.biomass, i)
            
            results['transport']['energy']['煤炭'].append(round(trn_coal, 4))
            results['transport']['energy']['石油'].append(round(trn_oil, 4))
            results['transport']['energy']['天然气'].append(round(trn_gas, 4))
            results['transport']['energy']['电力'].append(round(trn_elec, 4))
            results['transport']['energy']['氢能'].append(round(trn_h2, 4))
            results['transport']['energy']['其它非化石能源'].append(round(trn_nf, 4))
            results['transport']['energy']['生物质'].append(round(trn_bio, 4))
            
            # 交通CO2排放
            trn_co2_coal = self.formulas.calculate_co2_from_coal(trn_coal)
            trn_co2_oil = self.formulas.calculate_co2_from_oil(trn_oil)
            trn_co2_gas = self.formulas.calculate_co2_from_gas(trn_gas)
            trn_co2_total = self.formulas.calculate_direct_co2_total(
                trn_co2_coal, trn_co2_oil, trn_co2_gas)
            
            results['transport']['co2']['来自煤炭'].append(round(trn_co2_coal, 4))
            results['transport']['co2']['来自石油'].append(round(trn_co2_oil, 4))
            results['transport']['co2']['来自天然气'].append(round(trn_co2_gas, 4))
            results['transport']['co2']['直接总排放'].append(round(trn_co2_total, 4))

            # ========== 电力部门 ==========
            pwr_coal = self._get_value(self.power.energy_coal, i)
            pwr_oil = self._get_value(self.power.energy_oil, i)
            pwr_gas = self._get_value(self.power.energy_gas, i)
            pwr_nf = self._get_value(self.power.energy_non_fossil, i)
            
            results['power']['energy']['煤炭'].append(round(pwr_coal, 4))
            results['power']['energy']['石油'].append(round(pwr_oil, 4))
            results['power']['energy']['天然气'].append(round(pwr_gas, 4))
            results['power']['energy']['其它非化石能源'].append(round(pwr_nf, 4))
            
            # 非化石细分
            results['power']['non_fossil']['风能'].append(
                round(self._get_value(self.power.wind, i), 4))
            results['power']['non_fossil']['太阳能'].append(
                round(self._get_value(self.power.solar, i), 4))
            results['power']['non_fossil']['水能'].append(
                round(self._get_value(self.power.hydro, i), 4))
            results['power']['non_fossil']['核能'].append(
                round(self._get_value(self.power.nuclear, i), 4))
            results['power']['non_fossil']['生物质能'].append(
                round(self._get_value(self.power.biomass, i), 4))
            
            # 电力CO2
            pwr_co2_coal = self._get_value(self.power.co2_coal, i)
            pwr_co2_gas = self._get_value(self.power.co2_gas, i)
            pwr_co2_total = self._get_value(self.power.co2_total, i)
            pwr_fossil_ccs = self._get_value(self.power.fossil_ccs, i)
            pwr_bio_ccs = self._get_value(self.power.biomass_ccs, i)
            pwr_net = self.formulas.calculate_power_net_emission(
                pwr_co2_total, pwr_fossil_ccs, pwr_bio_ccs)
            
            results['power']['co2']['来自煤炭'].append(round(pwr_co2_coal, 4))
            results['power']['co2']['来自天然气'].append(round(pwr_co2_gas, 4))
            results['power']['co2']['总直接排放'].append(round(pwr_co2_total, 4))
            results['power']['co2']['化石能源CCS'].append(round(pwr_fossil_ccs, 4))
            results['power']['co2']['生物质CCS'].append(round(pwr_bio_ccs, 4))
            results['power']['co2']['净排放'].append(round(pwr_net, 4))
            
            # ========== 氢能 ==========
            h2_grey = self._get_value(self.hydrogen.grey, i)
            h2_blue = self._get_value(self.hydrogen.blue, i)
            h2_bio = self._get_value(self.hydrogen.biomass, i)
            h2_elec = self._get_value(self.hydrogen.electrolysis, i)
            
            results['hydrogen']['supply']['灰氢'].append(round(h2_grey, 4))
            results['hydrogen']['supply']['蓝氢'].append(round(h2_blue, 4))
            results['hydrogen']['supply']['生物质制氢'].append(round(h2_bio, 4))
            results['hydrogen']['supply']['电制氢'].append(round(h2_elec, 4))
            
            # 氢能需求
            h2_ind = self._get_value(self.hydrogen.demand_industry, i)
            h2_bld = self._get_value(self.hydrogen.demand_building, i)
            h2_trn = self._get_value(self.hydrogen.demand_transport, i)
            h2_total = self.formulas.calculate_hydrogen_demand_total(h2_ind, h2_bld, h2_trn)
            h2_tons = self.formulas.calculate_hydrogen_in_tons(h2_total)
            
            results['hydrogen']['demand']['工业'].append(round(h2_ind, 4))
            results['hydrogen']['demand']['建筑'].append(round(h2_bld, 4))
            results['hydrogen']['demand']['交通'].append(round(h2_trn, 4))
            results['hydrogen']['demand']['总氢需求'].append(round(h2_total, 4))
            results['hydrogen']['demand']['万吨'].append(round(h2_tons, 4))
            
            # 氢能比例
            h2_supply_total = h2_grey + h2_blue + h2_bio + h2_elec
            grey_ratio = self.formulas.calculate_hydrogen_ratio(h2_grey, h2_supply_total)
            blue_ratio = self.formulas.calculate_hydrogen_ratio(h2_blue, h2_supply_total)
            green_ratio = self.formulas.calculate_hydrogen_ratio(h2_bio + h2_elec, h2_supply_total)
            
            results['hydrogen']['ratio']['灰氢比例'].append(round(grey_ratio, 4))
            results['hydrogen']['ratio']['蓝氢比例'].append(round(blue_ratio, 4))
            results['hydrogen']['ratio']['绿氢比例'].append(round(green_ratio, 4))
            
            # ========== 生物质 ==========
            bio_ind = self._get_value(self.biomass_by_sector.get('工业', []), i)
            bio_bld = self._get_value(self.biomass_by_sector.get('建筑', []), i)
            bio_trn = self._get_value(self.biomass_by_sector.get('交通', []), i)
            bio_pwr = self._get_value(self.biomass_by_sector.get('电力', []), i)
            bio_h2 = self._get_value(self.biomass_by_sector.get('氢能', []), i)
            bio_total = self.formulas.calculate_biomass_total(
                bio_ind, bio_bld, bio_trn, bio_pwr, bio_h2)
            
            results['biomass']['工业'].append(round(bio_ind, 4))
            results['biomass']['建筑'].append(round(bio_bld, 4))
            results['biomass']['交通'].append(round(bio_trn, 4))
            results['biomass']['电力'].append(round(bio_pwr, 4))
            results['biomass']['氢能'].append(round(bio_h2, 4))
            results['biomass']['总计'].append(round(bio_total, 4))
            
            # ========== 汇总 ==========
            total_co2 = ind_co2_total + bld_co2_total + trn_co2_total + pwr_net
            results['summary']['total_co2'].append(round(total_co2, 4))
            
            total_energy = (ind_coal + ind_oil + ind_gas + ind_nf +
                           bld_coal + bld_oil + bld_gas + bld_nf +
                           trn_coal + trn_oil + trn_gas + trn_nf +
                           pwr_coal + pwr_oil + pwr_gas + pwr_nf)
            results['summary']['total_energy'].append(round(total_energy, 4))
        
        # 处理装机容量和发电量
        for key, values in self.power.capacity.items():
            results['power']['capacity'][key] = [round(self._get_value(values, i), 4) 
                                                  for i in range(num_years)]
        
        for key, values in self.power.generation.items():
            results['power']['generation'][key] = [round(self._get_value(values, i), 4)
                                                    for i in range(num_years)]
        
        for key, values in self.power.consumption.items():
            results['power']['consumption'][key] = [round(self._get_value(values, i), 4)
                                                     for i in range(num_years)]
        
        # 计算间接CO2排放（来自电力）
        for i in range(num_years):
            pwr_net = results['power']['co2']['净排放'][i]
            total_pwr_cons = self._get_value(
                self.power.consumption.get('电力消费总量', []), i)
            
            ind_elec = results['industry']['energy']['电力'][i]
            bld_elec = results['building']['energy']['电力'][i]
            trn_elec = results['transport']['energy']['电力'][i]
            
            ind_co2_pwr = self.formulas.calculate_indirect_co2_from_power(
                ind_elec, pwr_net, total_pwr_cons)
            bld_co2_pwr = self.formulas.calculate_indirect_co2_from_power(
                bld_elec, pwr_net, total_pwr_cons)
            trn_co2_pwr = self.formulas.calculate_indirect_co2_from_power(
                trn_elec, pwr_net, total_pwr_cons)
            
            results['industry']['co2']['来自电力'].append(round(ind_co2_pwr, 4))
            results['building']['co2']['来自电力'].append(round(bld_co2_pwr, 4))
            results['transport']['co2']['来自电力'].append(round(trn_co2_pwr, 4))
        
        return results

    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['部门', '类别', '项目', '单位'] + years
        
        # 工业部门
        rows.append(['工业部门', '', '', ''] + [''] * len(years))
        rows.append(['', '终端能源消费量', '', ''] + [''] * len(years))
        for key in ['煤炭', '石油', '天然气']:
            unit = '亿tce'
            rows.append(['', '', key, unit] + [f"{v:.4f}" for v in results['industry']['energy'][key]])
        rows.append(['', '', '电力', '万亿kWh'] + [f"{v:.4f}" for v in results['industry']['energy']['电力']])
        rows.append(['', '', '氢能', '亿tce'] + [f"{v:.4f}" for v in results['industry']['energy']['氢能']])
        rows.append(['', '', '其它非化石能源', '亿tce'] + [f"{v:.4f}" for v in results['industry']['energy']['其它非化石能源']])
        rows.append(['', '', '生物质', '亿tce'] + [f"{v:.4f}" for v in results['industry']['energy']['生物质']])
        
        rows.append(['', '直接CO2排放', '', ''] + [''] * len(years))
        for key in ['直接总排放', '来自煤炭', '来自石油', '来自天然气']:
            rows.append(['', '', key, '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['co2'][key]])
        rows.append(['', '间接CO2排放', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['industry']['co2']['来自电力']])
        
        rows.append([''] * (4 + len(years)))
        
        # 建筑部门
        rows.append(['建筑部门', '', '', ''] + [''] * len(years))
        rows.append(['', '终端能源消费量', '', ''] + [''] * len(years))
        for key in ['煤炭', '石油', '天然气']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['building']['energy'][key]])
        rows.append(['', '', '电力', '万亿kWh'] + [f"{v:.4f}" for v in results['building']['energy']['电力']])
        rows.append(['', '', '氢能', '亿tce'] + [f"{v:.4f}" for v in results['building']['energy']['氢能']])
        rows.append(['', '', '其它非化石能源', '亿tce'] + [f"{v:.4f}" for v in results['building']['energy']['其它非化石能源']])
        rows.append(['', '', '生物质', '亿tce'] + [f"{v:.4f}" for v in results['building']['energy']['生物质']])
        
        rows.append(['', '直接CO2排放', '', ''] + [''] * len(years))
        for key in ['直接总排放', '来自煤炭', '来自石油', '来自天然气']:
            rows.append(['', '', key, '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['co2'][key]])
        rows.append(['', '间接CO2排放', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['building']['co2']['来自电力']])
        
        rows.append([''] * (4 + len(years)))
        
        # 交通部门
        rows.append(['交通部门', '', '', ''] + [''] * len(years))
        rows.append(['', '终端能源消费量', '', ''] + [''] * len(years))
        for key in ['煤炭', '石油', '天然气']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['transport']['energy'][key]])
        rows.append(['', '', '电力', '万亿kWh'] + [f"{v:.4f}" for v in results['transport']['energy']['电力']])
        rows.append(['', '', '氢能', '亿tce'] + [f"{v:.4f}" for v in results['transport']['energy']['氢能']])
        rows.append(['', '', '其它非化石能源', '亿tce'] + [f"{v:.4f}" for v in results['transport']['energy']['其它非化石能源']])
        rows.append(['', '', '生物质', '亿tce'] + [f"{v:.4f}" for v in results['transport']['energy']['生物质']])
        
        rows.append(['', '直接CO2排放', '', ''] + [''] * len(years))
        for key in ['直接总排放', '来自煤炭', '来自石油', '来自天然气']:
            rows.append(['', '', key, '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['co2'][key]])
        rows.append(['', '间接CO2排放', '来自电力', '亿吨CO2'] + [f"{v:.4f}" for v in results['transport']['co2']['来自电力']])
        
        rows.append([''] * (4 + len(years)))
        
        # 电力部门
        rows.append(['电力部门', '', '', ''] + [''] * len(years))
        rows.append(['', '能源消耗', '', ''] + [''] * len(years))
        for key in ['煤炭', '石油', '天然气', '其它非化石能源']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['power']['energy'][key]])
        
        rows.append(['', '非化石细分', '', ''] + [''] * len(years))
        for key in ['风能', '太阳能', '水能', '核能', '生物质能']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['power']['non_fossil'][key]])
        
        rows.append(['', 'CO2排放', '', ''] + [''] * len(years))
        for key in ['来自煤炭', '来自天然气', '总直接排放', '化石能源CCS', '生物质CCS', '净排放']:
            rows.append(['', '', key, '亿吨CO2'] + [f"{v:.4f}" for v in results['power']['co2'][key]])
        
        rows.append([''] * (4 + len(years)))
        
        # 氢能
        rows.append(['氢能', '', '', ''] + [''] * len(years))
        rows.append(['', '氢能供给', '', ''] + [''] * len(years))
        for key in ['灰氢', '蓝氢', '生物质制氢', '电制氢']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['hydrogen']['supply'][key]])
        
        rows.append(['', '氢能需求', '', ''] + [''] * len(years))
        for key in ['工业', '建筑', '交通', '总氢需求']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['hydrogen']['demand'][key]])
        rows.append(['', '', '总氢需求', '万吨'] + [f"{v:.4f}" for v in results['hydrogen']['demand']['万吨']])
        
        rows.append(['', '氢能比例', '', ''] + [''] * len(years))
        for key in ['灰氢比例', '蓝氢比例', '绿氢比例']:
            rows.append(['', '', key, '%'] + [f"{v*100:.2f}" for v in results['hydrogen']['ratio'][key]])
        
        rows.append([''] * (4 + len(years)))
        
        # 生物质
        rows.append(['生物质', '', '', ''] + [''] * len(years))
        for key in ['工业', '建筑', '交通', '电力', '氢能', '总计']:
            rows.append(['', '', key, '亿tce'] + [f"{v:.4f}" for v in results['biomass'][key]])
        
        rows.append([''] * (4 + len(years)))
        
        # 汇总
        rows.append(['汇总', '', '', ''] + [''] * len(years))
        rows.append(['', '', '总CO2排放', '亿吨CO2'] + [f"{v:.4f}" for v in results['summary']['total_co2']])
        rows.append(['', '', '总能源消费', '亿tce'] + [f"{v:.4f}" for v in results['summary']['total_energy']])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")

    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 120)
        print("数据模板 - 中国碳中和路径")
        print("=" * 120)
        
        # 打印表头
        header = f"{'部门':<8}{'类别':<12}{'项目':<16}{'单位':<10}" + "".join([f"{y:>10}" for y in years])
        print(header)
        print("-" * 120)
        
        # 工业部门
        print("【工业部门】")
        print("  终端能源消费量")
        for key in ['煤炭', '石油', '天然气']:
            values = results['industry']['energy'][key]
            print(f"    {key:<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        values = results['industry']['energy']['电力']
        print(f"    {'电力':<14}{'万亿kWh':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("  直接CO2排放")
        for key in ['直接总排放', '来自煤炭', '来自石油', '来自天然气']:
            values = results['industry']['co2'][key]
            print(f"    {key:<14}{'亿吨CO2':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 建筑部门
        print("【建筑部门】")
        print("  终端能源消费量")
        for key in ['煤炭', '石油', '天然气']:
            values = results['building']['energy'][key]
            print(f"    {key:<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        values = results['building']['energy']['电力']
        print(f"    {'电力':<14}{'万亿kWh':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("  直接CO2排放")
        for key in ['直接总排放']:
            values = results['building']['co2'][key]
            print(f"    {key:<14}{'亿吨CO2':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 交通部门
        print("【交通部门】")
        print("  终端能源消费量")
        for key in ['煤炭', '石油', '天然气']:
            values = results['transport']['energy'][key]
            print(f"    {key:<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        values = results['transport']['energy']['电力']
        print(f"    {'电力':<14}{'万亿kWh':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("  直接CO2排放")
        for key in ['直接总排放']:
            values = results['transport']['co2'][key]
            print(f"    {key:<14}{'亿吨CO2':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 电力部门
        print("【电力部门】")
        print("  能源消耗")
        for key in ['煤炭', '石油', '天然气', '其它非化石能源']:
            values = results['power']['energy'][key]
            print(f"    {key:<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("  CO2排放")
        for key in ['总直接排放', '净排放']:
            values = results['power']['co2'][key]
            print(f"    {key:<14}{'亿吨CO2':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 氢能
        print("【氢能】")
        print("  氢能供给")
        for key in ['灰氢', '蓝氢', '生物质制氢', '电制氢']:
            values = results['hydrogen']['supply'][key]
            print(f"    {key:<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("  氢能需求")
        values = results['hydrogen']['demand']['总氢需求']
        print(f"    {'总氢需求':<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        values = results['hydrogen']['demand']['万吨']
        print(f"    {'总氢需求':<14}{'万吨':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 生物质
        print("【生物质】")
        values = results['biomass']['总计']
        print(f"    {'总计':<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("-" * 120)
        
        # 汇总
        print("【汇总】")
        values = results['summary']['total_co2']
        print(f"    {'总CO2排放':<14}{'亿吨CO2':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        values = results['summary']['total_energy']
        print(f"    {'总能源消费':<14}{'亿tce':<10}" + "".join([f"{v:>10.4f}" for v in values]))
        
        print("=" * 120)
