# 🚀 快速测试部署指南

## 📋 概述

本指南帮助你在不同平台快速部署和测试知识管理平台。

---

## 🖥️ 平台选择

### 支持的平台
- ✅ **本地开发** - Windows/macOS/Linux
- ✅ **Docker** - 任何支持Docker的平台
- ✅ **Kubernetes** - 本地K8s或云端K8s
- ✅ **云服务** - AWS/Azure/GCP/阿里云

---

## 🎯 方法1: 本地快速测试（最简单）

### Windows

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 运行一键部署脚本
quick-start.bat
```

### macOS/Linux

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 赋予执行权限并运行
chmod +x quick-start.sh
./quick-start.sh
```

### 访问应用

部署完成后访问：
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

**默认账号**: `admin` / `admin123`

---

## 🐳 方法2: Docker部署（推荐用于测试）

### 前提条件
- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose

### 部署步骤

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 使用自动配置的Docker Compose
docker-compose -f deployment/docker-compose.auto.yml up -d

# 3. 查看日志
docker-compose -f deployment/docker-compose.auto.yml logs -f

# 4. 停止服务
docker-compose -f deployment/docker-compose.auto.yml down
```

### 访问应用

- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库管理**: http://localhost:8080 (phpMyAdmin)

---

## ☸️ 方法3: Kubernetes部署（适合生产测试）

### 前提条件
- Kubernetes集群（本地Minikube/Docker Desktop K8s 或云端K8s）
- kubectl命令行工具

### 使用kubectl部署

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 创建命名空间
kubectl apply -f deployment/kubernetes/namespace.yaml

# 3. 部署所有组件
kubectl apply -f deployment/kubernetes/

# 4. 查看部署状态
kubectl get pods -n knowledge-platform
kubectl get services -n knowledge-platform

# 5. 访问应用（如果使用LoadBalancer）
kubectl get svc frontend-service -n knowledge-platform
```

### 使用Helm部署

```bash
# 1. 克隆仓库
git clone https://github.com/jackchen1941/knowledge_platform.git
cd knowledge_platform

# 2. 安装Helm Chart
helm install knowledge-platform ./deployment/helm-chart \
  --namespace knowledge-platform \
  --create-namespace

# 3. 查看状态
helm status knowledge-platform -n knowledge-platform

# 4. 卸载
helm uninstall knowledge-platform -n knowledge-platform
```

---

## 🌐 方法4: 云平台部署

### AWS部署

```bash
# 使用ECS或EKS
# 1. 构建并推送Docker镜像到ECR
# 2. 使用ECS任务定义或EKS部署

# 详细步骤参考 DEPLOYMENT_GUIDE.md
```

### Azure部署

```bash
# 使用Azure Container Instances或AKS
# 详细步骤参考 DEPLOYMENT_GUIDE.md
```

### 阿里云部署

```bash
# 使用容器服务ACK
# 详细步骤参考 DEPLOYMENT_GUIDE.md
```

---

## 🧪 测试验证

### 1. 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查系统状态
curl http://localhost:8000/status
```

### 2. API测试

```bash
# 用户注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123456!",
    "full_name": "Test User"
  }'

# 用户登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456!"
  }'
```

### 3. 运行测试套件

```bash
# 运行所有测试
python run_tests.py

# 运行特定类别测试
python run_tests.py --category security
python run_tests.py --category integration
```

### 4. 性能测试

```bash
# 使用Apache Bench
ab -n 1000 -c 10 http://localhost:8000/

# 使用wrk
wrk -t4 -c100 -d30s http://localhost:8000/
```

---

## 🔍 故障排除

### 问题1: 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :3000

# 终止进程
kill -9 <PID>

# 或使用不同端口
# 修改 docker-compose.yml 中的端口映射
```

### 问题2: 数据库连接失败

```bash
# 检查数据库容器状态
docker ps | grep mysql

# 查看数据库日志
docker logs <mysql-container-id>

# 重启数据库容器
docker restart <mysql-container-id>
```

