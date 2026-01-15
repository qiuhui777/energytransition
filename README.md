目录结构：

config/ - 配置文件，控制启用哪些模块及输入输出路径
data/input/ - 输入数据
data/output/ - 输出结果
src/base/ - 基类（calculator、formulas、variables）
src/modules/ - 各计算模块（balance已实现，industry/transport/building/power待实现）
src/utils/ - 工具类（配置加载、IO处理）
main.py - 主入口
扩展新模块只需：

在 src/modules/ 下创建模块目录，实现 variables.py、formulas.py、calculator.py
在 main.py 的 CALCULATORS 字典中注册
在 config/config.json 中配置



==========================================================================================
# 工业结果计算模块 (src/modules/industry/)：

variables.py - 定义变量：

一次消费能源类型：煤炭、石油、天然气、生物质
消费结构类型：煤、油、气、电、其他
消费总量类型：煤、油、气、电、氢、生物质、热
formulas.py - 定义公式：

一次消费合计 = 煤炭 + 石油 + 天然气 + 生物质
消费总量合计 = SUM(煤+油+气+电+氢+生物质+热)
消费结构占比 = 单项 / 消费总量
其他占比 = 1 - (煤+油+气+电)
氢 = 氢调整 + 氢原始
用电量(亿kWh) = 电(亿tce) / 1.229
calculator.py - 计算器实现，支持CSV/JSON输入，自动计算并输出结果

输入文件格式见 data/input/industry_input.csv，配置文件中已启用该模块。

==========================================================================================
# 交通结果计算模块 (src/modules/transport/)：

variables.py - 定义变量：

一次消费能源类型：煤炭、石油、天然气、生物质
消费结构类型：煤、油、气、电、其他
消费总量类型：煤、油、气、电、氢、生物质、热
碳排放运输类型：道路运输、民航运输、铁路运输、水路运输
formulas.py - 定义公式：

一次消费合计 = 煤炭 + 石油 + 天然气 + 生物质
消费总量合计 = SUM(煤+油+气+电+氢+生物质+热)
消费结构占比 = 单项 / 消费总量
其他占比 = 1 - (煤+油+气+电)
用电量(亿kWh) = 电(亿tce) / 1.229
碳排放合计 = 道路 + 民航 + 铁路 + 水路
calculator.py - 计算器实现，支持CSV/JSON输入，输出包含消费结构百分比和碳排放数据

汽车保有量（亿辆）：燃油车、天然气汽车、电动车、燃料电池汽车
货运周转量（亿吨公里）：铁路、道路、水路、民航（使用 货运_ 前缀区分）
客运周转量（亿人公里）：铁路、道路、水路、民航（使用 客运_ 前缀区分）
输入CSV文件格式已更新，输出结果包含所有新增数据。

==========================================================================================
# 建筑结果计算模块 (src/modules/building/)：

variables.py - 定义变量：

一次消费能源类型：煤炭、石油、天然气、生物质
消费结构类型：煤、油、气、电、其他
消费总量类型：煤、油、气、电、氢、生物质、热
建筑面积类型：城镇住宅、农村住宅、公共建筑
人均建筑面积类型：城镇住宅、农村住宅、公共建筑
人口类型：城市人口、农村人口

formulas.py - 定义公式：

一次消费合计 = 煤炭 + 石油 + 天然气 + 生物质
消费总量合计 = SUM(煤+油+气+电+氢+生物质+热)
消费结构占比 = 单项 / 消费总量
其他占比 = 1 - (煤+油+气+电)
用电量(亿kWh) = 电(亿tce) / 1.229 + 数据中心用电量
建筑面积合计 = 城镇住宅 + 农村住宅 + 公共建筑

calculator.py - 计算器实现，支持CSV/JSON输入，输出包含建筑面积、人均面积、人口等数据#

==========================================================================================
# 电力结果计算模块的开发，包括：

变量定义 (src/modules/power/variables.py)：定义了所有电力相关变量，包括装机类型、发电量类型、利用小时数、成本参数、设备寿命等。

公式定义 (src/modules/power/formulas.py)：实现了所有计算公式，包括：

装机容量计算（从发电量和利用小时数反推）
装机结构占比（非化石、风光、煤电占比）
发电量占比计算
储能配置计算
碳捕集占比计算
投资成本、运维成本、燃料成本计算
LCOE（平准化度电成本）计算
计算器 (src/modules/power/calculator.py)：实现了完整的计算流程，支持CSV数据输入和输出。

输入数据 (data/input/power_input.csv)：创建了示例输入数据文件，包含2020-2060年的电力系统数据。

配置更新：更新了config/config.json和main.py以支持电力模块。

模块输出包括：装机容量、装机结构、储能配置、发电量、发电结构、供需平衡、投资成本、运维成本、燃料成本、总成本和LCOE等完整的电力系统计算结果。

==========================================================================================
# 宏观测算参考模块：

