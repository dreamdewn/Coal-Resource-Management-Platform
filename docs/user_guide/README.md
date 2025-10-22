# 矿能云析 - 智能煤层分析系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 项目概述

**矿能云析**是一个基于人工智能的煤层分析系统，专门用于处理和分析钻井数据，提供煤层识别、污染评估、资源评估和农业利用建议等功能。系统采用现代化的Web界面和先进的数据分析算法，为矿业和农业领域提供科学决策支持。

### 🎯 核心功能

- **🔍 智能煤层识别**: 基于多参数物理特性自动识别煤层位置和厚度
- **🛡️ 污染监测评估**: 综合分析煤层污染程度和扩散风险
- **📊 资源储量计算**: 精确计算煤炭资源储量和开采规划
- **🌱 农业利用建议**: 提供土地复垦和农作物种植建议
- **📈 数据可视化**: 实时生成交互式图表和分析报告

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows/Linux/macOS
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd python_project
```

2. **安装依赖**
```bash
pip install -r requirements
```

3. **启动应用**
```bash
python app.py
```

4. **访问系统**
打开浏览器访问: `http://localhost:5000`

### 数据格式要求

系统支持Excel格式文件（.xlsx, .xls）和CSV文件，需要包含以下字段：

| 字段名 | 描述 | 单位 |
|--------|------|------|
| 深度 | 钻井深度 | 米(m) |
| 深侧向 | 深侧向电阻率 | Ω·m |
| 浅侧向 | 浅侧向电阻率 | Ω·m |
| 声波时差 | 声波传播时差 | μs/m |
| 自然伽玛 | 自然伽马射线强度 | API |
| 密度 | 岩石密度 | g/cm³ |

## 📖 功能详解

### 1. 智能煤层识别

系统通过分析以下物理参数自动识别煤层：

- **双侧向电阻率**: 50-2000 Ω·m
- **声波时差**: 300-600 μs/m  
- **自然伽玛**: 20-80 API
- **密度**: 1.0-1.8 g/cm³

**输出结果**:
- 煤层位置和厚度
- 煤层品质评估
- 开采难度分析
- 可视化深度剖面图

### 2. 污染监测评估

基于多参数综合分析评估煤层污染：

**评估指标**:
- 污染程度评分（0-100分）
- 污染等级分类（轻微/轻度/中度/严重/极严重）
- 污染物类型识别（重金属/有机污染物/酸性物质）
- 扩散风险分析

**影响分析**:
- 生态影响评估
- 水资源影响分析
- 土壤质量影响
- 健康风险评估

### 3. 资源储量计算

精确计算煤炭资源储量和制定开采规划：

**计算内容**:
- 总资源储量（吨）
- 煤层体积计算
- 开采方法推荐
- 回收率预测
- 开采优先级排序

**开采方法**:
- 露天开采（浅层厚煤层）
- 长壁开采（中深度煤层）
- 分层开采（厚煤层）
- 窄煤柱开采（薄煤层）
- 水力开采（深层煤层）
- 房柱式开采（通用）

### 4. 农业利用建议

基于土壤质量分析提供农业利用方案：

**土壤分析**:
- pH值评估
- 有机质含量
- 煤含量检测
- 水分含量
- 肥力评分

**复垦方案**:
- 土壤改良措施
- 植被恢复计划
- 工程措施建议
- 时间成本评估

**种植建议**:
- 适合作物推荐
- 施肥方案
- 灌溉策略
- 管理要点

## 🏗️ 技术架构

### 后端技术栈

- **Flask**: Web框架
- **Pandas**: 数据处理
- **NumPy**: 数值计算
- **Matplotlib**: 图表生成
- **Scikit-learn**: 机器学习算法
- **SciPy**: 科学计算

### 前端技术栈

- **HTML5/CSS3**: 页面结构
- **Bootstrap 5**: UI框架
- **Chart.js**: 数据可视化
- **JavaScript**: 交互逻辑
- **NoUiSlider**: 范围选择器

