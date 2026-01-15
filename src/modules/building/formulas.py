# -*- coding: utf-8 -*-
"""建筑结果公式定义"""

from ...base import BaseFormulas


class BuildingFormulas(BaseFormulas):
    """建筑结果计算公式"""
    
    def calculate_primary_consumption_total(self, coal: float, oil: float, 
                                            gas: float, biomass: float) -> float:
        """
        计算一次消费总量
        公式: 一次消费 = 煤炭 + 石油 + 天然气 + 生物质
        对应: B1 = SUM(B2:B5)
        """
        return self.calculate_sum([coal, oil, gas, biomass])
    
    def calculate_consumption_total(self, coal: float, oil: float, gas: float,
                                    electricity: float, hydrogen: float,
                                    biomass: float, heat: float) -> float:
        """
        计算消费总量
        公式: 消费总量 = SUM(煤 + 油 + 气 + 电 + 氢 + 生物质 + 热)
        对应: B14 = SUM(B15:B21)
        """
        return self.calculate_sum([coal, oil, gas, electricity, hydrogen, biomass, heat])
    
    def calculate_structure_ratio(self, value: float, total: float) -> float:
        """
        计算消费结构占比
        公式: 占比 = 单项 / 消费总量
        对应: B8 = B15/B14, B9 = B16/B14, etc.
        """
        if total == 0:
            return 0.0
        return value / total
    
    def calculate_other_ratio(self, coal_ratio: float, oil_ratio: float,
                              gas_ratio: float, electricity_ratio: float) -> float:
        """
        计算其他占比
        公式: 其他 = 1 - (煤 + 油 + 气 + 电)
        对应: B12 = 1 - SUM(B8:B11)
        """
        return 1 - self.calculate_sum([coal_ratio, oil_ratio, gas_ratio, electricity_ratio])
    
    def calculate_electricity_kwh(self, electricity_tce: float, 
                                   data_center_kwh: float = 0) -> float:
        """
        计算用电量(亿kWh)
        公式: 用电量 = 电(亿tce) / 1.229 + 数据中心用电量
        对应: B23 = B18/1.229 + B26
        
        Args:
            electricity_tce: 电的标煤值 (亿tce)
            data_center_kwh: 数据中心用电量 (亿kWh)
        """
        return self.calculate_electricity_quantity(electricity_tce) + data_center_kwh
    
    def calculate_building_area_total(self, urban_residential: float,
                                       rural_residential: float,
                                       public_building: float) -> float:
        """
        计算建筑面积总量
        公式: 总面积 = 城镇住宅 + 农村住宅 + 公共建筑
        """
        return self.calculate_sum([urban_residential, rural_residential, public_building])
    
    def calculate_per_capita_urban_residential(self, urban_residential: float, 
                                                urban_population: float) -> float:
        """
        计算城镇住宅人均建筑面积
        公式: 人均_城镇住宅 = 城镇住宅 / (城市人口 / 10^4)
        
        Args:
            urban_residential: 城镇住宅面积 (亿m2)
            urban_population: 城市人口 (万人)
        Returns:
            人均城镇住宅面积 (m2)
        """
        if urban_population == 0:
            return 0.0
        return urban_residential / (urban_population / 10000)
    
    def calculate_per_capita_rural_residential(self, rural_residential: float,
                                                rural_population: float) -> float:
        """
        计算农村住宅人均建筑面积
        公式: 人均_农村住宅 = 农村住宅 / (农村人口 / 10^4)
        
        Args:
            rural_residential: 农村住宅面积 (亿m2)
            rural_population: 农村人口 (万人)
        Returns:
            人均农村住宅面积 (m2)
        """
        if rural_population == 0:
            return 0.0
        return rural_residential / (rural_population / 10000)
    
    def calculate_per_capita_public_building(self, public_building: float,
                                              urban_population: float) -> float:
        """
        计算公共建筑人均建筑面积
        公式: 人均_公共建筑 = 公共建筑 / (城市人口 / 10^4)
        
        Args:
            public_building: 公共建筑面积 (亿m2)
            urban_population: 城市人口 (万人)
        Returns:
            人均公共建筑面积 (m2)
        """
        if urban_population == 0:
            return 0.0
        return public_building / (urban_population / 10000)