src/analysis/macro/analyzer.py - 添加了 export_to_csv() 和 print_results() 方法
data/input/macro_input.csv - 宏观参数输入文件（GDP增长率、能源强度下降幅度、排放因子等）
data/input/macro_sector_data.csv - 部门能源消费数据（煤炭/石油/天然气/非化石按部门分类）
config/config.json - 添加了 analysis.macro 配置节
main.py - 集成了 run_macro_analysis() 函数
src/__init__.py - 导出分析模块
模块支持两种数据加载方式：

从CSV文件加载部门数据（当前配置）
从其他模块计算结果加载（设置 use_module_results: true）
输出结果包含：宏观指标、能源结构、CO2指标、GDP强度指标、CO2下降指标，以及按部门分类的煤炭/石油/天然气/非化石能源消费数据。

==========================================================================================
# 数据模板模块：

创建了 src/analysis/template/ 目录结构：

__init__.py - 模块导出
variables.py - 变量定义（工业/建筑/交通/电力部门能源消费、CO2排放、氢能、生物质等）
formulas.py - 计算公式（CO2排放计算、电力净排放、氢能转换等）
analyzer.py - 分析器（数据加载、计算、导出）
功能特点：

支持从CSV文件加载各部门数据
支持从其他模块计算结果加载（设置 use_module_results: true）
计算各部门终端能源消费（煤炭/石油/天然气/电力/氢能/非化石能源）
计算各部门直接和间接CO2排放
计算电力部门能源消耗和CO2排放（含CCS）
计算氢能供给（灰氢/蓝氢/绿氢）和需求
计算生物质消费汇总
输出CSV和控制台打印
文件：

data/input/template_input.csv - 输入数据
data/output/template_output.csv - 输出结果
config/config.json - 添加了template配置
main.py - 集成了 run_template_analysis() 函数


==========================================================================================
# 能源结构模块

完成了 src/analysis/structure/analyzer.py - 添加了 calculate()、export_to_csv() 和 print_results() 方法
更新了 src/analysis/__init__.py - 导出 StructureAnalyzer、StructureVariables、StructureFormulas
更新了 main.py - 添加了 run_structure_analysis() 函数并在主流程中调用
更新了 config/config.json - 添加了 structure 分析配置
创建了 data/input/structure_input.csv - 示例输入数据
能源结构模块计算内容包括：

终端消费（工业/建筑/交通/其他部门）
电气化率（各部门及终端总体）
氢能消费及占比
一次能源（煤/油/气/非化石）及结构占比
终端能源结构
生物质汇总

==========================================================================================
# 碳排放轨迹模块

variables.py - 定义碳排放轨迹相关变量（部门类型、排放变量、CCS变量、排放因子等）

formulas.py - 定义计算公式：

工业/建筑/交通/电力部门排放计算
总排放（含/不含间接排放）计算
CCS汇总计算
能源相关CO2、温室气体排放、净排放计算
中和分析计算
analyzer.py - 分析器类：

支持从CSV文件加载输入数据
支持从其他模块结果加载数据（load_module_results）
执行完整的碳排放轨迹计算
导出结果到CSV
打印结果摘要
data/input/trajectory_input.csv - 示例输入数据文件

使用方式：

from src.analysis.trajectory import TrajectoryAnalyzer

analyzer = TrajectoryAnalyzer()
analyzer.load_input_from_csv('data/input/trajectory_input.csv')
results = analyzer.calculate()
analyzer.export_to_csv(results, 'data/output/trajectory_output.csv')
该模块与现有的 template、structure、macro 模块保持一致的代码风格，可以独立运行，也可以通过 load_module_results() 方法接收其他模块的计算结果进行再分析。

==========================================================================================
# 2030年和2050年平衡模块

src/analysis/balance_2030_2050/
├── __init__.py           # 模块初始化
├── variables.py          # 变量定义
├── formulas.py           # 计算公式
└── analyzer.py           # 分析器主类

data/input/
├── balance_2030_2050_input.csv    # 输入数据模板
└── balance_2030_2050_sample.csv   # 示例数据

run_balance_2030_2050.py          # 独立运行脚本
主要功能：

变量定义 (variables.py)：定义了目标年份、终端部门、能源类型、CO2排放因子等变量

计算公式 (formulas.py)：实现了Excel中的计算公式，包括：

电热当量转换：电热当量 = 电量 × 1.229
CO2排放计算：CO2 = 煤炭×2.66 + 石油×1.73 + 天然气×1.56
一次能源消费汇总
终端消费结构计算
温室气体排放计算
分析器 (analyzer.py)：支持两种数据输入方式：

从CSV文件直接读取
从其他模块（template, structure, trajectory）结果提取
运行脚本 (run_balance_2030_2050.py)：提供命令行接口，支持：

--from-csv：从CSV文件读取
--from-modules：从其他模块结果提取
--input/--output：指定输入输出路径
该模块与现有的analysis模块结构保持一致，可以独立运行，也可以与其他模块集成使用。

==========================================================================================
# 情景数据一览表模块