### 数据流程

```
数据上传 → 格式验证 → 参数计算 → 煤层识别 → 分析评估 → 结果可视化
```

## 📁 项目结构

```
python_project/
├── app.py                 # 主应用程序
├── coal_analysis.py       # 煤层分析模块
├── pollution_assessment.py # 污染评估模块
├── resource_assessment.py # 资源评估模块
├── agriculture.py         # 农业利用模块
├── utils.py              # 工具函数
├── requirements          # 依赖列表
├── index.html            # 主页面
├── pollution.html        # 污染监测页面
├── resource.html         # 资源评估页面
├── agriculture.html      # 农业利用页面
├── uploads/              # 上传文件目录
├── history_data/         # 历史数据目录
├── resource_data/        # 资源数据目录
└── temp_charts/          # 临时图表目录
```

## 🔧 API接口

### 文件上传
```http
POST /upload
Content-Type: multipart/form-data

参数:
- file: 数据文件
```

### 数据获取
```http
GET /data/{filename}?start={start_depth}&end={end_depth}

参数:
- filename: 文件名
- start: 起始深度（可选）
- end: 结束深度（可选）
```

### 污染评估
```http
POST /pollution-assessment
Content-Type: multipart/form-data

参数:
- file: 数据文件
- location: 位置信息
- notes: 备注信息
```

### 资源评估
```http
POST /resource-assessment
Content-Type: multipart/form-data

参数:
- file: 数据文件
- location: 位置信息
- area: 面积（平方米）
- notes: 备注信息
```

### 农业评估
```http
POST /agriculture-assessment
Content-Type: multipart/form-data

参数:
- file: 数据文件
- location: 位置信息
- area: 面积（平方米）
- type: 评估类型（reclamation/agriculture/both）
- notes: 备注信息
```

## 📊 使用示例

### 1. 上传数据文件

1. 打开系统主页
2. 点击"选择文件"按钮
3. 选择包含钻井数据的Excel文件
4. 点击"启动AI分析引擎"

### 2. 查看分析结果

- **图表分析**: 查看不同参数的深度剖面图
- **煤层信息**: 查看识别的煤层位置和厚度
- **深度控制**: 使用滑块调整查看范围

### 3. 进行专项评估

- **污染监测**: 上传数据到污染监测页面
- **资源评估**: 上传数据到资源评估页面  
- **农业利用**: 上传数据到农业利用页面

## ⚙️ 配置说明

### 环境变量

```bash
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### 煤层识别参数

可在 `coal_analysis.py` 中调整煤层识别阈值：

```python
# 煤层识别条件
coal_conditions = (
    (data['双侧向电阻率'] >= 50) & (data['双侧向电阻率'] <= 2000) &
    (data['声波时差'] >= 300) & (data['声波时差'] <= 600) &
    (data['自然伽玛'] >= 20) & (data['自然伽玛'] <= 80) &
    (data['密度'] >= 1.0) & (data['密度'] <= 1.8)
)
```

## 🐛 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件格式是否为支持的格式
   - 确认文件大小不超过16MB
   - 验证文件包含必需的字段

2. **图表显示异常**
   - 检查浏览器是否支持Canvas
   - 确认JavaScript已启用
   - 清除浏览器缓存

3. **中文字体显示问题**
   - Windows: 确保系统安装了中文字体
   - Linux: 安装文泉驿字体包
   - macOS: 使用系统默认中文字体

### 日志查看

系统日志保存在 `coal_app.log` 文件中，可通过以下命令查看：

```bash
tail -f coal_app.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目链接: [https://github.com/yourusername/python_project](https://github.com/yourusername/python_project)

## 🙏 致谢

感谢以下开源项目的支持：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Pandas](https://pandas.pydata.org/) - 数据处理
- [Matplotlib](https://matplotlib.org/) - 图表库
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [Chart.js](https://www.chartjs.org/) - 图表库

---

**矿能云析** - 让数据驱动决策，让智能赋能矿业 🌟
