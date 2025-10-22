# Dockerfile - 矿能云析系统Docker镜像

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements /app/requirements

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/data/uploads \
    /app/data/history \
    /app/data/resource \
    /app/data/charts \
    /app/logs

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# 启动命令
CMD ["python", "run.py", "--env", "production", "--host", "0.0.0.0", "--port", "5000"]