src/scenario_summary/
├── __init__.py           # 模块初始化
├── variables.py          # 变量定义
├── formulas.py           # 计算公式
└── analyzer.py           # 分析器主类

data/input/
└── scenario_summary_input.csv    # 输入数据（人口等直接输入数据）

data/output/
└── scenario_summary_output.csv   # 输出结果

run_scenario_summary.py           # 独立运行脚本

## 主要功能

该模块用于汇总各分析模块的计算结果，生成情景数据一览表。

### 数据来源
- 宏观测算参考 (macro_output.csv) - GDP年增长率、GDP指数
- 能源消费结构 (structure_output.csv) - 能源消费量、能源结构占比
- 碳排放轨迹 (trajectory_output.csv) - 各部门CO2排放、CCS、碳汇
- 数据模板 (template_output.csv) - 非CO2温室气体（甲烷、氧化亚氮、F-Gas）

### 变量定义 (variables.py)
定义了情景数据一览表中的所有变量：
- 基础指标：人口、GDP年增长率、GDP指数
- 能源消费：能源消费量、煤炭/石油/天然气/非化石占比
- CO2排放：能源相关CO2排放量、各部门直接CO2排放
- 非CO2温室气体：甲烷、氧化亚氮、F-Gas、工业过程排放
- 温室气体汇总：排放总量、碳捕集埋存量、碳汇量、净排放
- 强度指标：单位能耗CO2强度、人均温室气体排放量
- 增长率指标：能源消费年增长率、CO2排放年增长率、各类强度下降率
- 弹性系数：能源消费弹性

### 计算公式 (formulas.py)
实现了Excel中的计算公式：
- 能源相关CO2排放量 = SUM(工业+建筑+交通+电力+其它) + 其他排放
- 温室气体排放总量 = SUM(CO2排放 + 非CO2温室气体)
- 单位能耗CO2强度 = 能源相关CO2排放量 / 能源消费量
- 人均温室气体排放量 = 温室气体排放总量 / 人口
- 能源消费年增长率 = (当期/上期 - 1) / 5 × 100
- 单位GDP能耗强度年下降率 = (1 - (当期能源×上期GDP)/(当期GDP×上期能源)) / 5 × 100
- 能源消费弹性 = 能源消费年增长率 / GDP年增长率

### 分析器 (analyzer.py)
- 自动加载各模块输出数据
- 支持直接输入数据（如人口）
- 执行完整的情景数据计算
- 导出结果到CSV

### 使用方式

```python
from src.scenario_summary import ScenarioSummaryAnalyzer

analyzer = ScenarioSummaryAnalyzer()
results = analyzer.run(
    input_path='data/input/scenario_summary_input.csv',
    output_path='data/output/scenario_summary_output.csv'
)
```

或使用命令行：
```bash
python run_scenario_summary.py
```

### 代码结构说明
该模块位于 `src/scenario_summary/`，与 `src/modules/` 并列，因为它需要读取modules的计算结果进行再分析计算。这种结构便于后续扩展其他汇总分析模块。

主要特点
模块位置：放在 src/scenario_summary/，与 src/modules/ 并列，便于读取modules的计算结果进行再分析

数据来源：自动从4个模块输出文件读取数据：

macro_output.csv (GDP相关)
structure_output.csv (能源消费结构)
trajectory_output.csv (碳排放轨迹)
template_output.csv (非CO2温室气体)
计算公式：完整实现了temp11.xlsx中的所有计算公式，包括：

能源相关CO2排放量汇总
温室气体排放总量
各类强度指标和下降率
能源消费弹性
输出格式：CSV格式，包含32个指标，覆盖2020-2060年

运行 python run_scenario_summary.py 即可执行计算并生成结果。

==========================================================================================

# 统计表格模块结构
src/statistics/
├── __init__.py          # 模块入口，导出主要类
├── variables.py         # 变量定义（年份、指标名称、数据源映射）
├── formulas.py          # 计算公式定义
└── analyzer.py          # 分析器（数据加载、计算、导出）

run_statistics.py        # 运行脚本
data/input/statistics_input.csv   # 输入说明文件
data/output/statistics_output.csv # 输出结果
主要功能
变量定义 (variables.py)：定义了7个部分的年份列表和指标名称
公式定义 (formulas.py)：实现了CO2排放、温室气体、用电量等计算公式
分析器 (analyzer.py)：
从4个数据源CSV加载数据（能源消费结构、碳排放轨迹、数据模板、宏观测算参考）
支持从其他模块的计算结果直接加载
执行7个部分的统计计算
导出CSV和打印结果
使用方式
from src.statistics import StatisticsAnalyzer

analyzer = StatisticsAnalyzer()
analyzer.load_from_csv('data/output')  # 从CSV加载
results = analyzer.calculate()          # 执行计算
analyzer.export_to_csv('data/output/statistics_output.csv')  # 导出
该模块与modules文件夹并列，可以读取modules的计算结果进行再分析，便于后续扩展。