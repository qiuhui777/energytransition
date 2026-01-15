# -*- coding: utf-8 -*-
"""
运行情景数据一览表分析

该脚本用于汇总各模块的计算结果，生成情景数据一览表。
数据来源：
- 宏观测算参考 (macro_output.csv)
- 能源消费结构 (structure_output.csv)
- 碳排放轨迹 (trajectory_output.csv)
- 数据模板 (template_output.csv)

使用方法:
    python run_scenario_summary.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analysis.scenario_summary import ScenarioSummaryAnalyzer


def main():
    """主函数"""
    print("=" * 60)
    print("情景数据一览表分析")
    print("=" * 60)
    
    # 创建分析器
    analyzer = ScenarioSummaryAnalyzer()
    
    # 定义文件路径
    input_path = 'data/input/scenario_summary_input.csv'
    output_path = 'data/output/scenario_summary_output.csv'
    macro_path = 'data/output/macro_output.csv'
    structure_path = 'data/output/structure_output.csv'
    trajectory_path = 'data/output/trajectory_output.csv'
    template_path = 'data/output/template_output.csv'
    
    # 检查依赖文件
    print("\n检查依赖文件...")
    dependencies = [
        ('宏观测算参考', macro_path),
        ('能源消费结构', structure_path),
        ('碳排放轨迹', trajectory_path),
        ('数据模板', template_path),
    ]
    
    missing = []
    for name, path in dependencies:
        if os.path.exists(path):
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ✗ {name}: {path} (未找到)")
            missing.append(name)
    
    if missing:
        print(f"\n警告: 缺少以下依赖文件: {', '.join(missing)}")
        print("部分计算结果可能为0")
    
    # 运行分析
    print("\n开始计算...")
    results = analyzer.run(
        input_path=input_path,
        output_path=output_path,
        macro_path=macro_path,
        structure_path=structure_path,
        trajectory_path=trajectory_path,
        template_path=template_path
    )
    
    # 打印关键结果
    print("\n" + "=" * 60)
    print("关键结果摘要")
    print("=" * 60)
    
    years = results['years']
    print(f"\n年份: {years}")
    
    print("\n基础指标:")
    print(f"  人口 (亿人): {results['人口']}")
    print(f"  GDP年增长率 (%): {results['GDP年增长率']}")
    print(f"  GDP指数: {results['GDP指数']}")
    
    print("\n能源消费:")
    print(f"  能源消费量 (亿tce): {results['能源消费量']}")
    print(f"  煤炭占比 (%): {results['煤炭']}")
    print(f"  非化石占比 (%): {results['非化石']}")
    
    print("\nCO2排放:")
    print(f"  能源相关CO2排放量 (亿tCO2): {results['能源相关CO2排放量']}")
    print(f"  温室气体排放总量 (亿tCO2e): {results['温室气体排放总量']}")
    print(f"  温室气体净排放 (亿tCO2e): {results['温室气体净排放']}")
    
    print("\n强度指标:")
    print(f"  单位能耗CO2强度 (kgCO2/kgce): {results['单位能耗CO2强度']}")
    print(f"  人均温室气体排放量 (tCO2e/人): {results['人均温室气体排放量']}")
    
    print("\n" + "=" * 60)
    print(f"结果已保存到: {output_path}")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    main()
