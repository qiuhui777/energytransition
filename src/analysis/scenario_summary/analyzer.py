# -*- coding: utf-8 -*-
"""情景数据一览表分析器

汇总各模块计算结果，生成情景数据一览表
"""

import os
import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .variables import ScenarioSummaryVariables
from .formulas import ScenarioSummaryFormulas


@dataclass
class ModuleData:
    """模块数据结构"""
    macro: Dict[str, List[float]] = field(default_factory=dict)
    structure: Dict[str, List[float]] = field(default_factory=dict)
    trajectory: Dict[str, List[float]] = field(default_factory=dict)
    template: Dict[str, List[float]] = field(default_factory=dict)


class ScenarioSummaryAnalyzer:
    """情景数据一览表分析器"""
    
    def __init__(self):
        self.variables = ScenarioSummaryVariables()
        self.formulas = ScenarioSummaryFormulas()
        self.years: List[str] = []
        self.module_data = ModuleData()
        self.results: Dict[str, List[float]] = {}
    
    def load_module_outputs(
        self,
        macro_path: str = 'data/output/macro_output.csv',
        structure_path: str = 'data/output/structure_output.csv',
        trajectory_path: str = 'data/output/trajectory_output.csv',
        template_path: str = 'data/output/template_output.csv'
    ) -> None:
        """加载各模块的输出数据"""
        if os.path.exists(macro_path):
            self._load_macro_data(macro_path)
        if os.path.exists(structure_path):
            self._load_structure_data(structure_path)
        if os.path.exists(trajectory_path):
            self._load_trajectory_data(trajectory_path)
        if os.path.exists(template_path):
            self._load_template_data(template_path)

    def _load_macro_data(self, filepath: str) -> None:
        """加载宏观测算参考数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['项目', '类别', '单位', '部门']]
        self.years = year_cols
        
        for _, row in df.iterrows():
            item = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            if item:
                values = [self._safe_float(row[y]) for y in year_cols]
                self.module_data.macro[item] = values
    
    def _load_structure_data(self, filepath: str) -> None:
        """加载能源消费结构数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['类别', '项目', '单位', '部门']]
        if not self.years:
            self.years = year_cols
        
        current_category = ''
        for _, row in df.iterrows():
            category = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            item = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ''
            
            if category:
                current_category = category
            
            key = f"{current_category}_{item}" if item else current_category
            if key:
                values = [self._safe_float(row[y]) for y in year_cols]
                self.module_data.structure[key] = values
    
    def _load_trajectory_data(self, filepath: str) -> None:
        """加载碳排放轨迹数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['部门', '项目', '单位', '类别']]
        if not self.years:
            self.years = year_cols
        
        current_section = ''
        for _, row in df.iterrows():
            section = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            item = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ''
            
            if section:
                current_section = section
            
            key = f"{current_section}_{item}" if item else current_section
            if key:
                values = [self._safe_float(row[y]) for y in year_cols]
                self.module_data.trajectory[key] = values

    def _load_template_data(self, filepath: str) -> None:
        """加载数据模板数据"""
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['部门', '类别', '项目', '单位']]
        if not self.years:
            self.years = year_cols
        
        current_section = ''
        current_subsection = ''
        for _, row in df.iterrows():
            section = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            subsection = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ''
            item = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ''
            
            if section:
                current_section = section
            if subsection:
                current_subsection = subsection
            
            key = f"{current_section}_{current_subsection}_{item}" if item else f"{current_section}_{current_subsection}"
            if key:
                values = [self._safe_float(row[y]) for y in year_cols]
                self.module_data.template[key] = values
    
    def load_input_from_csv(self, filepath: str) -> None:
        """从CSV文件加载输入数据（用于直接输入人口等数据）"""
        df = pd.read_csv(filepath, encoding='utf-8')
        year_cols = [c for c in df.columns if c not in ['项目', '单位']]
        if not self.years:
            self.years = year_cols
        
        for _, row in df.iterrows():
            item = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            if item:
                values = [self._safe_float(row[y]) for y in year_cols]
                self.results[item] = values
    
    @staticmethod
    def _safe_float(value) -> float:
        """安全转换为浮点数"""
        if value is None or pd.isna(value) or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_value(self, data_dict: Dict, key: str, index: int, default: float = 0.0) -> float:
        """安全获取字典中列表的值"""
        if key in data_dict and index < len(data_dict[key]):
            return data_dict[key][index]
        return default
    
    def _get_list(self, data_dict: Dict, key: str, default: List[float] = None) -> List[float]:
        """安全获取字典中的列表"""
        if default is None:
            default = [0.0] * len(self.years)
        return data_dict.get(key, default)

    def calculate(self) -> Dict[str, Any]:
        """执行情景数据一览表计算"""
        num_years = len(self.years)
        
        # 初始化结果
        results = {
            'years': self.years,
            '人口': self.results.get('人口', [0.0] * num_years),
            'GDP年增长率': [], 'GDP指数': [], '能源消费量': [],
            '煤炭': [], '石油': [], '天然气': [], '非化石': [],
            '能源相关CO2排放量': [], '工业部门直接CO2排放': [], '建筑部门直接CO2排放': [],
            '交通部门直接CO2排放': [], '电力部分直接CO2排放-无CCS': [], '其它部门': [],
            '甲烷': [], '氧化亚氮': [], 'F-Gas': [], '工业过程排放': [],
            '温室气体排放总量': [], '碳捕集埋存量': [], '碳汇量': [], '温室气体净排放': [],
            '单位能耗CO2强度': [], '人均温室气体排放量': [],
            '能源消费年增长率': [], 'CO2排放年增长率': [],
            '单位GDP能耗强度年下降率': [], '单位GDPCO2强度年下降率': [],
            '单位能耗CO2强度年下降率': [], '5年GDP能源强度下降幅度': [],
            '5年GDPCO2强度下降幅度': [], '能源消费弹性': [],
        }
        
        # 从宏观数据获取GDP相关数据
        gdp_growth_rate = self._get_list(self.module_data.macro, 'GDP年增长率')
        gdp_index = self._get_list(self.module_data.macro, 'GDP指数')
        
        # 从能源消费结构获取数据
        energy_consumption = self._get_list(self.module_data.structure, '一次能源_总能源消费')
        if all(v == 0 for v in energy_consumption):
            energy_consumption = self._get_list(self.module_data.macro, '能源消费量')
        
        coal_ratio = self._get_list(self.module_data.structure, '能源结构占比_煤炭')
        oil_ratio = self._get_list(self.module_data.structure, '能源结构占比_石油')
        gas_ratio = self._get_list(self.module_data.structure, '能源结构占比_天然气')
        non_fossil_ratio = self._get_list(self.module_data.structure, '能源结构占比_非化石能源')
        
        # 从碳排放轨迹获取数据
        industry_co2 = self._get_list(self.module_data.trajectory, '汇总_工业直接排放')
        building_co2 = self._get_list(self.module_data.trajectory, '汇总_建筑排放')
        transport_co2 = self._get_list(self.module_data.trajectory, '汇总_交通排放')
        power_co2 = self._get_list(self.module_data.trajectory, '汇总_电力直接排放')
        other_co2 = self._get_list(self.module_data.trajectory, '汇总_其他排放')
        industrial_process = self._get_list(self.module_data.trajectory, '工业部门_工业过程CO2')
        ccs_amount = self._get_list(self.module_data.trajectory, '汇总_电力CCS')
        carbon_sink = self._get_list(self.module_data.trajectory, '碳汇量')
        
        # 从数据模板获取非CO2数据
        methane = self._get_list(self.module_data.template, '非CO2_CH4')
        n2o = self._get_list(self.module_data.template, '非CO2_N2O')
        f_gas = self._get_list(self.module_data.template, '非CO2_F-gases')

        for i in range(num_years):
            # GDP相关
            results['GDP年增长率'].append(round(gdp_growth_rate[i] * 100 if gdp_growth_rate[i] < 1 else gdp_growth_rate[i], 4))
            results['GDP指数'].append(round(gdp_index[i], 4))
            
            # 能源消费
            results['能源消费量'].append(round(energy_consumption[i], 4))
            results['煤炭'].append(round(coal_ratio[i] * 100 if coal_ratio[i] < 1 else coal_ratio[i], 4))
            results['石油'].append(round(oil_ratio[i] * 100 if oil_ratio[i] < 1 else oil_ratio[i], 4))
            results['天然气'].append(round(gas_ratio[i] * 100 if gas_ratio[i] < 1 else gas_ratio[i], 4))
            results['非化石'].append(round(non_fossil_ratio[i] * 100 if non_fossil_ratio[i] < 1 else non_fossil_ratio[i], 4))
            
            # CO2排放
            ind_co2, bld_co2, trn_co2 = industry_co2[i], building_co2[i], transport_co2[i]
            pwr_co2, oth_co2 = power_co2[i], other_co2[i]
            
            results['工业部门直接CO2排放'].append(round(ind_co2, 4))
            results['建筑部门直接CO2排放'].append(round(bld_co2, 4))
            results['交通部门直接CO2排放'].append(round(trn_co2, 4))
            results['电力部分直接CO2排放-无CCS'].append(round(pwr_co2, 4))
            results['其它部门'].append(round(oth_co2, 4))
            
            energy_co2 = self.formulas.calculate_energy_co2_emission(ind_co2, bld_co2, trn_co2, pwr_co2, oth_co2, 0)
            results['能源相关CO2排放量'].append(round(energy_co2, 4))
            
            # 非CO2温室气体
            ch4, n2o_val, f_gas_val = methane[i], n2o[i], f_gas[i]
            ind_process = industrial_process[i]
            
            results['甲烷'].append(round(ch4, 4))
            results['氧化亚氮'].append(round(n2o_val, 4))
            results['F-Gas'].append(round(f_gas_val, 4))
            results['工业过程排放'].append(round(ind_process, 4))
            
            total_ghg = self.formulas.calculate_total_ghg_emission(
                ind_co2, bld_co2, trn_co2, pwr_co2, oth_co2, ch4, n2o_val, f_gas_val, ind_process, 0)
            results['温室气体排放总量'].append(round(total_ghg, 4))
            
            ccs, sink = abs(ccs_amount[i]), carbon_sink[i]
            results['碳捕集埋存量'].append(round(ccs, 4))
            results['碳汇量'].append(round(sink, 4))
            
            net_ghg = self.formulas.calculate_net_ghg_emission(total_ghg, ccs, sink)
            results['温室气体净排放'].append(round(net_ghg, 4))
            
            co2_intensity = self.formulas.calculate_co2_intensity_per_energy(energy_co2, energy_consumption[i])
            results['单位能耗CO2强度'].append(round(co2_intensity, 4))
            
            population = results['人口'][i] if i < len(results['人口']) else 14.0
            ghg_per_capita = self.formulas.calculate_ghg_per_capita(total_ghg, population)
            results['人均温室气体排放量'].append(round(ghg_per_capita, 4))

        # 计算增长率和下降率
        for i in range(num_years):
            if i == 0:
                results['能源消费年增长率'].append(0.0)
                results['CO2排放年增长率'].append(0.0)
                results['单位GDP能耗强度年下降率'].append(0.0)
                results['单位GDPCO2强度年下降率'].append(0.0)
                results['单位能耗CO2强度年下降率'].append(0.0)
                results['5年GDP能源强度下降幅度'].append(0.0)
                results['5年GDPCO2强度下降幅度'].append(0.0)
                results['能源消费弹性'].append(0.0)
            else:
                energy_growth = self.formulas.calculate_energy_growth_rate(energy_consumption[i], energy_consumption[i-1])
                results['能源消费年增长率'].append(round(energy_growth, 4))
                
                co2_growth = self.formulas.calculate_co2_growth_rate(results['能源相关CO2排放量'][i], results['能源相关CO2排放量'][i-1])
                results['CO2排放年增长率'].append(round(co2_growth, 4))
                
                gdp_energy_decline = self.formulas.calculate_gdp_energy_intensity_decline(
                    energy_consumption[i], energy_consumption[i-1], gdp_index[i], gdp_index[i-1])
                results['单位GDP能耗强度年下降率'].append(round(gdp_energy_decline, 4))
                
                gdp_co2_decline = self.formulas.calculate_gdp_co2_intensity_decline(
                    results['能源相关CO2排放量'][i], results['能源相关CO2排放量'][i-1], gdp_index[i], gdp_index[i-1])
                results['单位GDPCO2强度年下降率'].append(round(gdp_co2_decline, 4))
                
                energy_co2_decline = self.formulas.calculate_energy_co2_intensity_decline(
                    results['能源相关CO2排放量'][i], results['能源相关CO2排放量'][i-1], energy_consumption[i], energy_consumption[i-1])
                results['单位能耗CO2强度年下降率'].append(round(energy_co2_decline, 4))
                
                gdp_energy_5y = self.formulas.calculate_gdp_energy_intensity_5y_decline(
                    energy_consumption[i], energy_consumption[i-1], gdp_index[i], gdp_index[i-1])
                results['5年GDP能源强度下降幅度'].append(round(gdp_energy_5y, 4))
                
                gdp_co2_5y = self.formulas.calculate_gdp_co2_intensity_5y_decline(
                    results['能源相关CO2排放量'][i], results['能源相关CO2排放量'][i-1], gdp_index[i], gdp_index[i-1])
                results['5年GDPCO2强度下降幅度'].append(round(gdp_co2_5y, 4))
                
                elasticity = self.formulas.calculate_energy_elasticity(energy_growth, results['GDP年增长率'][i])
                results['能源消费弹性'].append(round(elasticity, 4))
        
        return results

    def export_to_csv(self, results: Dict, filepath: str) -> None:
        """将计算结果导出为CSV"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
        
        years = results['years']
        rows = []
        headers = ['项目', '单位'] + years
        
        output_items = [
            ('人口', '亿人'), ('GDP年增长率', '%'), ('GDP指数', '2005=1'),
            ('能源消费量', '亿tce'), ('煤炭', '%'), ('石油', '%'), ('天然气', '%'), ('非化石', '%'),
            ('能源相关CO2排放量', '亿tCO2'), ('工业部门直接CO2排放', '亿tCO2'),
            ('建筑部门直接CO2排放', '亿tCO2'), ('交通部门直接CO2排放', '亿tCO2'),
            ('电力部分直接CO2排放-无CCS', '亿tCO2'), ('其它部门', '亿tCO2'),
            ('甲烷', '亿tCO2e'), ('氧化亚氮', '亿tCO2e'), ('F-Gas', '亿tCO2e'),
            ('工业过程排放', '亿tCO2e'), ('温室气体排放总量', '亿tCO2e'),
            ('碳捕集埋存量', '亿tCO2e'), ('碳汇量', '亿tCO2e'), ('温室气体净排放', '亿tCO2e'),
            ('单位能耗CO2强度', 'kgCO2/kgce'), ('人均温室气体排放量', 'tCO2e/人'),
            ('能源消费年增长率', '%'), ('CO2排放年增长率', '%'),
            ('单位GDP能耗强度年下降率', '%'), ('单位GDPCO2强度年下降率', '%'),
            ('单位能耗CO2强度年下降率', '%'), ('5年GDP能源强度下降幅度', '%'),
            ('5年GDPCO2强度下降幅度', '%'), ('能源消费弹性', ''),
        ]
        
        for item, unit in output_items:
            if item in results:
                values = results[item]
                row = [item, unit] + [f"{v:.4f}" if isinstance(v, float) else str(v) for v in values]
                rows.append(row)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"情景数据一览表已导出到: {filepath}")
    
    def run(
        self,
        input_path: Optional[str] = None,
        output_path: str = 'data/output/scenario_summary_output.csv',
        macro_path: str = 'data/output/macro_output.csv',
        structure_path: str = 'data/output/structure_output.csv',
        trajectory_path: str = 'data/output/trajectory_output.csv',
        template_path: str = 'data/output/template_output.csv'
    ) -> Dict[str, Any]:
        """运行情景数据一览表分析"""
        self.load_module_outputs(macro_path, structure_path, trajectory_path, template_path)
        
        if input_path and os.path.exists(input_path):
            self.load_input_from_csv(input_path)
        
        results = self.calculate()
        self.export_to_csv(results, output_path)
        
        return results


def main():
    """主函数"""
    analyzer = ScenarioSummaryAnalyzer()
    results = analyzer.run()
    
    print("\n=== 情景数据一览表计算完成 ===")
    print(f"年份: {results['years']}")
    print(f"能源消费量: {results['能源消费量']}")
    print(f"能源相关CO2排放量: {results['能源相关CO2排放量']}")
    print(f"温室气体排放总量: {results['温室气体排放总量']}")


if __name__ == '__main__':
    main()
