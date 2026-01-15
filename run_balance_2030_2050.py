# -*- coding: utf-8 -*-
"""
2030年和2050年平衡模块运行脚本

该脚本用于运行2030年和2050年平衡分析模块，支持两种数据输入方式：
1. 从CSV文件直接读取输入数据
2. 从其他模块（template, structure, trajectory）的计算结果中提取数据

使用方法:
    python run_balance_2030_2050.py [--from-csv] [--from-modules]
    
    --from-csv: 从CSV文件读取输入数据
    --from-modules: 从其他模块结果提取数据（需要先运行其他模块）
"""

import argparse
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analysis.balance_2030_2050 import BalanceAnalyzer, BalanceVariables, BalanceFormulas


def run_from_csv(input_path: str, output_path: str):
    """从CSV文件运行分析"""
    print(f"从CSV文件加载数据: {input_path}")
    
    analyzer = BalanceAnalyzer()
    analyzer.load_input_from_csv(input_path)
    
    print("执行计算...")
    results = analyzer.calculate()
    
    print(f"导出结果到: {output_path}")
    analyzer.export_to_csv(results, output_path)
    
    print("计算完成!")
    return results


def run_from_modules(output_path: str):
    """从其他模块结果运行分析"""
    print("从其他模块加载数据...")
    
    # 导入其他分析模块
    from src.analysis.template import TemplateAnalyzer
    from src.analysis.structure import StructureAnalyzer
    from src.analysis.trajectory import TrajectoryAnalyzer
    
    # 运行数据模板分析
    print("  - 加载数据模板结果...")
    template_analyzer = TemplateAnalyzer()
    template_input = 'data/input/template_input.csv'
    if os.path.exists(template_input):
        template_analyzer.load_input_from_csv(template_input)
        template_results = template_analyzer.calculate()
    else:
        print(f"    警告: 未找到 {template_input}")
        template_results = {}
    
    # 运行能源消费结构分析
    print("  - 加载能源消费结构结果...")
    structure_analyzer = StructureAnalyzer()
    structure_input = 'data/input/structure_input.csv'
    if os.path.exists(structure_input):
        structure_analyzer.load_input_from_csv(structure_input)
        structure_results = structure_analyzer.calculate()
    else:
        print(f"    警告: 未找到 {structure_input}")
        structure_results = {}
    
    # 运行碳排放轨迹分析
    print("  - 加载碳排放轨迹结果...")
    trajectory_analyzer = TrajectoryAnalyzer()
    trajectory_input = 'data/input/trajectory_input.csv'
    if os.path.exists(trajectory_input):
        trajectory_analyzer.load_input_from_csv(trajectory_input)
        trajectory_results = trajectory_analyzer.calculate()
    else:
        print(f"    警告: 未找到 {trajectory_input}")
        trajectory_results = {}
    
    # 创建平衡分析器并加载模块结果
    print("创建平衡分析器...")
    analyzer = BalanceAnalyzer()
    analyzer.load_module_results('template', template_results)
    analyzer.load_module_results('structure', structure_results)
    analyzer.load_module_results('trajectory', trajectory_results)
    analyzer.load_from_modules()
    
    print("执行计算...")
    results = analyzer.calculate()
    
    print(f"导出结果到: {output_path}")
    analyzer.export_to_csv(results, output_path)
    
    print("计算完成!")
    return results


def print_results_summary(results: dict):
    """打印结果摘要"""
    print("\n" + "=" * 60)
    print("2030年和2050年平衡计算结果摘要")
    print("=" * 60)
    
    for year in results.get('years', []):
        year_data = results.get('balance_data', {}).get(year, {})
        if not year_data:
            continue
        
        print(f"\n【{year}年】")
        
        # 终端部门总计
        terminal_total = year_data.get('terminal_sectors', {}).get('总计', {})
        print(f"  终端能源消费总计: {terminal_total.get('终端能源消费', 0):.2f} 亿tce")
        print(f"  终端CO2直接排放: {terminal_total.get('CO2直接排放', 0):.2f} 亿吨")
        
        # 一次能源消费
        primary = year_data.get('summary', {}).get('一次能源消费', {})
        print(f"  一次能源消费总计: {primary.get('小计', 0):.2f} 亿tce")
        
        # 一次能源结构
        structure = year_data.get('summary', {}).get('一次能源结构', {})
        print(f"  一次能源结构:")
        print(f"    - 煤炭: {structure.get('煤炭', 0)*100:.1f}%")
        print(f"    - 石油: {structure.get('石油', 0)*100:.1f}%")
        print(f"    - 天然气: {structure.get('天然气', 0)*100:.1f}%")
        print(f"    - 非化石能源: {structure.get('非化石能源', 0)*100:.1f}%")
        
        # 碳排放汇总
        summary = year_data.get('summary', {})
        print(f"  能源相关CO2: {summary.get('能源相关CO2', 0):.2f} 亿吨")
        print(f"  温室气体排放: {summary.get('温室气体排放', 0):.2f} 亿吨")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='2030年和2050年平衡分析模块'
    )
    parser.add_argument(
        '--from-csv', 
        action='store_true',
        help='从CSV文件读取输入数据'
    )
    parser.add_argument(
        '--from-modules',
        action='store_true', 
        help='从其他模块结果提取数据'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/input/balance_2030_2050_input.csv',
        help='输入CSV文件路径'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/output/balance_2030_2050_output.csv',
        help='输出CSV文件路径'
    )
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    if args.from_csv:
        results = run_from_csv(args.input, args.output)
    elif args.from_modules:
        results = run_from_modules(args.output)
    else:
        # 默认从CSV运行
        print("未指定数据源，默认从CSV文件读取...")
        results = run_from_csv(args.input, args.output)
    
    # 打印结果摘要
    print_results_summary(results)


if __name__ == '__main__':
    main()
