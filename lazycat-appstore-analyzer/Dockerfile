FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖（精简版）
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py /app/
COPY app/ /app/app/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY data/ /app/data/

# 创建必要的目录
RUN mkdir -p /lzcapp/var/database \
    /lzcapp/var/uploads \
    /lzcapp/var/config \
    /lzcapp/cache \
    && chmod -R 755 /app \
    && chmod -R 777 /lzcapp/var

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "main.py"]