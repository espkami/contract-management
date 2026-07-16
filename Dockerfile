
# ========== 阶段一：构建前端 ==========
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# 配置 npm 国内镜像源
RUN npm config set registry https://mirrors.tencent.com/npm/

# 复制前端代码
COPY frontend/package*.json ./
COPY frontend/ ./

# 安装依赖并构建
RUN npm install && npm run build


# ========== 阶段二：构建后端 ==========
FROM python:3.11-slim

WORKDIR /app

# 配置 pip 国内镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 复制依赖文件
COPY app/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/main.py .

# 复制前端构建产物到静态目录
COPY --from=frontend-builder /frontend/dist ./static/

# 创建数据目录
RUN mkdir -p /data/uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
