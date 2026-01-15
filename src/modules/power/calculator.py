# -*- coding: utf-8 -*-
"""电力结果计算器"""

import csv
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ...base import BaseCalculator
from .variables import PowerVariables
from .formulas import PowerFormulas


@dataclass
class PowerData:
    """电力结果数据结构"""
    # 年份列表
    years: List[str] = field(default_factory=list)
    
    # 发电量数据 (万亿kWh) - 行23-33
    generation: Dict[str, List[float]] = field(default_factory=dict)
    
    # 利用小时数 (小时) - 行56-66
    utilization_hours: Dict[str, List[float]] = field(default_factory=dict)
    
    # 储能装机 (GW) - 行18-19
    storage: Dict[str, List[float]] = field(default_factory=dict)
    
    # 传输损耗 (百分比) - 行35
    transmission_loss: List[float] = field(default_factory=list)
    
    # 误差 (百分比) - 行36
    error_rate: List[float] = field(default_factory=list)
    
    # 跨区传输容量 (万亿kWh) - 行37
    cross_region_capacity: List[float] = field(default_factory=list)
    
    # 电制氢需求 (万亿kWh) - 行68
    hydrogen_demand: List[float] = field(default_factory=list)
    
    # 电力需求 (万亿kWh) - 行69
    electricity_demand: List[float] = field(default_factory=list)
    
    # CCS改造系数 (百分比) - 行93-95
    ccs_retrofit_factor: Dict[str, List[float]] = field(default_factory=dict)
    
    # 燃料消耗率 - 行98-104
    fuel_rate: Dict[str, List[float]] = field(default_factory=dict)
    
    # CCS捕集率 (百分比) - 行105
    ccs_capture_rate: List[float] = field(default_factory=list)
    
    # 装机成本 (万/MW) - 行117-130
    capacity_cost: Dict[str, List[float]] = field(default_factory=dict)
    
    # 运维成本占比 (百分比) - 行132-143
    om_ratio: Dict[str, List[float]] = field(default_factory=dict)
    
    # 燃料成本 (元/kWh) - 行145-156
    fuel_cost: Dict[str, List[float]] = field(default_factory=dict)
    
    # 海上风电占比 (百分比) - 行171
    offshore_wind_ratio: List[float] = field(default_factory=list)
    
    # 分布式光伏占比 (百分比) - 行172
    distributed_solar_ratio: List[float] = field(default_factory=list)
    
    # 设备寿命 - 行N117-N130
    equipment_lifetime: Dict[str, int] = field(default_factory=dict)
    
    # CO2排放系数
    coal_co2_factor: float = 2.66
    gas_co2_factor: float = 2.16
    gas_conversion_factor: float = 1.33


