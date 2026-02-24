# 部署文档

## 1. 部署概述

### 1.1 部署目标
将系统部署到生产环境，确保系统稳定运行，提供持续的服务。

### 1.2 部署方式
- **本地部署**：适合开发和测试
- **Docker部署**：适合生产环境
- **云服务部署**：适合大规模应用

## 2. 系统要求

### 2.1 硬件要求
- **CPU**: 2核或以上
- **内存**: 4GB或以上
- **存储**: 20GB或以上
- **网络**: 100Mbps或以上

### 2.2 软件要求
- **操作系统**: Windows 10/11, macOS 11+, Ubuntu 20.04+
- **Python**: 3.10+
- **Node.js**: 18.0+
- **数据库**: SQLite 3.40+, PostgreSQL 13+

## 3. 本地部署

### 3.1 后端部署

#### 3.1.1 创建虚拟环境
```bash
cd backend
python -m venv .venv
```

#### 3.1.2 激活虚拟环境
- **Windows**:
```bash
.venv\Scripts\activate
```

- **Linux/macOS**:
```bash
source .venv/bin/activate
```

#### 3.1.3 安装依赖
```bash
pip install -r requirements.txt
```

#### 3.1.4 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库、API密钥等配置
```

#### 3.1.5 初始化数据库
```bash
# 创建数据库表
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 或者使用Alembic
alembic upgrade head
```

#### 3.1.6 运行服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.2 前端部署

#### 3.2.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2.2 配置API地址
```bash
# 编辑 .env 文件
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### 3.2.3 运行开发服务器
```bash
npm run dev
```

#### 3.2.4 构建生产版本
```bash
npm run build
```

#### 3.2.5 预览生产版本
```bash
npm run preview
```

## 4. Docker部署

### 4.1 Docker环境准备

#### 4.1.1 安装Docker
- **Windows**: 下载Docker Desktop
- **Linux**: `sudo apt-get install docker.io`
- **macOS**: 下载Docker Desktop

#### 4.1.2 验证安装
```bash
docker --version
docker-compose --version
```

### 4.2 构建Docker镜像

#### 4.2.1 后端Dockerfile
```dockerfile
# Dockerfile.backend
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY .env.example .env

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 4.2.2 前端Dockerfile
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 构建应用
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 4.2.3 Nginx配置
```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4.3 Docker Compose配置

#### 4.3.1 docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: obe-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./obe_analysis.db
      - DEBUG=False
    volumes:
      - ./backend/data:/app/data
    networks:
      - obe-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: obe-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - obe-network

  # 可选：PostgreSQL数据库
  postgres:
    image: postgres:13
    container_name: obe-postgres
    environment:
      POSTGRES_DB: obe_analysis
      POSTGRES_USER: obe_user
      POSTGRES_PASSWORD: obe_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - obe-network

volumes:
  postgres_data:

networks:
  obe-network:
    driver: bridge
```

### 4.4 启动服务
```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps
```

## 5. 云服务部署

### 5.1 阿里云部署

#### 5.1.1 准备ECS实例
- 选择Ubuntu 20.04系统
- 配置安全组规则（开放80、8000端口）
- 配置SSH密钥对

#### 5.1.2 安装Docker
```bash
# 连接到ECS实例
ssh root@your-ecs-ip

# 安装Docker
apt-get update
apt-get install -y docker.io docker-compose

# 启动Docker服务
systemctl start docker
systemctl enable docker
```

#### 5.1.3 部署应用
```bash
# 复制项目文件到ECS
scp -r ./ root@your-ecs-ip:/opt/obe-analysis

# 进入项目目录
cd /opt/obe-analysis

# 启动服务
docker-compose up -d
```

### 5.2 腾讯云部署

#### 5.2.1 使用云开发
```bash
# 安装CloudBase CLI
npm i -g @cloudbase/cli

# 登录腾讯云
tcb login

# 部署后端
cd backend
tcb deploy

# 部署前端
cd frontend
tcb deploy
```

## 6. 配置管理

### 6.1 环境变量配置

#### 6.1.1 后端环境变量
```bash
# .env 生产环境配置
PROJECT_NAME=OBE Paper Analysis System
VERSION=0.1.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/obe_analysis

# AI API配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 安全配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

#### 6.1.2 前端环境变量
```bash
# .env.production
VITE_API_BASE_URL=https://your-domain.com/api/v1
VITE_APP_TITLE=OBE试卷分析系统
VITE_APP_VERSION=0.1.0
```

### 6.2 配置文件模板
```bash
# 提供配置模板
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

## 7. 监控与维护

### 7.1 日志管理

#### 7.1.1 后端日志
```python
# app/core/logging.py
import logging
import sys
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)
```

#### 7.1.2 Docker日志
```bash
# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 日志轮转
docker run --log-opt max-size=10m --log-opt max-file=3
```

### 7.2 性能监控

#### 7.2.1 使用Prometheus和Grafana
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### 7.2.2 应用性能指标
- 接口响应时间
- 数据库查询时间
- 内存使用情况
- CPU使用率

### 7.3 备份策略

#### 7.3.1 数据库备份
```bash
# 备份脚本 backup.sh
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/obe-analysis"
mkdir -p $BACKUP_DIR

# 备份PostgreSQL
pg_dump -U obe_user -d obe_analysis > $BACKUP_DIR/db_$DATE.sql

# 备份SQLite
cp /opt/obe-analysis/backend/data/obe_analysis.db $BACKUP_DIR/sqlite_$DATE.db

# 压缩备份
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR db_$DATE.sql sqlite_$DATE.db

