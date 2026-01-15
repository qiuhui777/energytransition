#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计表格运行脚本

从其他模块的输出数据读取，进行汇总分析，生成统计报表
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analysis.statistics import StatisticsAnalyzer


def main():
    """主函数"""
    print("=" * 60)
    print("统计表格分析")
    print("=" * 60)
    
    # 创建分析器
    analyzer = StatisticsAnalyzer()
    
    # 从CSV文件加载数据
    print("\n正在加载数据...")
    analyzer.load_from_csv('data/output')
    
    # 执行计算
    print("正在计算...")
    results = analyzer.calculate()
    
    # 打印结果
    analyzer.print_results()
    
    # 导出结果
    output_path = 'data/output/statistics_output.csv'
    analyzer.export_to_csv(output_path)
    
    print("\n" + "=" * 60)
    print("统计表格分析完成！")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    main()
