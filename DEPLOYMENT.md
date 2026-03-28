# PDS CALC 部署指南

## 项目概述

PDS CALC 是一个用于小型过程系统（涡轮发电 + 换热）的热力计算与设备选型工具。

- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Python 3.12 + FastAPI + Uvicorn
- **端口**: 前端 80, 后端 8000

## 部署方式

### 方式一：Docker Compose 部署（推荐）

#### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 服务器内存至少 2GB
- 磁盘空间至少 5GB

#### 部署步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Small-Process-Calc
```

2. **配置环境变量（可选）**
```bash
cp .env.example .env
# 编辑 .env 文件配置端口等参数
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **验证部署**
```bash
docker-compose ps
# 查看日志
docker-compose logs -f
```

5. **访问应用**
- 前端：http://your-server-ip:8080
- 后端 API: http://your-server-ip:8000
- API 文档：http://your-server-ip:8000/docs

#### 停止服务
```bash
docker-compose down
```

#### 重启服务
```bash
docker-compose restart
```

### 方式二：直接部署

#### 后端部署

1. **安装 Python 3.12**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# CentOS/RHEL
sudo yum install python3.12 python3.12-devel
```

2. **安装依赖**
```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **启动后端**
```bash
# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 后台运行
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > backend.log 2>&1 &
```

#### 前端部署

1. **安装 Node.js 18+**
```bash
# 使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

2. **构建前端**
```bash
cd frontend
npm install
npm run build
```

3. **配置 Nginx**
```bash
sudo apt install nginx  # Ubuntu/Debian
sudo yum install nginx  # CentOS/RHEL
```

复制 `nginx.conf` 到 Nginx 配置目录：
```bash
sudo cp nginx.conf /etc/nginx/sites-available/pds-calc
sudo ln -s /etc/nginx/sites-available/pds-calc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 防火墙配置

### Ubuntu (UFW)
```bash
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

### CentOS (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 云服务器安全组

在云平台控制台添加以下入站规则：
- TCP 8080 - 前端访问
- TCP 8000 - API 访问（可选，如果通过 Nginx 代理则不需要）

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| BACKEND_PORT | 后端服务端口 | 8000 |
| FRONTEND_PORT | 前端服务端口 | 8080 |
| API_HOST | API 服务地址 | backend |

## 故障排查

### 后端无法启动
```bash
# 查看日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep 8000
```

### 前端无法访问
```bash
# 查看日志
docker-compose logs frontend

# 检查 Nginx 配置
docker-compose exec frontend nginx -t
```

### 重启单个服务
```bash
docker-compose restart backend
docker-compose restart frontend
```

## 健康检查

```bash
# 检查后端 API
curl http://localhost:8000/health

# 检查前端
curl http://localhost:8080/
```

## 备份与恢复

### 备份
```bash
tar -czf pds-calc-backup-$(date +%Y%m%d).tar.gz Small-Process-Calc/
```

### 恢复
```bash
tar -xzf pds-calc-backup-*.tar.gz
cd Small-Process-Calc
docker-compose up -d
```

## 性能优化建议

1. **增加后端 worker 数量** (多核 CPU)
```yaml
# docker-compose.yml
environment:
  - WORKERS=8  # CPU 核心数 * 2 + 1
```

2. **启用 Redis 缓存** (可选)
```yaml
# 添加 Redis 服务到 docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

3. **配置 Nginx 缓存**
```nginx
# nginx.conf 中添加
location /api/ {
  proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
  proxy_cache api_cache;
  proxy_cache_valid 200 10m;
}
```

## 安全建议

1. **使用 HTTPS** - 配置 SSL 证书
2. **限制 API 访问** - 配置 IP 白名单
3. **定期更新依赖** - `pip install --upgrade -r requirements.txt`
4. **配置日志轮转** - 防止日志文件过大

## 联系支持

如有部署问题，请查看项目 GitHub Issues 或联系开发团队。
