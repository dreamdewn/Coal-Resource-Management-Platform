# 矿能云析系统 - 项目结构说明

## 📁 项目目录结构

```
python_project/
├── 📁 config/                     # 配置文件目录
│   └── settings.py               # 系统配置文件
├── 📁 data/                      # 数据存储目录
│   ├── 📁 uploads/               # 上传文件存储
│   │   └── .gitkeep             # 保持目录存在
│   ├── 📁 history/               # 历史数据存储
│   │   └── .gitkeep             # 保持目录存在
│   ├── 📁 resource/              # 资源数据存储
│   │   └── .gitkeep             # 保持目录存在
│   └── 📁 charts/                # 图表文件存储
│       └── .gitkeep             # 保持目录存在
├── 📁 docs/                      # 文档目录
│   ├── 📁 api/                   # API文档
│   └── 📁 user_guide/            # 用户指南
│       ├── README.md             # 项目说明文档
│       └── ARCHITECTURE.md       # 架构设计文档
├── 📁 logs/                      # 日志文件目录
│   └── .gitkeep                 # 保持目录存在
├── 📁 src/                       # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── 📁 api/                   # API接口模块
│   │   ├── __init__.py
│   │   └── routes.py            # API路由定义
│   ├── 📁 core/                  # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── coal_analysis.py     # 煤层分析模块
│   │   ├── pollution_assessment.py # 污染评估模块
│   │   ├── resource_assessment.py # 资源评估模块
│   │   ├── agriculture.py       # 农业利用模块
│   │   └── utils.py             # 工具函数
│   ├── 📁 models/                # 数据模型
│   │   ├── __init__.py
│   │   └── coal_model.py        # 煤层数据模型
│   ├── 📁 services/              # 服务层
│   ├── 📁 static/                # 静态资源
│   │   ├── 📁 css/               # 样式文件
│   │   ├── 📁 js/                # JavaScript文件
│   │   └── 📁 images/            # 图片资源
│   ├── 📁 templates/             # 模板文件
│   │   └── 📁 pages/             # 页面模板
│   │       ├── index.html        # 主页面
│   │       ├── pollution.html    # 污染监测页面
│   │       ├── resource.html     # 资源评估页面
│   │       └── agriculture.html  # 农业利用页面
│   └── 📁 tests/                 # 测试代码
│       ├── 📁 unit/              # 单元测试
│       └── 📁 integration/       # 集成测试
├── 📁 temp_charts/               # 临时图表存储
├── app.py                       # 主应用程序入口
├── requirements                 # 项目依赖列表
├── .gitignore                   # Git忽略文件配置
└── PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
```

## 🎯 目录说明

### 📁 config/ - 配置文件目录
- **settings.py**: 系统配置文件，包含不同环境的配置参数
- 支持开发、生产、测试三种环境配置
- 包含文件上传、数据存储、煤层识别等参数配置

### 📁 data/ - 数据存储目录
- **uploads/**: 存储用户上传的Excel/CSV数据文件
- **history/**: 存储历史分析结果数据
- **resource/**: 存储资源评估相关数据
- **charts/**: 存储生成的图表文件

### 📁 docs/ - 文档目录
- **api/**: API接口文档
- **user_guide/**: 用户使用指南和架构文档

### 📁 src/ - 源代码目录
- **api/**: API接口层，处理HTTP请求和响应
- **core/**: 核心业务逻辑，包含所有分析算法
- **models/**: 数据模型定义
- **services/**: 服务层，封装业务逻辑
- **static/**: 静态资源文件
- **templates/**: HTML模板文件
- **tests/**: 测试代码

### 📁 logs/ - 日志目录
- 存储系统运行日志
- 包含错误日志、访问日志等

## 🔧 文件说明

### 核心文件
- **app.py**: Flask应用主入口，包含路由定义和服务器启动
- **requirements**: 项目依赖包列表
- **.gitignore**: Git版本控制忽略文件配置

### 配置文件
- **config/settings.py**: 系统配置，支持多环境
- 包含文件上传、数据存储、算法参数等配置

### 数据模型
- **src/models/coal_model.py**: 煤层相关数据模型
- 定义了CoalLayer、CoalAnalysisResult等数据结构

## 🚀 使用说明

### 开发环境启动
```bash
# 安装依赖
pip install -r requirements

# 启动应用
python app.py
```

### 项目结构优势
1. **模块化设计**: 各功能模块独立，便于维护
2. **分层架构**: API、业务逻辑、数据模型分离
3. **配置管理**: 统一的配置管理，支持多环境
4. **数据隔离**: 不同类型数据分别存储
5. **文档完整**: 详细的文档和注释

### 扩展指南
- 新增功能模块：在`src/core/`目录下添加
- 新增API接口：在`src/api/routes.py`中添加
- 新增数据模型：在`src/models/`目录下添加
- 新增页面：在`src/templates/pages/`目录下添加

## 📝 注意事项

1. **数据安全**: 敏感数据文件已添加到`.gitignore`
2. **环境配置**: 生产环境需要修改`config/settings.py`中的配置
3. **日志管理**: 定期清理`logs/`目录下的日志文件
4. **数据备份**: 定期备份`data/`目录下的重要数据
5. **版本控制**: 使用Git进行版本控制，遵循Git Flow工作流

---

**项目结构版本**: v1.0.0  
**最后更新**: 2024年10月22日  
**维护者**: 矿能云析开发团队
