# 每日一言系统部署指南

## 项目架构

本项目采用前后端分离架构：

- **后端**：FastAPI + SQLite，提供API服务
- **前端**：纯静态HTML/CSS/JS，通过nginx提供服务

## 部署方式

### 方式一：仅API服务（推荐用于开源分发）

适用于只需要API服务的场景，前端可由用户自行开发。

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OPENAI_API_KEY

# 2. 确保数据库文件存在（首次运行）
touch daily_quotes.db

# 3. 启动API服务
docker compose -f docker-compose.api.yml up -d

# 4. 访问API
curl http://localhost:6000/api/quote
```

**访问地址：**
- API服务：http://localhost:6000
- API文档：http://localhost:6000/docs
- 健康检查：http://localhost:6000/health

### 方式二：完整服务（包含前端预览）

适用于需要完整体验的场景，包含美观的前端预览页面。

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OPENAI_API_KEY

# 2. 确保数据库文件存在（首次运行）
touch daily_quotes.db

# 3. 启动完整服务
docker compose -f docker-compose.full.yml up -d

# 4. 访问服务
open http://localhost:6001
```

**访问地址：**
- 前端页面：http://localhost:6001
- API服务：http://localhost:6001/api/
- API文档：http://localhost:6001/docs

## 环境变量配置

在 `.env` 文件中配置以下变量：

```bash
# 必需配置
OPENAI_API_KEY=your_openai_api_key_here

# 可选配置
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
ENABLE_MANUAL_GENERATION=False
```

## 数据持久化

新的挂载方式更加实用：

- **数据库文件**：`./daily_quotes.db` 直接挂载到容器，数据持久保存
- **环境配置**：`./.env` 文件直接挂载，便于配置管理
- **优势**：
  - 可以直接在宿主机上查看和备份数据库文件
  - 可以直接修改 `.env` 文件，重启容器即可生效
  - 不需要额外的数据目录，结构更简洁
  - 容器重启后数据和配置都不会丢失

## 安全建议

1. **生产环境**：设置 `ENABLE_MANUAL_GENERATION=False`
2. **API密钥**：妥善保管 `OPENAI_API_KEY`
3. **网络安全**：建议使用反向代理和HTTPS

## 自定义前端

如果你想自定义前端，可以：

1. 使用仅API模式部署后端
2. 参考 `frontend/` 目录下的示例前端
3. 调用API接口开发自己的前端

## API接口说明

### 获取今日语录
```bash
GET /api/quote
```

### 获取指定日期语录
```bash
GET /api/quote/{date}
```

### 获取最近语录
```bash
GET /api/quotes/recent?limit=10
```

### 系统健康检查
```bash
GET /health
```

## 故障排除

### 常见问题

1. **API密钥错误**：检查 `.env` 文件中的 `OPENAI_API_KEY`
2. **端口冲突**：修改 compose 文件中的端口映射
3. **数据库问题**：删除 `./daily_quotes.db` 文件重新初始化

### 查看日志

```bash
# 查看API服务日志
docker logs daily-quote-api

# 查看完整服务日志
docker compose -f docker-compose.full.yml logs
```

## 开发模式

如果需要开发模式，可以直接运行：

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OPENAI_API_KEY

# 2. 后端开发
python start.py

# 3. 前端开发（可选）
# 方式一：直接打开 frontend/index.html
# 方式二：使用HTTP服务器
cd frontend
python -m http.server 8080
```
