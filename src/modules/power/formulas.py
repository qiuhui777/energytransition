# -*- coding: utf-8 -*-
"""电力结果公式定义"""

from ...base import BaseFormulas


class PowerFormulas(BaseFormulas):
    """电力结果计算公式"""
    
    def __init__(self):
        super().__init__()
        self.discount_rate = 0.06  # 折现率 6%
    
    # ==================== 装机容量计算 ====================
    
    def calculate_capacity_from_generation(self, generation: float, 
                                           utilization_hours: float) -> float:
        """
        根据发电量和利用小时数计算装机容量
        公式: 装机容量(GW) = IF(利用小时数>0, 发电量(万亿kWh)/利用小时数*1000000, 0)
        对应: D2 = IF(D56>0, D23/D56*1000000, 0)
        """
        if utilization_hours <= 0:
            return 0.0
        return generation / utilization_hours * 1000000
    
    def calculate_total_capacity(self, capacities: list) -> float:
        """
        计算总装机容量
        公式: 总装机 = SUM(各类型装机)
        对应: D13 = SUM(D2:D11)
        """
        return self.calculate_sum(capacities)
    
    def calculate_non_fossil_capacity_ratio(self, nuclear: float, hydro: float,
                                            wind: float, solar: float,
                                            biomass: float, biomass_ccs: float,
                                            other: float, total: float) -> float:
        """
        计算非化石装机容量占比
        公式: 非化石占比 = SUM(核电+水电+风电+光伏+生物质+生物质CCS+其他) / 总装机
        对应: D14 = SUM(D6:D12)/D13
        """
        if total == 0:
            return 0.0
        non_fossil = self.calculate_sum([nuclear, hydro, wind, solar, 
                                         biomass, biomass_ccs, other])
        return non_fossil / total
    
    def calculate_wind_solar_capacity_ratio(self, wind: float, solar: float, 
                                            total: float) -> float:
        """
        计算风光装机占比
        公式: 风光占比 = (风电 + 光伏) / 总装机
        对应: D15 = (D8+D9)/D13
        """
        if total == 0:
            return 0.0
        return (wind + solar) / total
    
    def calculate_coal_capacity_ratio(self, coal: float, coal_ccs: float, 
                                      total: float) -> float:
        """
        计算煤电装机占比
        公式: 煤电占比 = (煤电 + 煤电CCS) / 总装机
        对应: D16 = (D2+D3)/D13
        """
        if total == 0:
            return 0.0
        return (coal + coal_ccs) / total
    
    def calculate_storage_ratio(self, total_storage: float, wind: float, 
                                solar: float) -> float:
        """
        计算储能/新能源比例
        公式: 储能/新能源 = 总储能 / (风电 + 光伏)
        对应: D17 = D20/SUM(D8:D9)
        """
        wind_solar = wind + solar
        if wind_solar == 0:
            return 0.0
        return total_storage / wind_solar
    
    def calculate_total_storage(self, pumped: float, electrochemical: float) -> float:
        """
        计算总储能装机
        公式: 总储能 = 抽蓄 + 电化学
        对应: D20 = SUM(D18:D19)
        """
        return pumped + electrochemical
    
    # ==================== 发电量计算 ====================
    
    def calculate_total_generation(self, generations: list) -> float:
        """
        计算总发电量
        公式: 总发电量 = SUM(各类型发电量)
        对应: D34 = SUM(D23:D33)
        """
        return self.calculate_sum(generations)
    
    def calculate_transmission_loss_ratio(self, total_generation: float,
                                          error_rate: float,
                                          total_demand: float) -> float:
        """
        计算传输损耗比例
        公式: 传输损耗 = (总发电量/(1+误差) - 总需求) / 总需求
        对应: D36 = (D34/(1+D35)-D70)/D70
        """
        if total_demand == 0:
            return 0.0
        adjusted_generation = total_generation / (1 + error_rate)
        return (adjusted_generation - total_demand) / total_demand
    
    def calculate_cross_region_ratio(self, cross_region: float, 
                                     total_generation: float) -> float:
        """
        计算跨区传输/总发电量比例
        公式: 传输/负荷 = 跨区传输容量 / 总发电量
        对应: D38 = D37/D34
        """
        if total_generation == 0:
            return 0.0
        return cross_region / total_generation
    
    def calculate_non_fossil_generation_ratio(self, nuclear: float, hydro: float,
                                              wind: float, solar: float,
                                              biomass: float, biomass_ccs: float,
                                              other: float, total: float) -> float:
        """
        计算非化石发电量占比
        公式: 非化石占比 = SUM(核电+水电+风电+光伏+生物质+生物质CCS+其他) / 总发电量
        对应: D39 = SUM(D27:D33)/D34
        """
        if total == 0:
            return 0.0
        non_fossil = self.calculate_sum([nuclear, hydro, wind, solar, 
                                         biomass, biomass_ccs, other])
        return non_fossil / total
    
    def calculate_wind_solar_generation_ratio(self, wind: float, solar: float, 
                                              total: float) -> float:
        """
        计算风光发电占比
        公式: 风光占比 = (风电 + 光伏) / 总发电量
        对应: D40 = (D29+D30)/D34
        """
        if total == 0:
            return 0.0
        return (wind + solar) / total
    
    def calculate_coal_generation_ratio(self, coal: float, coal_ccs: float, 
                                        total: float) -> float:
        """
        计算煤电发电占比
        公式: 煤电占比 = (煤电 + 煤电CCS) / 总发电量
        对应: D41 = (D23+D24)/D34
        """
        if total == 0:
            return 0.0
        return (coal + coal_ccs) / total
    
    def calculate_generation_ratio(self, generation: float, total: float) -> float:
        """
        计算单项发电量占比
        公式: 占比 = 单项发电量 / 总发电量
        对应: D43 = D23/D$34
        """
        if total == 0:
            return 0.0
        return generation / total
    
    # ==================== 碳捕集占比计算 ====================
    
    def calculate_ccs_ratio(self, without_ccs: float, with_ccs: float) -> float:
        """
        计算碳捕集占比（无CCS部分）
        公式: 无CCS占比 = 无CCS发电量 / (无CCS + 有CCS)
        对应: D73 = D23/(D23+D24)
        """
        total = without_ccs + with_ccs
        if total == 0:
            return 0.0
        return without_ccs / total
    
    def calculate_ccs_ratio_complement(self, without_ccs: float, with_ccs: float) -> float:
        """
        计算碳捕集占比（有CCS部分）
        公式: 有CCS占比 = 1 - 无CCS占比
        对应: D74 = 1-D73
        """
        return 1 - self.calculate_ccs_ratio(without_ccs, with_ccs)
    
    # ==================== 能源消耗计算 ====================
    
    def calculate_coal_consumption(self, coal_gen: float, coal_rate: float,
                                   coal_ccs_gen: float, coal_ccs_rate: float) -> float:
        """
        计算煤炭消耗
        公式: 煤炭消耗 = 煤电发电量*煤炭消耗率 + 煤电CCS发电量*煤炭CCS消耗率
        对应: D81 = D23*D98 + D24*D99
        """
        return coal_gen * coal_rate + coal_ccs_gen * coal_ccs_rate
    
    def calculate_gas_consumption(self, gas_gen: float, gas_rate: float,
                                  gas_ccs_gen: float, gas_ccs_rate: float,
                                  conversion_factor: float = 1.33) -> float:
        """
        计算天然气消耗
        公式: 天然气消耗 = (气电发电量*天然气消耗率 + 气电CCS发电量*天然气CCS消耗率) * 转换系数
        对应: D83 = (D25*D100+D26*D101)*$O$83
        """
        return (gas_gen * gas_rate + gas_ccs_gen * gas_ccs_rate) * conversion_factor
    
    def calculate_renewable_consumption(self, generation: float, rate: float) -> float:
        """
        计算可再生能源消耗（风能、太阳能、水能、核能）
        公式: 消耗 = 发电量 * 消耗率
        对应: D86 = D29*D98 (风能), D87 = D30*D98 (太阳能), etc.
        """
        return generation * rate
    
    def calculate_biomass_consumption(self, biomass_gen: float, biomass_rate: float,
                                      biomass_ccs_gen: float, biomass_ccs_rate: float) -> float:
        """
        计算生物质能消耗
        公式: 生物质消耗 = 生物质发电量*生物质消耗率 + 生物质CCS发电量*生物质CCS消耗率
        对应: D90 = D31*D102+D32*D103
        """
        return biomass_gen * biomass_rate + biomass_ccs_gen * biomass_ccs_rate
    
    def calculate_total_non_fossil(self, wind: float, solar: float, hydro: float,
                                   nuclear: float, biomass: float) -> float:
        """
        计算其它非化石能源总量
        公式: 非化石总量 = SUM(风能+太阳能+水能+核能+生物质能)
        对应: D84 = SUM(D86:D90)
        """
        return self.calculate_sum([wind, solar, hydro, nuclear, biomass])
    
    # ==================== 燃料消耗率计算 ====================
    
    def calculate_ccs_fuel_rate(self, base_rate: float, ccs_factor: float) -> float:
        """
        计算CCS燃料消耗率
        公式: CCS消耗率 = 基础消耗率 / CCS改造系数
        对应: D99 = D98/D93
        """
        if ccs_factor == 0:
            return 0.0
        return base_rate / ccs_factor
    
    def calculate_fuel_rate_decay(self, base_rate: float, decay_factor: float, 
                                  years: int) -> float:
        """
        计算燃料消耗率衰减
        公式: 衰减后消耗率 = 基础消耗率 * (衰减系数^年数)
        对应: E98 = D98*(O98^5)
        """
        return base_rate * (decay_factor ** years)
    
    # ==================== CO2排放计算 ====================
    
    def calculate_coal_co2(self, coal_consumption: float, co2_factor: float) -> float:
        """
        计算煤炭CO2排放
        公式: 煤炭CO2 = 煤炭消耗 * CO2排放系数
        对应: D109 = D81*宏观测算参考!G29
        """
        return coal_consumption * co2_factor
    
    def calculate_gas_co2(self, gas_consumption: float, co2_factor: float) -> float:
        """
        计算天然气CO2排放
        公式: 天然气CO2 = 天然气消耗 * CO2排放系数
        对应: D110 = D83*宏观测算参考!G31
        """
        return gas_consumption * co2_factor
    
    def calculate_total_direct_co2(self, coal_co2: float, gas_co2: float) -> float:
        """
        计算总直接CO2排放
        公式: 总直接排放 = 煤炭CO2 + 天然气CO2
        对应: D111 = SUM(D109:D110)
        """
        return coal_co2 + gas_co2
    
    def calculate_fossil_ccs_capture(self, coal_ccs_rate: float, coal_ccs_gen: float,
                                     coal_co2_factor: float, gas_ccs_rate: float,
                                     gas_ccs_gen: float, gas_co2_factor: float,
                                     gas_conversion: float, capture_rate: float) -> float:
        """
        计算化石能源CCS捕集量
        公式: 化石CCS = (煤电CCS消耗率*煤电CCS发电量*煤炭CO2系数 + 
                        天然气转换系数*气电CCS消耗率*气电CCS发电量*天然气CO2系数) * 捕集率
        对应: D112 = (D99*D24*G29+$O83*D101*D26*G31)*D105
        """
        coal_capture = coal_ccs_rate * coal_ccs_gen * coal_co2_factor
        gas_capture = gas_conversion * gas_ccs_rate * gas_ccs_gen * gas_co2_factor
        return (coal_capture + gas_capture) * capture_rate
    
    def calculate_biomass_ccs_capture(self, biomass_ccs_rate: float, 
                                      biomass_ccs_gen: float,
                                      biomass_co2_factor: float,
                                      capture_rate: float) -> float:
        """
        计算生物质CCS捕集量
        公式: 生物质CCS = 生物质CCS消耗率 * 生物质CCS发电量 * 生物质CO2系数 * 捕集率
        对应: D113 = D103*D32*1.74*D105
        """
        return biomass_ccs_rate * biomass_ccs_gen * biomass_co2_factor * capture_rate
    
    def calculate_net_co2(self, total_direct: float, fossil_ccs: float, 
                          biomass_ccs: float) -> float:
        """
        计算净CO2排放
        公式: 净排放 = 总直接排放 - 化石CCS - 生物质CCS
        对应: D114 = D111-D112-D113
        """
        return total_direct - fossil_ccs - biomass_ccs

    
    # ==================== 成本计算 ====================
    
    def calculate_annuity_factor(self, lifetime: int, rate: float = 0.06) -> float:
        """
        计算年金系数
        公式: 年金系数 = (1-rate) / (1-rate^lifetime)
        对应: (1-0.94)/(1-0.94^N117)
        """
        if lifetime <= 0:
            return 0.0
        factor = 1 - rate
        return factor / (1 - factor ** lifetime)
    
    def calculate_investment_cost(self, unit_cost: float, capacity: float,
                                  annuity_factor: float) -> float:
        """
        计算投资成本
        公式: 投资成本 = 单位成本 * 年金系数 * 装机容量 / 10
        对应: D174 = D117*(1-0.94)/(1-0.94^N117)*D2/10
        """
        return unit_cost * annuity_factor * capacity / 10
    
    def calculate_investment_cost_wind_onshore(self, unit_cost: float, capacity: float,
                                               annuity_factor: float, 
                                               offshore_ratio: float) -> float:
        """
        计算陆上风电投资成本
        公式: 陆上风电投资 = 单位成本 * 年金系数 * (1-海上占比) * 风电装机 / 10
        对应: D180 = D123*(1-0.94)/(1-0.94^N123)*(1-D171)*D8/10
        """
        return unit_cost * annuity_factor * (1 - offshore_ratio) * capacity / 10
    
    def calculate_investment_cost_wind_offshore(self, unit_cost: float, capacity: float,
                                                annuity_factor: float,
                                                offshore_ratio: float) -> float:
        """
        计算海上风电投资成本
        公式: 海上风电投资 = 单位成本 * 年金系数 * 海上占比 * 风电装机 / 10
        对应: D181 = D124*(1-0.94)/(1-0.94^N124)*D171*D8/10
        """
        return unit_cost * annuity_factor * offshore_ratio * capacity / 10
    
    def calculate_investment_cost_solar_centralized(self, unit_cost: float, capacity: float,
                                                    annuity_factor: float,
                                                    distributed_ratio: float) -> float:
        """
        计算集中式光伏投资成本
        公式: 集中式光伏投资 = 单位成本 * 年金系数 * (1-分布式占比) * 光伏装机 / 10
        对应: D182 = D125*(1-0.94)/(1-0.94^N125)*(1-D172)*D9/10
        """
        return unit_cost * annuity_factor * (1 - distributed_ratio) * capacity / 10
    
    def calculate_investment_cost_solar_distributed(self, unit_cost: float, capacity: float,
                                                    annuity_factor: float,
                                                    distributed_ratio: float) -> float:
        """
        计算分布式光伏投资成本
        公式: 分布式光伏投资 = 单位成本 * 年金系数 * 分布式占比 * 光伏装机 / 10
        对应: D183 = D126*(1-0.94)/(1-0.94^N126)*D172*D9/10
        """
        return unit_cost * annuity_factor * distributed_ratio * capacity / 10
    
    def calculate_om_cost(self, unit_cost: float, om_ratio: float, capacity: float) -> float:
        """
        计算运维成本
        公式: 运维成本 = 单位成本 * 运维比例 * 装机容量 / 10
        对应: D189 = D117*D132*D2/10
        """
        return unit_cost * om_ratio * capacity / 10
    
    def calculate_om_cost_wind_onshore(self, unit_cost: float, om_ratio: float,
                                       capacity: float, offshore_ratio: float) -> float:
        """
        计算陆上风电运维成本
        公式: 陆上风电运维 = 单位成本 * 运维比例 * (1-海上占比) * 风电装机 / 10
        对应: D195 = D123*D138*(1-D171)*D8/10
        """
        return unit_cost * om_ratio * (1 - offshore_ratio) * capacity / 10
    
    def calculate_om_cost_wind_offshore(self, unit_cost: float, om_ratio: float,
                                        capacity: float, offshore_ratio: float) -> float:
        """
        计算海上风电运维成本
        公式: 海上风电运维 = 单位成本 * 运维比例 * 海上占比 * 风电装机 / 10
        对应: D196 = D124*D139*D171*D9/10
        """
        return unit_cost * om_ratio * offshore_ratio * capacity / 10
    
    def calculate_om_cost_solar_centralized(self, unit_cost: float, om_ratio: float,
                                            capacity: float, distributed_ratio: float) -> float:
        """
        计算集中式光伏运维成本
        公式: 集中式光伏运维 = 单位成本 * 运维比例 * (1-分布式占比) * 光伏装机 / 10
        对应: D197 = D125*D140*(1-D172)*D9/10
        """
        return unit_cost * om_ratio * (1 - distributed_ratio) * capacity / 10
    
    def calculate_om_cost_solar_distributed(self, unit_cost: float, om_ratio: float,
                                            capacity: float, distributed_ratio: float) -> float:
        """
        计算分布式光伏运维成本
        公式: 分布式光伏运维 = 单位成本 * 运维比例 * 分布式占比 * 光伏装机 / 10
        对应: D198 = D126*D141*D172*D9/10
        """
        return unit_cost * om_ratio * distributed_ratio * capacity / 10
    
    def calculate_fuel_cost(self, fuel_price: float, generation: float) -> float:
        """
        计算燃料成本
        公式: 燃料成本 = 燃料单价 * 发电量 * 10000
        对应: D202 = D145*D23*10000
        """
        return fuel_price * generation * 10000
    
    def calculate_total_power_investment(self, investments: list) -> float:
        """
        计算总电源投资
        公式: 总电源投资 = SUM(各类型投资)
        对应: D215 = SUM(D174:D185)
        """
        return self.calculate_sum(investments)
    
    def calculate_total_storage_investment(self, pumped: float, 
                                           electrochemical: float) -> float:
        """
        计算总储能投资
        公式: 总储能投资 = 抽蓄投资 + 电化学投资
        对应: D216 = SUM(D186:D187)
        """
        return pumped + electrochemical
    
    def calculate_grid_investment(self, cross_region: float, factor: float = 0.06) -> float:
        """
        计算跨省电网投资
        公式: 跨省电网投资 = 跨区传输容量 * 0.06 * 10000
        对应: D217 = D37*0.06*10000
        """
        return cross_region * factor * 10000
    
    def calculate_total_om_cost(self, om_costs: list) -> float:
        """
        计算总运维成本
        公式: 总运维成本 = SUM(各类型运维成本)
        对应: D219 = SUM(D189:D200)
        """
        return self.calculate_sum(om_costs)
    
    def calculate_total_fuel_cost(self, fuel_costs: list) -> float:
        """
        计算总燃料成本
        公式: 总燃料成本 = SUM(各类型燃料成本)
        对应: D220 = SUM(D202:D213)
        """
        return self.calculate_sum(fuel_costs)
    
    def calculate_total_cost(self, power_inv: float, storage_inv: float,
                             grid_inv: float, intra_grid: float,
                             om_cost: float, fuel_cost: float) -> float:
        """
        计算总成本
        公式: 总成本 = 电源投资 + 储能投资 + 跨省电网 + 省内电网 + 运维成本 + 燃料成本
        对应: D221 = SUM(D215:D220)
        """
        return self.calculate_sum([power_inv, storage_inv, grid_inv, 
                                   intra_grid, om_cost, fuel_cost])
    
    def calculate_lcoe_component(self, cost: float, total_generation: float) -> float:
        """
        计算LCOE分量（元/kWh）
        公式: LCOE分量 = 成本 / 总发电量 / 10000
        对应: D224 = D215/D$34/10000
        """
        if total_generation == 0:
            return 0.0
        return cost / total_generation / 10000
    
    def calculate_lcoe_index(self, lcoe: float, base_lcoe: float) -> float:
        """
        计算LCOE指数（相对于基准年）
        公式: LCOE指数 = 当年LCOE / 基准年LCOE
        对应: D231 = D230/$D230
        """
        if base_lcoe == 0:
            return 0.0
        return lcoe / base_lcoe
    
    # ==================== 供需平衡计算 ====================
    
    def calculate_total_demand(self, hydrogen_demand: float, 
                               electricity_demand: float) -> float:
        """
        计算总需求
        公式: 总需求 = 电制氢 + 电力需求
        对应: D70 = D68 + D69
        """
        return hydrogen_demand + electricity_demand
    
    # ==================== LCOE计算 ====================
    
    def calculate_lcoe(self, unit_cost: float, om_ratio: float, fuel_price: float,
                       utilization_hours: float, lifetime: int, 
                       rate: float = 0.06) -> float:
        """
        计算平准化度电成本(LCOE)
        公式: LCOE = (单位成本*(1-rate)/(1-rate^寿命)*10 + 单位成本*运维比例*10) / 利用小时数 + 燃料单价
        对应: D158 = (D117*(1-0.94)/(1-0.94^N117)*10+D117*D132*10)/C158+D145
        """
        if utilization_hours == 0:
            return 0.0
        annuity_factor = self.calculate_annuity_factor(lifetime, rate)
        capital_cost = unit_cost * annuity_factor * 10
        om_cost = unit_cost * om_ratio * 10
        return (capital_cost + om_cost) / utilization_hours + fuel_price
    
    def calculate_fuel_price_decay(self, base_price: float, target_price: float,
                                   decay_factor: float, years: int) -> float:
        """
        计算燃料价格衰减
        公式: 衰减后价格 = 基础价格 + (目标价格 - 基础价格) * 衰减系数^年数
        对应: E146 = D145+(D146-D145)*0.97^5
        """
        return base_price + (target_price - base_price) * (decay_factor ** years)