### 问题3: 前端无法连接后端

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查前端环境变量
# 确保 REACT_APP_API_URL 指向正确的后端地址
```

### 问题4: Docker镜像构建失败

```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

---

## 📊 性能基准

### 预期性能指标

在标准配置下（2核CPU，4GB内存）：

- **API响应时间**: < 300ms (平均)
- **数据库查询**: < 50ms (平均)
- **WebSocket延迟**: < 10ms
- **并发用户**: 100+ 用户
- **吞吐量**: 1000+ 请求/秒

### 监控指标

```bash
# CPU使用率
docker stats

# 内存使用
docker stats --format "table {{.Container}}\t{{.MemUsage}}"

# 网络流量
docker stats --format "table {{.Container}}\t{{.NetIO}}"
```

---

## 🔒 安全测试

### 运行安全测试套件

```bash
# 运行完整安全测试
python tests/security/test_security_comprehensive.py

# 预期结果: 26/26 测试通过
```

### 手动安全检查

```bash
# 1. 检查SQL注入防护
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin'\'' OR '\''1'\''='\''1", "password": "test"}'

# 2. 检查XSS防护
curl -X POST http://localhost:8000/api/v1/knowledge/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "<script>alert('\''XSS'\'')</script>", "content": "test"}'

# 3. 检查暴力破解保护
# 连续5次错误登录应该触发账户锁定
```

---

## 📈 扩展测试

### 水平扩展测试

```bash
# Docker Compose扩展
docker-compose -f deployment/docker-compose.auto.yml up -d --scale backend=3

# Kubernetes扩展
kubectl scale deployment backend --replicas=3 -n knowledge-platform
```

### 负载测试

```bash
# 使用Locust进行负载测试
pip install locust

# 创建locustfile.py并运行
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🎯 测试清单

部署后请验证以下功能：

### 基础功能
- [ ] 用户注册和登录
- [ ] 创建知识条目
- [ ] 搜索功能
- [ ] 分类和标签
- [ ] 文件上传

### 高级功能
- [ ] WebSocket实时通信
- [ ] 多设备同步
- [ ] 通知系统
- [ ] 导入导出
- [ ] 知识图谱

### 性能测试
- [ ] API响应时间 < 300ms
- [ ] 并发100用户无问题
- [ ] 数据库查询优化
- [ ] 内存使用正常

### 安全测试
- [ ] SQL注入防护
- [ ] XSS防护
- [ ] CSRF防护
- [ ] 暴力破解保护
- [ ] 会话安全

---

## 📞 获取帮助

### 遇到问题？

1. **查看日志**
   ```bash
   # Docker
   docker-compose logs -f
   
   # Kubernetes
   kubectl logs -f <pod-name> -n knowledge-platform
   ```

2. **查看文档**
   - [完整部署指南](DEPLOYMENT_GUIDE.md)
   - [Git问题解决](GIT_TROUBLESHOOTING.md)
   - [API文档](http://localhost:8000/docs)

3. **提交Issue**
   - GitHub Issues: https://github.com/jackchen1941/knowledge_platform/issues

4. **社区支持**
   - GitHub Discussions: https://github.com/jackchen1941/knowledge_platform/discussions

---

## 🎉 测试成功！

如果所有测试都通过，恭喜你！系统已经准备好用于生产环境了。

### 下一步

1. **配置生产环境**
   - 使用生产级数据库（PostgreSQL/MySQL）
   - 配置HTTPS
   - 设置备份策略
   - 配置监控和日志

2. **性能优化**
   - 启用Redis缓存
   - 配置CDN
   - 数据库索引优化
   - 负载均衡

3. **安全加固**
   - 更改默认密码
   - 配置防火墙
   - 启用速率限制
   - 定期安全审计

---

**文档版本**: 1.0.0  
**最后更新**: 2024-02-09  
**维护者**: Knowledge Platform Team