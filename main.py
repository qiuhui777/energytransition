#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源计算系统 - 主入口
支持模块: 能源平衡表、工业、交通、建筑、电力
分析模块: 宏观测算参考
"""

import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import ConfigLoader
from src.modules import (BalanceCalculator, IndustryCalculator, 
                         TransportCalculator, BuildingCalculator, PowerCalculator)
from src.analysis import MacroAnalyzer, TemplateAnalyzer, StructureAnalyzer


# 模块计算器映射
CALCULATORS = {
    # 'balance': BalanceCalculator,
    # 'industry': IndustryCalculator,
    # 'transport': TransportCalculator,
    'building': BuildingCalculator,
    'power': PowerCalculator,
}


def run_module(module_name: str, module_config: dict) -> dict:
    """运行指定模块的计算"""
    if module_name not in CALCULATORS:
        print(f"模块 {module_name} 尚未实现")
        return {}
    
    calculator_class = CALCULATORS[module_name]
    calculator = calculator_class()
    
    input_type = module_config.get('input_type', 'csv')
    
    if input_type == 'json':
        input_file = module_config.get('input_json_file')
    else:
        input_file = module_config.get('input_csv_file')
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 - {input_file}")
        return {}
    
    print(f"从{input_type.upper()}文件加载数据: {input_file}")
    
    if input_type == 'json':
        calculator.load_from_json(input_file)
    else:
        calculator.load_from_csv(input_file)
    
    results = calculator.calculate()
    calculator.print_results(results)
    
    output_file = module_config.get('output_csv_file')
    calculator.export_to_csv(results, output_file)
    
    return results


def run_macro_analysis(config: dict, module_results: dict = None) -> dict:
    """运行宏观测算参考分析"""
    macro_config = config.get('analysis', {}).get('macro', {})
    
    if not macro_config.get('enabled', False):
        return {}
    
    print(f"\n{'='*70}")
    print("运行分析模块: 宏观测算参考")
    print("=" * 70)
    
    analyzer = MacroAnalyzer()
    
    # 加载输入数据
    input_file = macro_config.get('input_csv_file')
    if input_file and os.path.exists(input_file):
        print(f"从CSV文件加载输入数据: {input_file}")
        analyzer.load_input_from_csv(input_file)
    
    # 加载部门数据
    use_module_results = macro_config.get('use_module_results', False)
    
    if use_module_results and module_results:
        # 从模块计算结果加载部门数据
        print("从模块计算结果加载部门数据...")
        for module_name, results in module_results.items():
            analyzer.load_module_results(module_name, results)
        analyzer.load_sector_data_from_modules()
    else:
        # 从CSV文件加载部门数据
        sector_file = macro_config.get('sector_data_csv_file')
        if sector_file and os.path.exists(sector_file):
            print(f"从CSV文件加载部门数据: {sector_file}")
            analyzer.load_sector_data_from_csv(sector_file)
    
    # 执行计算
    results = analyzer.calculate()
    
    # 打印结果
    analyzer.print_results(results)
    
    # 导出结果
    output_file = macro_config.get('output_csv_file')
    if output_file:
        analyzer.export_to_csv(results, output_file)
    
    return results


def run_template_analysis(config: dict, module_results: dict = None) -> dict:
    """运行数据模板分析"""
    template_config = config.get('analysis', {}).get('template', {})
    
    if not template_config.get('enabled', False):
        return {}
    
    print(f"\n{'='*70}")
    print("运行分析模块: 数据模板")
    print("=" * 70)
    
    analyzer = TemplateAnalyzer()
    
    # 加载数据
    use_module_results = template_config.get('use_module_results', False)
    
    if use_module_results and module_results:
        # 从模块计算结果加载数据
        print("从模块计算结果加载数据...")
        for module_name, results in module_results.items():
            analyzer.load_module_results(module_name, results)
        analyzer.load_from_modules()
    else:
        # 从CSV文件加载数据
        input_file = template_config.get('input_csv_file')
        if input_file and os.path.exists(input_file):
            print(f"从CSV文件加载数据: {input_file}")
            analyzer.load_input_from_csv(input_file)
    
    # 执行计算
    results = analyzer.calculate()
    
    # 打印结果
    analyzer.print_results(results)
    
    # 导出结果
    output_file = template_config.get('output_csv_file')
    if output_file:
        analyzer.export_to_csv(results, output_file)
    
    return results


def run_structure_analysis(config: dict, module_results: dict = None) -> dict:
    """运行能源结构分析"""
    structure_config = config.get('analysis', {}).get('structure', {})
    
    if not structure_config.get('enabled', False):
        return {}
    
    print(f"\n{'='*70}")
    print("运行分析模块: 能源结构")
    print("=" * 70)
    
    analyzer = StructureAnalyzer()
    
    # 加载数据
    use_module_results = structure_config.get('use_module_results', False)
    
    if use_module_results and module_results:
        # 从模块计算结果加载数据
        print("从模块计算结果加载数据...")
        for module_name, results in module_results.items():
            analyzer.load_module_results(module_name, results)
        analyzer.load_from_modules()
    else:
        # 从CSV文件加载数据
        input_file = structure_config.get('input_csv_file')
        if input_file and os.path.exists(input_file):
            print(f"从CSV文件加载数据: {input_file}")
            analyzer.load_input_from_csv(input_file)
    
    # 执行计算
    results = analyzer.calculate()
    
    # 打印结果
    analyzer.print_results(results)
    
    # 导出结果
    output_file = structure_config.get('output_csv_file')
    if output_file:
        analyzer.export_to_csv(results, output_file)
    
    return results


def main():
    """主函数"""
    print("=" * 70)
    print("能源计算系统")
    print("=" * 70)
    
    # 加载配置
    config_loader = ConfigLoader('config/config.json')
    config = config_loader.load()
    
    # 获取启用的模块
    enabled_modules = config_loader.get_enabled_modules()
    
    if not enabled_modules:
        print("没有启用的计算模块，请检查配置文件")
    else:
        print(f"启用的模块: {', '.join(enabled_modules)}")
    
    # 存储模块计算结果
    module_results = {}
    
    # 运行各模块
    for module_name in enabled_modules:
        print(f"\n{'='*70}")
        print(f"运行模块: {module_name}")
        print("=" * 70)
        
        module_config = config_loader.get_module_config(module_name)
        results = run_module(module_name, module_config)
        if results:
            module_results[module_name] = results
    
    # 运行宏观测算参考分析
    run_macro_analysis(config, module_results)
    
    # 运行数据模板分析
    run_template_analysis(config, module_results)
    
    # 运行能源结构分析
    run_structure_analysis(config, module_results)
    
    print("\n" + "=" * 70)
    print("所有计算完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
