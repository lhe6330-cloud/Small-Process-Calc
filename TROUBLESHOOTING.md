# PDS CALC 故障排查指南

## 问题：点击计算以后，不计算也不报错

### 可能原因及解决方案

#### 1. 前端无法连接到后端 API

**症状**：点击计算按钮后，没有任何反应，没有计算结果也没有错误提示。

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 切换到 "Console"（控制台）标签
3. 查看是否有红色的错误信息

**常见错误及解决**：

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `net::ERR_CONNECTION_REFUSED` | 后端服务未启动 | 检查后端是否正常运行：`docker-compose ps` |
| `net::ERR_NAME_NOT_RESOLVED` | DNS 解析失败 | 检查 docker-compose 网络配置 |
| `CORS policy` | 跨域请求被阻止 | 检查后端 CORS 配置或 Nginx 代理配置 |
| `404 Not Found` | API 路径错误 | 检查 Nginx 是否正确配置 `/api/` 代理 |

---

#### 2. 后端服务未启动

**检查方法**：
```bash
# Docker 部署
docker-compose ps

# 查看后端日志
docker-compose logs backend
```

**解决方案**：
```bash
# 重启后端服务
docker-compose restart backend

# 或者完全重启
docker-compose down
docker-compose up -d
```

---

#### 3. Nginx 配置未正确加载

**检查方法**：
```bash
# 检查 Nginx 配置
docker-compose exec frontend nginx -t

# 查看 Nginx 日志
docker-compose logs frontend
```

**解决方案**：
```bash
# 重新加载 Nginx 配置
docker-compose exec frontend nginx -s reload
```

---

#### 4. 端口冲突

**检查方法**：
```bash
# 检查端口占用
netstat -tlnp | grep 8000  # 后端端口
netstat -tlnp | grep 8080  # 前端端口
```

**解决方案**：
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8081:80"  # 将前端端口改为 8081
```

---

#### 5. 防火墙阻止访问

**检查方法**：
```bash
# Ubuntu/Debian
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --list-all
```

**解决方案**：
```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

#### 6. 云服务器安全组配置

**检查方法**：登录云服务器控制台，检查安全组入站规则。

**需要开放的端口**：
- TCP 8080 - 前端访问
- TCP 8000 - API 访问（可选，如果通过 Nginx 代理则不需要）

---

### 调试步骤

#### 步骤 1：检查后端健康状态

```bash
# 访问健康检查接口
curl http://localhost:8000/api/health

# 或者在服务器上
docker-compose exec backend curl http://localhost:8000/health
```

期望返回：
```json
{"status": "ok", "timestamp": "2026-03-28T..."}
```

#### 步骤 2：检查前端是否能访问后端

```bash
# 从前端容器访问后端
docker-compose exec frontend wget -qO- http://backend:8000/api/health
```

#### 步骤 3：测试 API 接口

```bash
# 测试模式 1 计算接口
curl -X POST http://localhost:8000/api/calculate/mode1 \
  -H "Content-Type: application/json" \
  -d '{
    "cold_side": {
      "medium_type": "single",
      "medium": "N2",
      "flow_rate": 1000,
      "flow_unit": "Nm3/h",
      "p_in": 0.5,
      "p_out": 0.48,
      "t_in": 20,
      "t_out": 200
    },
    "hot_side": {
      "medium_type": "single",
      "medium": "H2O",
      "flow_rate": 0.5,
      "flow_unit": "T/h",
      "p_in": 0.6,
      "p_out": 0.55,
      "t_in": 250
    },
    "turbine": {
      "p_out": 0.1,
      "adiabatic_efficiency": 85
    }
  }'
```

---

### 快速修复脚本

如果以上步骤都无法解决问题，可以尝试完全重置：

```bash
# 1. 停止所有服务
docker-compose down

# 2. 删除所有容器和卷（可选，会清除数据）
docker-compose down -v

# 3. 重新构建镜像
docker-compose build --no-cache

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

---

### 联系支持

如果问题仍然存在，请收集以下信息：

1. **浏览器控制台错误**（F12 → Console）
2. **网络请求详情**（F12 → Network → 点击失败的请求）
3. **后端日志**：`docker-compose logs backend`
4. **前端日志**：`docker-compose logs frontend`
5. **系统信息**：操作系统版本、Docker 版本、浏览器版本

将以上信息提交到 GitHub Issues 或联系开发团队。