# 删除旧备份（保留30天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
```

#### 7.3.2 自动化备份
```bash
# 添加到crontab
0 2 * * * /opt/obe-analysis/backup.sh
```

## 8. 安全配置

### 8.1 SSL/TLS配置

#### 8.1.1 使用Let's Encrypt
```bash
# 安装Certbot
apt-get install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

#### 8.1.2 Nginx SSL配置
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://frontend;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

### 8.2 安全加固

#### 8.2.1 防火墙配置
```bash
# 开放必要端口
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 查看状态
ufw status
```

#### 8.2.2 安全头配置
```nginx
# 添加安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## 9. 故障排查

### 9.1 常见问题

#### 9.1.1 服务无法启动
```bash
# 检查日志
docker-compose logs backend

# 检查端口占用
netstat -tuln | grep 8000

# 检查配置文件
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

#### 9.1.2 数据库连接失败
```bash
# 检查数据库服务状态
systemctl status postgresql

# 检查连接配置
psql -h localhost -U obe_user -d obe_analysis

# 检查网络连接
telnet localhost 5432
```

#### 9.1.3 前端构建失败
```bash
# 清除缓存
npm cache clean --force

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查Node版本
node --version
```

### 9.2 性能问题

#### 9.2.1 慢查询优化
```python
# 使用SQLAlchemy事件记录慢查询
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # 超过1秒的查询
        logger.warning(f"慢查询: {statement}, 耗时: {total:.2f}s")
```

#### 9.2.2 内存泄漏检测
```bash
# 使用memory_profiler
pip install memory_profiler

# 监控内存使用
python -m memory_profiler your_script.py

# 使用tracemalloc
python -m tracemalloc your_script.py
```

## 10. 升级维护

### 10.1 版本升级

#### 10.1.1 后端升级
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 数据库迁移
alembic upgrade head

# 重启服务
docker-compose restart backend
```

#### 10.1.2 前端升级
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
npm install

# 重新构建
npm run build

# 重启Nginx
docker-compose restart frontend
```

### 10.2 回滚操作
```bash
# 查看历史版本
git log --oneline

# 回滚到指定版本
git checkout <commit-hash>

# 重新构建和部署
docker-compose build
docker-compose up -d
```

## 11. 容器化最佳实践

### 11.1 镜像优化

#### 11.1.1 多阶段构建
```dockerfile
# 后端优化Dockerfile
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -t /app/deps

FROM python:3.10-slim

WORKDIR /app

# 只复制依赖
COPY --from=builder /app/deps /usr/local/lib/python3.10/site-packages

# 复制应用代码
COPY app/ ./app/
COPY .env .env

EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

#### 11.1.2 .dockerignore配置
```dockerfile
# .dockerignore
__pycache__
*.pyc
*.pyo
.env
.venv
.git
*.md
Dockerfile
docker-compose.yml
```

### 11.2 容器安全

#### 11.2.1 非root用户运行
```dockerfile
FROM python:3.10-slim

# 创建非root用户
RUN groupadd -r obe && useradd -r -g obe obe

WORKDIR /app

# 复制应用
COPY --chown=obe:obe . .

# 切换到非root用户
USER obe

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 11.2.2 资源限制
```yaml
# docker-compose.yml 添加资源限制
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 12. CI/CD配置

### 12.1 GitHub Actions部署

#### 12.1.1 自动部署到服务器
```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/obe-analysis
          git pull origin main
          docker-compose build
          docker-compose up -d
          docker system prune -f
```

#### 12.1.2 自动部署到Docker Hub
```yaml
name: Publish Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Build and Push Backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          your-dockerhub-username/obe-backend:latest
          your-dockerhub-username/obe-backend:${{ github.sha }}

    - name: Build and Push Frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: |
          your-dockerhub-username/obe-frontend:latest
          your-dockerhub-username/obe-frontend:${{ github.sha }}
```

### 12.2 Jenkins部署

#### 12.2.1 Jenkins Pipeline
```groovy
pipeline {
    agent any

    environment {
        DOCKER_HUB = credentials('docker-hub')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Backend') {
            steps {
                sh 'cd backend && docker build -t obe-backend .'
            }
        }

        stage('Build Frontend') {
            steps {
                sh 'cd frontend && docker build -t obe-frontend .'
            }
        }

        stage('Test') {
            steps {
                sh 'cd backend && docker run obe-backend pytest'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker-compose down
                    docker-compose up -d
                '''
            }
        }
    }
}
```

## 13. 文档维护

### 13.1 API文档更新
```bash
# 生成OpenAPI文档
uvicorn app.main:app --docs-url=/docs

# 导出OpenAPI规范
curl http://localhost:8000/openapi.json > openapi.json
```

### 13.2 部署文档更新
- 记录每次部署的详细信息
- 更新配置文件示例
- 记录已知问题和解决方案

## 14. 部署检查清单

### 14.1 部署前检查
- [ ] 代码已提交到版本控制
- [ ] 所有测试通过
- [ ] 配置文件已更新
- [ ] 数据库迁移脚本已准备
- [ ] 备份策略已配置
- [ ] 监控和日志已配置

### 14.2 部署后验证
- [ ] 服务正常运行
- [ ] API接口可访问
- [ ] 数据库连接正常
- [ ] 文件上传功能正常
- [ ] 分析计算功能正常
- [ ] 报表导出功能正常
- [ ] 系统响应时间符合要求

### 14.3 安全验证
- [ ] HTTPS配置正确
- [ ] 安全头已添加
- [ ] 防火墙规则正确
- [ ] API访问控制正常
- [ ] 敏感信息已加密
- [ ] 日志审计功能正常

---

*部署文档最后更新：2026年2月24日*