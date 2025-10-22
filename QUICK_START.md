# 🚀 矿能云析系统 - 快速启动指南

## 📋 系统要求

- **Python**: 3.8+ 
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **内存**: 4GB+ (推荐8GB+)
- **存储**: 2GB+ 可用空间

## ⚡ 快速启动

### 方法一：直接启动（推荐）

```bash
# 1. 安装依赖
pip install -r requirements

# 2. 启动系统
python run.py
```

### 方法二：使用Docker

```bash
# 1. 构建镜像
docker build -t coal-analysis .

# 2. 启动容器
docker run -p 5000:5000 coal-analysis
```

### 方法三：使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d
```

## 🌐 访问系统

启动成功后，打开浏览器访问：

- **主页面**: http://localhost:5000
- **API接口**: http://localhost:5000/api/v1/health

## 📁 项目结构

```
python_project/
├── 📁 config/          # 配置文件
├── 📁 data/            # 数据存储
├── 📁 docs/            # 文档
├── 📁 src/             # 源代码
│   ├── 📁 core/        # 核心模块
│   ├── 📁 api/         # API接口
│   ├── 📁 models/      # 数据模型
│   └── 📁 templates/   # 页面模板
├── app.py              # 主应用
├── run.py              # 启动脚本
└── requirements        # 依赖列表
```

## 🔧 配置说明

### 环境配置

系统支持三种环境：

- **开发环境**: `python run.py --env development`
- **生产环境**: `python run.py --env production`
- **测试环境**: `python run.py --env testing`

### 端口配置

```bash
# 自定义端口
python run.py --port 8080

# 自定义主机和端口
python run.py --host 127.0.0.1 --port 8080
```

### 调试模式

```bash
# 启用调试模式
python run.py --debug
```

## 📊 使用说明

### 1. 上传数据文件

1. 打开浏览器访问 http://localhost:5000
2. 点击"选择文件"按钮
3. 选择包含钻井数据的Excel文件
4. 点击"启动AI分析引擎"

### 2. 查看分析结果

- **图表分析**: 查看不同参数的深度剖面图
- **煤层信息**: 查看识别的煤层位置和厚度
- **深度控制**: 使用滑块调整查看范围

### 3. 进行专项评估

- **污染监测**: 访问 /pollution 页面
- **资源评估**: 访问 /resource 页面
- **农业利用**: 访问 /agriculture 页面

## 🛠️ 开发说明

### 添加新功能

1. **核心模块**: 在 `src/core/` 目录下添加
2. **API接口**: 在 `src/api/routes.py` 中添加
3. **数据模型**: 在 `src/models/` 目录下添加
4. **页面模板**: 在 `src/templates/pages/` 目录下添加

### 运行测试

```bash
# 运行单元测试
python -m pytest src/tests/unit/

# 运行集成测试
python -m pytest src/tests/integration/
```

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   netstat -ano | findstr :5000
   
   # 使用其他端口
   python run.py --port 8080
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   python -m pip install --upgrade pip
   
   # 重新安装依赖
   pip install -r requirements --force-reinstall
   ```

3. **文件上传失败**
   - 检查文件格式是否为Excel/CSV
   - 确认文件大小不超过16MB
   - 验证文件包含必需字段

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 📞 技术支持

- **文档**: 查看 `docs/` 目录
- **架构**: 查看 `ARCHITECTURE.md`
- **项目结构**: 查看 `PROJECT_STRUCTURE.md`

## 🔄 更新说明

### 从旧版本升级

1. 备份现有数据
2. 拉取最新代码
3. 安装新依赖
4. 重启服务

```bash
# 备份数据
cp -r data/ data_backup/

# 更新代码
git pull origin main

# 安装依赖
pip install -r requirements

# 重启服务
python run.py
```

---

**矿能云析系统** - 让数据驱动决策，让智能赋能矿业 🌟