class PowerCalculator(BaseCalculator):
    """电力结果计算器"""
    
    def __init__(self):
        super().__init__()
        self.variables = PowerVariables()
        self.formulas = PowerFormulas()
        self.power_data = PowerData()
    
    def load_from_dict(self, data: dict) -> None:
        """从字典加载数据"""
        self.power_data.years = data.get('years', [])
        self.power_data.generation = data.get('generation', {})
        self.power_data.utilization_hours = data.get('utilization_hours', {})
        self.power_data.storage = data.get('storage', {})
        self.power_data.transmission_loss = data.get('transmission_loss', [])
        self.power_data.error_rate = data.get('error_rate', [])
        self.power_data.cross_region_capacity = data.get('cross_region_capacity', [])
        self.power_data.hydrogen_demand = data.get('hydrogen_demand', [])
        self.power_data.electricity_demand = data.get('electricity_demand', [])
        self.power_data.ccs_retrofit_factor = data.get('ccs_retrofit_factor', {})
        self.power_data.fuel_rate = data.get('fuel_rate', {})
        self.power_data.ccs_capture_rate = data.get('ccs_capture_rate', [])
        self.power_data.capacity_cost = data.get('capacity_cost', {})
        self.power_data.om_ratio = data.get('om_ratio', {})
        self.power_data.fuel_cost = data.get('fuel_cost', {})
        self.power_data.offshore_wind_ratio = data.get('offshore_wind_ratio', [])
        self.power_data.distributed_solar_ratio = data.get('distributed_solar_ratio', [])
        self.power_data.equipment_lifetime = data.get('equipment_lifetime', 
                                                       self.variables.EQUIPMENT_LIFETIME)
    
    def _parse_dataframe(self, df: pd.DataFrame) -> None:
        """解析DataFrame数据"""
        df.columns = ['项目'] + list(df.columns[1:])
        self.power_data.years = [str(c) for c in df.columns[1:]]
        
        # 初始化数据字典
        generation_types = ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电', 
                           '风电', '光伏', '生物质', '生物质+CCS', '其他']
        self.power_data.generation = {k: [] for k in generation_types}
        self.power_data.utilization_hours = {k: [] for k in generation_types}
        
        storage_types = ['抽蓄', '电化学']
        self.power_data.storage = {k: [] for k in storage_types}
        
        ccs_types = ['煤电', '气电', '生物质']
        self.power_data.ccs_retrofit_factor = {k: [] for k in ccs_types}
        
        fuel_types = ['煤炭', '煤炭CCS', '天然气', '天然气CCS', '生物质', '生物质CCS', '浓缩铀']
        self.power_data.fuel_rate = {k: [] for k in fuel_types}
        
        cost_types = ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                     '风电(陆上)', '风电(海上)', '光伏(集中)', '光伏(分布式)',
                     '生物质', '生物质+CCS', '抽蓄', '电化学']
        self.power_data.capacity_cost = {k: [] for k in cost_types}
        
        om_types = ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电(陆上)', '风电(海上)', '光伏(集中)', '光伏(分布式)',
                   '生物质', '生物质+CCS']
        self.power_data.om_ratio = {k: [] for k in om_types}
        self.power_data.fuel_cost = {k: [] for k in om_types}
        
        # 当前解析的数据类别
        current_category = None
        
        for _, row in df.iterrows():
            item_name = str(row['项目']).strip() if pd.notna(row['项目']) else ''
            values = [self.safe_float(row[col]) for col in df.columns[1:]]
            
            # 识别数据类别
            if item_name in ['发电量数据', '发电量']:
                current_category = 'generation'
                continue
            elif item_name in ['利用小时数', '利用小时']:
                current_category = 'utilization_hours'
                continue
            elif item_name in ['储能配置', '储能']:
                current_category = 'storage'
                continue
            elif item_name in ['CCS改造容量变化系数', 'CCS改造系数']:
                current_category = 'ccs_retrofit'
                continue
            elif item_name in ['燃料消耗率', '燃料消耗']:
                current_category = 'fuel_rate'
                continue
            elif item_name in ['装机成本(单价)', '装机成本']:
                current_category = 'capacity_cost'
                continue
            elif item_name in ['运维成本(单价)', '运维成本占比']:
                current_category = 'om_ratio'
                continue
            elif item_name in ['燃料成本(单价)', '燃料成本']:
                current_category = 'fuel_cost'
                continue
            
            # 解析具体数据
            if current_category == 'generation' and item_name in generation_types:
                self.power_data.generation[item_name] = values
            elif current_category == 'utilization_hours' and item_name in generation_types:
                self.power_data.utilization_hours[item_name] = values
            elif current_category == 'storage' and item_name in storage_types:
                self.power_data.storage[item_name] = values
            elif current_category == 'ccs_retrofit' and item_name in ccs_types:
                self.power_data.ccs_retrofit_factor[item_name] = values
            elif current_category == 'fuel_rate':
                if item_name in fuel_types:
                    self.power_data.fuel_rate[item_name] = values
                elif item_name == 'CCS捕集率':
                    self.power_data.ccs_capture_rate = values
            elif current_category == 'capacity_cost' and item_name in cost_types:
                self.power_data.capacity_cost[item_name] = values
            elif current_category == 'om_ratio' and item_name in om_types:
                self.power_data.om_ratio[item_name] = values
            elif current_category == 'fuel_cost' and item_name in om_types:
                self.power_data.fuel_cost[item_name] = values
            
            # 解析其他单独的数据项
            if item_name == '传输损耗':
                self.power_data.transmission_loss = values
            elif item_name == '误差':
                self.power_data.error_rate = values
            elif item_name == '跨区传输容量':
                self.power_data.cross_region_capacity = values
            elif item_name == '电制氢':
                self.power_data.hydrogen_demand = values
            elif item_name == '电力需求':
                self.power_data.electricity_demand = values
            elif item_name == '海上风电占比':
                self.power_data.offshore_wind_ratio = values
            elif item_name == '分布式光伏占比':
                self.power_data.distributed_solar_ratio = values
        
        # 设置默认设备寿命
        self.power_data.equipment_lifetime = self.variables.EQUIPMENT_LIFETIME
    
    def _get_value(self, data_dict: dict, key: str, index: int, 
                   default: float = 0.0) -> float:
        """安全获取字典中的值"""
        values = data_dict.get(key, [])
        if index < len(values):
            return values[index]
        return default
    
    def _get_list_value(self, data_list: list, index: int, 
                        default: float = 0.0) -> float:
        """安全获取列表中的值"""
        if index < len(data_list):
            return data_list[index]
        return default

    
    def calculate(self) -> Dict[str, Any]:
        """执行所有计算"""
        years = self.power_data.years
        num_years = len(years)
        
        results = {
            'years': years,
            # 装机容量 (GW)
            'capacity': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '风电': [], '光伏': [],
                '生物质': [], '生物质+CCS': [], '其他': [], '总装机': []
            },
            # 装机结构
            'capacity_structure': {
                '非化石占比': [], '风光占比': [], '煤电占比': []
            },
            # 储能装机 (GW)
            'storage': {
                '抽蓄': [], '电化学': [], '总装机': [], '储能/新能源': []
            },
            # 发电量 (万亿kWh)
            'generation': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '风电': [], '光伏': [],
                '生物质': [], '生物质+CCS': [], '其他': [], '总发电量': []
            },
            # 发电量占比
            'generation_ratio': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '风电': [], '光伏': [],
                '生物质': [], '生物质+CCS': [], '其他': [], '风光占比': []
            },
            # 发电结构
            'generation_structure': {
                '非化石占比': [], '风光占比': [], '煤电占比': []
            },
            # 供需平衡 (万亿kWh)
            'supply_demand': {
                '电制氢': [], '电力需求': [], '总需求': [],
                '传输损耗': [], '跨区传输': []
            },
            # 碳捕集占比
            'ccs_ratio': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '生物质': [], '生物质+CCS': []
            },
            # CO2排放 (亿吨CO2)
            'co2_emission': {
                '来自煤炭': [], '来自天然气': [], '总直接排放': [],
                '化石能源CCS': [], '生物质CCS': [], '净排放': []
            },
            # 投资成本 (亿元)
            'investment': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '风电(陆上)': [], '风电(海上)': [],
                '光伏(集中)': [], '光伏(分布式)': [], '生物质': [], '生物质+CCS': [],
                '抽蓄': [], '电化学': [], '总电源投资': [], '总储能投资': [],
                '跨省电网': [], '省内电网': []
            },
            # 运维成本 (亿元)
            'om_cost': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '风电(陆上)': [], '风电(海上)': [],
                '光伏(集中)': [], '光伏(分布式)': [], '生物质': [], '生物质+CCS': [],
                '总运维成本': []
            },
            # 燃料成本 (亿元)
            'fuel_cost_total': {
                '煤电': [], '煤电+CCS': [], '气电': [], '气电+CCS': [],
                '核电': [], '水电': [], '生物质': [], '生物质+CCS': [],
                '总燃料成本': []
            },
            # 总成本 (亿元)
            'total_cost': {
                '总成本': []
            },
            # LCOE (元/kWh)
            'lcoe': {
                '电源投资': [], '储能投资': [], '电网投资(跨省)': [],
                '电网投资(省内)': [], '运维成本': [], '燃料成本': [], 'LCOE': []
            }
        }
        
        for i in range(num_years):
            # ==================== 发电量 ====================
            gen = self.power_data.generation
            coal_gen = self._get_value(gen, '煤电', i)
            coal_ccs_gen = self._get_value(gen, '煤电+CCS', i)
            gas_gen = self._get_value(gen, '气电', i)
            gas_ccs_gen = self._get_value(gen, '气电+CCS', i)
            nuclear_gen = self._get_value(gen, '核电', i)
            hydro_gen = self._get_value(gen, '水电', i)
            wind_gen = self._get_value(gen, '风电', i)
            solar_gen = self._get_value(gen, '光伏', i)
            biomass_gen = self._get_value(gen, '生物质', i)
            biomass_ccs_gen = self._get_value(gen, '生物质+CCS', i)
            other_gen = self._get_value(gen, '其他', i)
            
            total_gen = self.formulas.calculate_total_generation([
                coal_gen, coal_ccs_gen, gas_gen, gas_ccs_gen, nuclear_gen,
                hydro_gen, wind_gen, solar_gen, biomass_gen, biomass_ccs_gen, other_gen
            ])
            
            results['generation']['煤电'].append(round(coal_gen, 4))
            results['generation']['煤电+CCS'].append(round(coal_ccs_gen, 4))
            results['generation']['气电'].append(round(gas_gen, 4))
            results['generation']['气电+CCS'].append(round(gas_ccs_gen, 4))
            results['generation']['核电'].append(round(nuclear_gen, 4))
            results['generation']['水电'].append(round(hydro_gen, 4))
            results['generation']['风电'].append(round(wind_gen, 4))
            results['generation']['光伏'].append(round(solar_gen, 4))
            results['generation']['生物质'].append(round(biomass_gen, 4))
            results['generation']['生物质+CCS'].append(round(biomass_ccs_gen, 4))
            results['generation']['其他'].append(round(other_gen, 4))
            results['generation']['总发电量'].append(round(total_gen, 4))
            
            # ==================== 利用小时数和装机容量 ====================
            hours = self.power_data.utilization_hours
            coal_hours = self._get_value(hours, '煤电', i)
            coal_ccs_hours = self._get_value(hours, '煤电+CCS', i)
            gas_hours = self._get_value(hours, '气电', i)
            gas_ccs_hours = self._get_value(hours, '气电+CCS', i)
            nuclear_hours = self._get_value(hours, '核电', i)
            hydro_hours = self._get_value(hours, '水电', i)
            wind_hours = self._get_value(hours, '风电', i)
            solar_hours = self._get_value(hours, '光伏', i)
            biomass_hours = self._get_value(hours, '生物质', i)
            biomass_ccs_hours = self._get_value(hours, '生物质+CCS', i)
            other_hours = self._get_value(hours, '其他', i)
            
            # 计算装机容量
            coal_cap = self.formulas.calculate_capacity_from_generation(coal_gen, coal_hours)
            coal_ccs_cap = self.formulas.calculate_capacity_from_generation(coal_ccs_gen, coal_ccs_hours)
            gas_cap = self.formulas.calculate_capacity_from_generation(gas_gen, gas_hours)
            gas_ccs_cap = self.formulas.calculate_capacity_from_generation(gas_ccs_gen, gas_ccs_hours)
            nuclear_cap = self.formulas.calculate_capacity_from_generation(nuclear_gen, nuclear_hours)
            hydro_cap = self.formulas.calculate_capacity_from_generation(hydro_gen, hydro_hours)
            wind_cap = self.formulas.calculate_capacity_from_generation(wind_gen, wind_hours)
            solar_cap = self.formulas.calculate_capacity_from_generation(solar_gen, solar_hours)
            biomass_cap = self.formulas.calculate_capacity_from_generation(biomass_gen, biomass_hours)
            biomass_ccs_cap = self.formulas.calculate_capacity_from_generation(biomass_ccs_gen, biomass_ccs_hours)
            other_cap = self.formulas.calculate_capacity_from_generation(other_gen, other_hours)
            
            total_cap = self.formulas.calculate_total_capacity([
                coal_cap, coal_ccs_cap, gas_cap, gas_ccs_cap, nuclear_cap,
                hydro_cap, wind_cap, solar_cap, biomass_cap, biomass_ccs_cap, other_cap
            ])
            
            results['capacity']['煤电'].append(round(coal_cap, 2))
            results['capacity']['煤电+CCS'].append(round(coal_ccs_cap, 2))
            results['capacity']['气电'].append(round(gas_cap, 2))
            results['capacity']['气电+CCS'].append(round(gas_ccs_cap, 2))
            results['capacity']['核电'].append(round(nuclear_cap, 2))
            results['capacity']['水电'].append(round(hydro_cap, 2))
            results['capacity']['风电'].append(round(wind_cap, 2))
            results['capacity']['光伏'].append(round(solar_cap, 2))
            results['capacity']['生物质'].append(round(biomass_cap, 2))
            results['capacity']['生物质+CCS'].append(round(biomass_ccs_cap, 2))
            results['capacity']['其他'].append(round(other_cap, 2))
            results['capacity']['总装机'].append(round(total_cap, 2))
            
            # 装机结构
            non_fossil_cap_ratio = self.formulas.calculate_non_fossil_capacity_ratio(
                nuclear_cap, hydro_cap, wind_cap, solar_cap, 
                biomass_cap, biomass_ccs_cap, other_cap, total_cap
            )
            wind_solar_cap_ratio = self.formulas.calculate_wind_solar_capacity_ratio(
                wind_cap, solar_cap, total_cap
            )
            coal_cap_ratio = self.formulas.calculate_coal_capacity_ratio(
                coal_cap, coal_ccs_cap, total_cap
            )
            
            results['capacity_structure']['非化石占比'].append(round(non_fossil_cap_ratio, 4))
            results['capacity_structure']['风光占比'].append(round(wind_solar_cap_ratio, 4))
            results['capacity_structure']['煤电占比'].append(round(coal_cap_ratio, 4))
            
            # ==================== 储能 ====================
            storage = self.power_data.storage
            pumped = self._get_value(storage, '抽蓄', i)
            electrochemical = self._get_value(storage, '电化学', i)
            total_storage = self.formulas.calculate_total_storage(pumped, electrochemical)
            storage_ratio = self.formulas.calculate_storage_ratio(total_storage, wind_cap, solar_cap)
            
            results['storage']['抽蓄'].append(round(pumped, 2))
            results['storage']['电化学'].append(round(electrochemical, 2))
            results['storage']['总装机'].append(round(total_storage, 2))
            results['storage']['储能/新能源'].append(round(storage_ratio, 4))
            
            # ==================== 发电量占比 ====================
            for gen_type in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                            '风电', '光伏', '生物质', '生物质+CCS', '其他']:
                gen_val = self._get_value(gen, gen_type, i)
                ratio = self.formulas.calculate_generation_ratio(gen_val, total_gen)
                results['generation_ratio'][gen_type].append(round(ratio, 4))
            
            wind_solar_gen_ratio = self.formulas.calculate_wind_solar_generation_ratio(
                wind_gen, solar_gen, total_gen
            )
            results['generation_ratio']['风光占比'].append(round(wind_solar_gen_ratio, 4))
            
            # 发电结构
            non_fossil_gen_ratio = self.formulas.calculate_non_fossil_generation_ratio(
                nuclear_gen, hydro_gen, wind_gen, solar_gen,
                biomass_gen, biomass_ccs_gen, other_gen, total_gen
            )
            coal_gen_ratio = self.formulas.calculate_coal_generation_ratio(
                coal_gen, coal_ccs_gen, total_gen
            )
            
            results['generation_structure']['非化石占比'].append(round(non_fossil_gen_ratio, 4))
            results['generation_structure']['风光占比'].append(round(wind_solar_gen_ratio, 4))
            results['generation_structure']['煤电占比'].append(round(coal_gen_ratio, 4))
            
            # ==================== 供需平衡 ====================
            h2_demand = self._get_list_value(self.power_data.hydrogen_demand, i)
            elec_demand = self._get_list_value(self.power_data.electricity_demand, i)
            total_demand = self.formulas.calculate_total_demand(h2_demand, elec_demand)
            trans_loss = self._get_list_value(self.power_data.transmission_loss, i)
            cross_region = self._get_list_value(self.power_data.cross_region_capacity, i)
            
            results['supply_demand']['电制氢'].append(round(h2_demand, 4))
            results['supply_demand']['电力需求'].append(round(elec_demand, 4))
            results['supply_demand']['总需求'].append(round(total_demand, 4))
            results['supply_demand']['传输损耗'].append(round(trans_loss, 4))
            results['supply_demand']['跨区传输'].append(round(cross_region, 4))
            
            # ==================== 碳捕集占比 ====================
            coal_ccs_ratio = self.formulas.calculate_ccs_ratio(coal_gen, coal_ccs_gen)
            coal_ccs_ratio_comp = self.formulas.calculate_ccs_ratio_complement(coal_gen, coal_ccs_gen)
            gas_ccs_ratio = self.formulas.calculate_ccs_ratio(gas_gen, gas_ccs_gen)
            gas_ccs_ratio_comp = self.formulas.calculate_ccs_ratio_complement(gas_gen, gas_ccs_gen)
            bio_ccs_ratio = self.formulas.calculate_ccs_ratio(biomass_gen, biomass_ccs_gen)
            bio_ccs_ratio_comp = self.formulas.calculate_ccs_ratio_complement(biomass_gen, biomass_ccs_gen)
            
            results['ccs_ratio']['煤电'].append(round(coal_ccs_ratio, 4))
            results['ccs_ratio']['煤电+CCS'].append(round(coal_ccs_ratio_comp, 4))
            results['ccs_ratio']['气电'].append(round(gas_ccs_ratio, 4))
            results['ccs_ratio']['气电+CCS'].append(round(gas_ccs_ratio_comp, 4))
            results['ccs_ratio']['生物质'].append(round(bio_ccs_ratio, 4))
            results['ccs_ratio']['生物质+CCS'].append(round(bio_ccs_ratio_comp, 4))
            
            # ==================== 成本计算 ====================
            self._calculate_costs(results, i, coal_cap, coal_ccs_cap, gas_cap, gas_ccs_cap,
                                 nuclear_cap, hydro_cap, wind_cap, solar_cap,
                                 biomass_cap, biomass_ccs_cap, pumped, electrochemical,
                                 coal_gen, coal_ccs_gen, gas_gen, gas_ccs_gen,
                                 nuclear_gen, hydro_gen, biomass_gen, biomass_ccs_gen,
                                 total_gen, cross_region)
        
        return results

    
    def _calculate_costs(self, results: dict, i: int,
                        coal_cap: float, coal_ccs_cap: float,
                        gas_cap: float, gas_ccs_cap: float,
                        nuclear_cap: float, hydro_cap: float,
                        wind_cap: float, solar_cap: float,
                        biomass_cap: float, biomass_ccs_cap: float,
                        pumped: float, electrochemical: float,
                        coal_gen: float, coal_ccs_gen: float,
                        gas_gen: float, gas_ccs_gen: float,
                        nuclear_gen: float, hydro_gen: float,
                        biomass_gen: float, biomass_ccs_gen: float,
                        total_gen: float, cross_region: float) -> None:
        """计算各类成本"""
        
        # 获取成本参数
        cap_cost = self.power_data.capacity_cost
        om_ratio = self.power_data.om_ratio
        fuel_cost = self.power_data.fuel_cost
        lifetime = self.power_data.equipment_lifetime
        
        offshore_ratio = self._get_list_value(self.power_data.offshore_wind_ratio, i)
        distributed_ratio = self._get_list_value(self.power_data.distributed_solar_ratio, i)
        
        # 计算年金系数
        def get_annuity(type_name: str) -> float:
            life = lifetime.get(type_name, 25)
            return self.formulas.calculate_annuity_factor(life)
        
        # ==================== 投资成本 ====================
        # 煤电
        coal_unit_cost = self._get_value(cap_cost, '煤电', i)
        coal_inv = self.formulas.calculate_investment_cost(
            coal_unit_cost, coal_cap, get_annuity('煤电')
        )
        results['investment']['煤电'].append(round(coal_inv, 2))
        
        # 煤电+CCS
        coal_ccs_unit_cost = self._get_value(cap_cost, '煤电+CCS', i)
        coal_ccs_inv = self.formulas.calculate_investment_cost(
            coal_ccs_unit_cost, coal_ccs_cap, get_annuity('煤电+CCS')
        )
        results['investment']['煤电+CCS'].append(round(coal_ccs_inv, 2))
        
        # 气电
        gas_unit_cost = self._get_value(cap_cost, '气电', i)
        gas_inv = self.formulas.calculate_investment_cost(
            gas_unit_cost, gas_cap, get_annuity('气电')
        )
        results['investment']['气电'].append(round(gas_inv, 2))
        
        # 气电+CCS
        gas_ccs_unit_cost = self._get_value(cap_cost, '气电+CCS', i)
        gas_ccs_inv = self.formulas.calculate_investment_cost(
            gas_ccs_unit_cost, gas_ccs_cap, get_annuity('气电+CCS')
        )
        results['investment']['气电+CCS'].append(round(gas_ccs_inv, 2))
        
        # 核电
        nuclear_unit_cost = self._get_value(cap_cost, '核电', i)
        nuclear_inv = self.formulas.calculate_investment_cost(
            nuclear_unit_cost, nuclear_cap, get_annuity('核电')
        )
        results['investment']['核电'].append(round(nuclear_inv, 2))
        
        # 水电
        hydro_unit_cost = self._get_value(cap_cost, '水电', i)
        hydro_inv = self.formulas.calculate_investment_cost(
            hydro_unit_cost, hydro_cap, get_annuity('水电')
        )
        results['investment']['水电'].append(round(hydro_inv, 2))
        
        # 风电(陆上)
        wind_onshore_unit_cost = self._get_value(cap_cost, '风电(陆上)', i)
        wind_onshore_inv = self.formulas.calculate_investment_cost_wind_onshore(
            wind_onshore_unit_cost, wind_cap, get_annuity('风电(陆上)'), offshore_ratio
        )
        results['investment']['风电(陆上)'].append(round(wind_onshore_inv, 2))
        
        # 风电(海上)
        wind_offshore_unit_cost = self._get_value(cap_cost, '风电(海上)', i)
        wind_offshore_inv = self.formulas.calculate_investment_cost_wind_offshore(
            wind_offshore_unit_cost, wind_cap, get_annuity('风电(海上)'), offshore_ratio
        )
        results['investment']['风电(海上)'].append(round(wind_offshore_inv, 2))
        
        # 光伏(集中)
        solar_central_unit_cost = self._get_value(cap_cost, '光伏(集中)', i)
        solar_central_inv = self.formulas.calculate_investment_cost_solar_centralized(
            solar_central_unit_cost, solar_cap, get_annuity('光伏(集中)'), distributed_ratio
        )
        results['investment']['光伏(集中)'].append(round(solar_central_inv, 2))
        
        # 光伏(分布式)
        solar_dist_unit_cost = self._get_value(cap_cost, '光伏(分布式)', i)
        solar_dist_inv = self.formulas.calculate_investment_cost_solar_distributed(
            solar_dist_unit_cost, solar_cap, get_annuity('光伏(分布式)'), distributed_ratio
        )
        results['investment']['光伏(分布式)'].append(round(solar_dist_inv, 2))
        
        # 生物质
        biomass_unit_cost = self._get_value(cap_cost, '生物质', i)
        biomass_inv = self.formulas.calculate_investment_cost(
            biomass_unit_cost, biomass_cap, get_annuity('生物质')
        )
        results['investment']['生物质'].append(round(biomass_inv, 2))
        
        # 生物质+CCS
        biomass_ccs_unit_cost = self._get_value(cap_cost, '生物质+CCS', i)
        biomass_ccs_inv = self.formulas.calculate_investment_cost(
            biomass_ccs_unit_cost, biomass_ccs_cap, get_annuity('生物质+CCS')
        )
        results['investment']['生物质+CCS'].append(round(biomass_ccs_inv, 2))
        
        # 抽蓄
        pumped_unit_cost = self._get_value(cap_cost, '抽蓄', i)
        pumped_inv = self.formulas.calculate_investment_cost(
            pumped_unit_cost, pumped, get_annuity('抽蓄')
        )
        results['investment']['抽蓄'].append(round(pumped_inv, 2))
        
        # 电化学
        elec_unit_cost = self._get_value(cap_cost, '电化学', i)
        elec_inv = self.formulas.calculate_investment_cost(
            elec_unit_cost, electrochemical, get_annuity('电化学')
        )
        results['investment']['电化学'].append(round(elec_inv, 2))
        
        # 总电源投资
        power_investments = [coal_inv, coal_ccs_inv, gas_inv, gas_ccs_inv,
                           nuclear_inv, hydro_inv, wind_onshore_inv, wind_offshore_inv,
                           solar_central_inv, solar_dist_inv, biomass_inv, biomass_ccs_inv]
        total_power_inv = self.formulas.calculate_total_power_investment(power_investments)
        results['investment']['总电源投资'].append(round(total_power_inv, 2))
        
        # 总储能投资
        total_storage_inv = self.formulas.calculate_total_storage_investment(pumped_inv, elec_inv)
        results['investment']['总储能投资'].append(round(total_storage_inv, 2))
        
        # 跨省电网投资
        grid_inv = self.formulas.calculate_grid_investment(cross_region)
        results['investment']['跨省电网'].append(round(grid_inv, 2))
        
        # 省内电网投资 (与总电源投资相同)
        results['investment']['省内电网'].append(round(total_power_inv, 2))
        
        # ==================== 运维成本 ====================
        # 煤电
        coal_om_ratio = self._get_value(om_ratio, '煤电', i)
        coal_om = self.formulas.calculate_om_cost(coal_unit_cost, coal_om_ratio, coal_cap)
        results['om_cost']['煤电'].append(round(coal_om, 2))
        
        # 煤电+CCS
        coal_ccs_om_ratio = self._get_value(om_ratio, '煤电+CCS', i)
        coal_ccs_om = self.formulas.calculate_om_cost(coal_ccs_unit_cost, coal_ccs_om_ratio, coal_ccs_cap)
        results['om_cost']['煤电+CCS'].append(round(coal_ccs_om, 2))
        
        # 气电
        gas_om_ratio = self._get_value(om_ratio, '气电', i)
        gas_om = self.formulas.calculate_om_cost(gas_unit_cost, gas_om_ratio, gas_cap)
        results['om_cost']['气电'].append(round(gas_om, 2))
        
        # 气电+CCS
        gas_ccs_om_ratio = self._get_value(om_ratio, '气电+CCS', i)
        gas_ccs_om = self.formulas.calculate_om_cost(gas_ccs_unit_cost, gas_ccs_om_ratio, gas_ccs_cap)
        results['om_cost']['气电+CCS'].append(round(gas_ccs_om, 2))
        
        # 核电
        nuclear_om_ratio = self._get_value(om_ratio, '核电', i)
        nuclear_om = self.formulas.calculate_om_cost(nuclear_unit_cost, nuclear_om_ratio, nuclear_cap)
        results['om_cost']['核电'].append(round(nuclear_om, 2))
        
        # 水电
        hydro_om_ratio = self._get_value(om_ratio, '水电', i)
        hydro_om = self.formulas.calculate_om_cost(hydro_unit_cost, hydro_om_ratio, hydro_cap)
        results['om_cost']['水电'].append(round(hydro_om, 2))
        
        # 风电(陆上)
        wind_onshore_om_ratio = self._get_value(om_ratio, '风电(陆上)', i)
        wind_onshore_om = self.formulas.calculate_om_cost_wind_onshore(
            wind_onshore_unit_cost, wind_onshore_om_ratio, wind_cap, offshore_ratio
        )
        results['om_cost']['风电(陆上)'].append(round(wind_onshore_om, 2))
        
        # 风电(海上)
        wind_offshore_om_ratio = self._get_value(om_ratio, '风电(海上)', i)
        wind_offshore_om = self.formulas.calculate_om_cost_wind_offshore(
            wind_offshore_unit_cost, wind_offshore_om_ratio, wind_cap, offshore_ratio
        )
        results['om_cost']['风电(海上)'].append(round(wind_offshore_om, 2))
        
        # 光伏(集中)
        solar_central_om_ratio = self._get_value(om_ratio, '光伏(集中)', i)
        solar_central_om = self.formulas.calculate_om_cost_solar_centralized(
            solar_central_unit_cost, solar_central_om_ratio, solar_cap, distributed_ratio
        )
        results['om_cost']['光伏(集中)'].append(round(solar_central_om, 2))
        
        # 光伏(分布式)
        solar_dist_om_ratio = self._get_value(om_ratio, '光伏(分布式)', i)
        solar_dist_om = self.formulas.calculate_om_cost_solar_distributed(
            solar_dist_unit_cost, solar_dist_om_ratio, solar_cap, distributed_ratio
        )
        results['om_cost']['光伏(分布式)'].append(round(solar_dist_om, 2))
        
        # 生物质
        biomass_om_ratio = self._get_value(om_ratio, '生物质', i)
        biomass_om = self.formulas.calculate_om_cost(biomass_unit_cost, biomass_om_ratio, biomass_cap)
        results['om_cost']['生物质'].append(round(biomass_om, 2))
        
        # 生物质+CCS
        biomass_ccs_om_ratio = self._get_value(om_ratio, '生物质+CCS', i)
        biomass_ccs_om = self.formulas.calculate_om_cost(biomass_ccs_unit_cost, biomass_ccs_om_ratio, biomass_ccs_cap)
        results['om_cost']['生物质+CCS'].append(round(biomass_ccs_om, 2))
        
        # 总运维成本
        om_costs = [coal_om, coal_ccs_om, gas_om, gas_ccs_om, nuclear_om, hydro_om,
                   wind_onshore_om, wind_offshore_om, solar_central_om, solar_dist_om,
                   biomass_om, biomass_ccs_om]
        total_om = self.formulas.calculate_total_om_cost(om_costs)
        results['om_cost']['总运维成本'].append(round(total_om, 2))
        
        # ==================== 燃料成本 ====================
        # 煤电
        coal_fuel_price = self._get_value(fuel_cost, '煤电', i)
        coal_fuel = self.formulas.calculate_fuel_cost(coal_fuel_price, coal_gen)
        results['fuel_cost_total']['煤电'].append(round(coal_fuel, 2))
        
        # 煤电+CCS
        coal_ccs_fuel_price = self._get_value(fuel_cost, '煤电+CCS', i)
        coal_ccs_fuel = self.formulas.calculate_fuel_cost(coal_ccs_fuel_price, coal_ccs_gen)
        results['fuel_cost_total']['煤电+CCS'].append(round(coal_ccs_fuel, 2))
        
        # 气电
        gas_fuel_price = self._get_value(fuel_cost, '气电', i)
        gas_fuel = self.formulas.calculate_fuel_cost(gas_fuel_price, gas_gen)
        results['fuel_cost_total']['气电'].append(round(gas_fuel, 2))
        
        # 气电+CCS
        gas_ccs_fuel_price = self._get_value(fuel_cost, '气电+CCS', i)
        gas_ccs_fuel = self.formulas.calculate_fuel_cost(gas_ccs_fuel_price, gas_ccs_gen)
        results['fuel_cost_total']['气电+CCS'].append(round(gas_ccs_fuel, 2))
        
        # 核电
        nuclear_fuel_price = self._get_value(fuel_cost, '核电', i)
        nuclear_fuel = self.formulas.calculate_fuel_cost(nuclear_fuel_price, nuclear_gen)
        results['fuel_cost_total']['核电'].append(round(nuclear_fuel, 2))
        
        # 水电
        hydro_fuel_price = self._get_value(fuel_cost, '水电', i)
        hydro_fuel = self.formulas.calculate_fuel_cost(hydro_fuel_price, hydro_gen)
        results['fuel_cost_total']['水电'].append(round(hydro_fuel, 2))
        
        # 生物质
        biomass_fuel_price = self._get_value(fuel_cost, '生物质', i)
        biomass_fuel = self.formulas.calculate_fuel_cost(biomass_fuel_price, biomass_gen)
        results['fuel_cost_total']['生物质'].append(round(biomass_fuel, 2))
        
        # 生物质+CCS
        biomass_ccs_fuel_price = self._get_value(fuel_cost, '生物质+CCS', i)
        biomass_ccs_fuel = self.formulas.calculate_fuel_cost(biomass_ccs_fuel_price, biomass_ccs_gen)
        results['fuel_cost_total']['生物质+CCS'].append(round(biomass_ccs_fuel, 2))
        
        # 总燃料成本
        fuel_costs = [coal_fuel, coal_ccs_fuel, gas_fuel, gas_ccs_fuel,
                     nuclear_fuel, hydro_fuel, biomass_fuel, biomass_ccs_fuel]
        total_fuel = self.formulas.calculate_total_fuel_cost(fuel_costs)
        results['fuel_cost_total']['总燃料成本'].append(round(total_fuel, 2))
        
        # ==================== 总成本和LCOE ====================
        intra_grid = total_power_inv  # 省内电网与电源投资相同
        total_cost = self.formulas.calculate_total_cost(
            total_power_inv, total_storage_inv, grid_inv, intra_grid, total_om, total_fuel
        )
        results['total_cost']['总成本'].append(round(total_cost, 2))
        
        # LCOE分量
        lcoe_power = self.formulas.calculate_lcoe_component(total_power_inv, total_gen)
        lcoe_storage = self.formulas.calculate_lcoe_component(total_storage_inv, total_gen)
        lcoe_grid_cross = self.formulas.calculate_lcoe_component(grid_inv, total_gen)
        lcoe_grid_intra = self.formulas.calculate_lcoe_component(intra_grid, total_gen)
        lcoe_om = self.formulas.calculate_lcoe_component(total_om, total_gen)
        lcoe_fuel = self.formulas.calculate_lcoe_component(total_fuel, total_gen)
        lcoe_total = lcoe_power + lcoe_storage + lcoe_grid_cross + lcoe_grid_intra + lcoe_om + lcoe_fuel
        
        results['lcoe']['电源投资'].append(round(lcoe_power, 4))
        results['lcoe']['储能投资'].append(round(lcoe_storage, 4))
        results['lcoe']['电网投资(跨省)'].append(round(lcoe_grid_cross, 4))
        results['lcoe']['电网投资(省内)'].append(round(lcoe_grid_intra, 4))
        results['lcoe']['运维成本'].append(round(lcoe_om, 4))
        results['lcoe']['燃料成本'].append(round(lcoe_fuel, 4))
        results['lcoe']['LCOE'].append(round(lcoe_total, 4))

    
    def export_to_csv(self, results: dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['项目'] + years
        
        # 装机容量
        rows.append(['电力装机数据(GW)'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电', '光伏', '生物质', '生物质+CCS', '其他', '总装机']:
            rows.append([key] + results['capacity'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 装机结构
        rows.append(['装机结构'] + [''] * len(years))
        for key in ['非化石占比', '风光占比', '煤电占比']:
            pct_values = [f"{v*100:.2f}%" for v in results['capacity_structure'][key]]
            rows.append([key] + pct_values)
        
        rows.append([''] * (len(years) + 1))
        
        # 储能
        rows.append(['储能配置(GW)'] + [''] * len(years))
        for key in ['抽蓄', '电化学', '总装机']:
            rows.append([key] + results['storage'][key])
        pct_values = [f"{v*100:.2f}%" for v in results['storage']['储能/新能源']]
        rows.append(['储能/新能源'] + pct_values)
        
        rows.append([''] * (len(years) + 1))
        
        # 发电量
        rows.append(['发电量数据(万亿kWh)'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电', '光伏', '生物质', '生物质+CCS', '其他', '总发电量']:
            rows.append([key] + results['generation'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 发电量占比
        rows.append(['发电量占比'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电', '光伏', '生物质', '生物质+CCS', '其他', '风光占比']:
            pct_values = [f"{v*100:.2f}%" for v in results['generation_ratio'][key]]
            rows.append([key] + pct_values)
        
        rows.append([''] * (len(years) + 1))
        
        # 发电结构
        rows.append(['发电结构'] + [''] * len(years))
        for key in ['非化石占比', '风光占比', '煤电占比']:
            pct_values = [f"{v*100:.2f}%" for v in results['generation_structure'][key]]
            rows.append([key] + pct_values)
        
        rows.append([''] * (len(years) + 1))
        
        # 供需平衡
        rows.append(['供需平衡(万亿kWh)'] + [''] * len(years))
        for key in ['电制氢', '电力需求', '总需求', '传输损耗', '跨区传输']:
            rows.append([key] + results['supply_demand'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 投资成本
        rows.append(['投资成本(亿元)'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电(陆上)', '风电(海上)', '光伏(集中)', '光伏(分布式)',
                   '生物质', '生物质+CCS', '抽蓄', '电化学',
                   '总电源投资', '总储能投资', '跨省电网', '省内电网']:
            rows.append([key] + results['investment'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 运维成本
        rows.append(['运维成本(亿元)'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电(陆上)', '风电(海上)', '光伏(集中)', '光伏(分布式)',
                   '生物质', '生物质+CCS', '总运维成本']:
            rows.append([key] + results['om_cost'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 燃料成本
        rows.append(['燃料成本(亿元)'] + [''] * len(years))
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '生物质', '生物质+CCS', '总燃料成本']:
            rows.append([key] + results['fuel_cost_total'][key])
        
        rows.append([''] * (len(years) + 1))
        
        # 总成本
        rows.append(['总成本(亿元)'] + results['total_cost']['总成本'])
        
        rows.append([''] * (len(years) + 1))
        
        # LCOE
        rows.append(['LCOE(元/kWh)'] + [''] * len(years))
        for key in ['电源投资', '储能投资', '电网投资(跨省)', '电网投资(省内)',
                   '运维成本', '燃料成本', 'LCOE']:
            rows.append([key] + results['lcoe'][key])
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"结果已导出到: {filepath}")
    
    def print_results(self, results: dict) -> None:
        """打印计算结果"""
        years = results['years']
        
        print("\n" + "=" * 120)
        print("电力结果计算")
        print("=" * 120)
        
        # 打印表头
        header = f"{'项目':<20}" + "".join([f"{y:>12}" for y in years])
        print(header)
        print("-" * 120)
        
        # 装机容量
        print("电力装机数据(GW)")
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电', '光伏', '生物质', '生物质+CCS', '其他', '总装机']:
            values = results['capacity'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.2f}" for v in values])
            print(row)
        
        print("-" * 120)
        
        # 装机结构
        print("装机结构")
        for key in ['非化石占比', '风光占比', '煤电占比']:
            values = results['capacity_structure'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.2%}" for v in values])
            print(row)
        
        print("-" * 120)
        
        # 储能
        print("储能配置(GW)")
        for key in ['抽蓄', '电化学', '总装机']:
            values = results['storage'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.2f}" for v in values])
            print(row)
        values = results['storage']['储能/新能源']
        row = f"  {'储能/新能源':<18}" + "".join([f"{v:>12.2%}" for v in values])
        print(row)
        
        print("-" * 120)
        
        # 发电量
        print("发电量数据(万亿kWh)")
        for key in ['煤电', '煤电+CCS', '气电', '气电+CCS', '核电', '水电',
                   '风电', '光伏', '生物质', '生物质+CCS', '其他', '总发电量']:
            values = results['generation'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 120)
        
        # 发电结构
        print("发电结构")
        for key in ['非化石占比', '风光占比', '煤电占比']:
            values = results['generation_structure'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.2%}" for v in values])
            print(row)
        
        print("-" * 120)
        
        # 供需平衡
        print("供需平衡(万亿kWh)")
        for key in ['电制氢', '电力需求', '总需求']:
            values = results['supply_demand'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("-" * 120)
        
        # 总成本
        values = results['total_cost']['总成本']
        row = f"{'总成本(亿元)':<20}" + "".join([f"{v:>12.2f}" for v in values])
        print(row)
        
        print("-" * 120)
        
        # LCOE
        print("LCOE(元/kWh)")
        for key in ['电源投资', '储能投资', '电网投资(跨省)', '电网投资(省内)',
                   '运维成本', '燃料成本', 'LCOE']:
            values = results['lcoe'][key]
            row = f"  {key:<18}" + "".join([f"{v:>12.4f}" for v in values])
            print(row)
        
        print("=" * 120)
