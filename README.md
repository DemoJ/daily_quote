# 每日一言

一个专注于提供高质量哲学家名言的API服务，采用前后端分离架构，支持Docker部署。

## 功能特性

- 🎯 **纯API服务**: 专注于提供稳定的API接口
- 📚 **真实名言**: 从AI知识库提取真实哲学家语录
- 🧠 **深度思考**: 30字以上的深刻哲学思辨内容
- 🤖 **AI驱动**: 使用OpenAI兼容的LLM智能选择
- ⏰ **定时更新**: 每日23:00自动生成下一日语录
- 🔄 **重试机制**: 生成失败时自动重试3次
- 🛡️ **兜底机制**: 重试失败时从历史语录中随机选择
- 🔒 **安全控制**: 可配置的手动生成接口权限
- 🐳 **Docker支持**: 提供完整的容器化部署方案

## 架构设计

- **后端**: FastAPI + SQLite + SQLAlchemy（纯API服务）
- **前端**: 纯静态HTML/CSS/JS + Nginx（可选预览组件）
- **AI**: OpenAI SDK
- **定时任务**: APScheduler
- **部署**: Docker + Docker Compose

## 快速开始

### 方式一：Docker部署（推荐）

#### 仅API服务
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OPENAI_API_KEY

# 2. 确保数据库文件存在（首次运行）
touch daily_quotes.db

# 3. 启动API服务
docker-compose -f docker-compose.api.yml up -d

# 4. 访问API
curl http://localhost:6000/api/quote
```

#### 完整服务（包含前端预览）
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OPENAI_API_KEY

# 2. 确保数据库文件存在（首次运行）
touch daily_quotes.db

# 3. 启动完整服务
docker-compose -f docker-compose.full.yml up -d

# 4. 访问前端
open http://localhost:6001
```

### 方式二：本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key

# 3. 启动后端API
python start.py

# 4. 访问服务
# API: http://localhost:8000
# 文档: http://localhost:8000/docs
# 前端: 直接打开 frontend/index.html
```

## API接口

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

### 返回格式示例
```json
{
  "success": true,
  "data": {
    "id": 1,
    "content": "有两样东西，人们越是经常持久地对之凝神思索，它们就越是使内心充满常新而日增的惊奇和敬畏：我头上的星空和我心中的道德律。",
    "author": "伊曼努尔·康德",
    "date": "2025-07-03",
    "created_at": "2025-07-03T06:29:27",
    "is_ai_generated": true,
    "is_fallback": false
  },
  "message": "获取成功"
}
```

## 项目结构

```
.
├── main.py                    # 后端API应用入口
├── start.py                   # 开发启动脚本
├── app/                       # 后端核心代码
│   ├── __init__.py
│   ├── database.py           # 数据库配置
│   ├── models.py             # 数据模型
│   ├── api.py               # API路由
│   ├── ai_service.py        # AI语录生成服务
│   └── scheduler.py         # 定时任务
├── frontend/                 # 前端静态文件（可选）
│   ├── index.html           # 前端页面
│   ├── js/
│   │   └── app.js          # 前端逻辑
│   ├── nginx.conf          # Nginx配置
│   └── Dockerfile          # 前端Docker配置
├── Dockerfile               # 后端Docker配置
├── docker-entrypoint.sh     # Docker启动脚本
├── docker-compose.api.yml   # 仅API服务
├── docker-compose.full.yml  # 完整服务（含前端）
├── requirements.txt         # Python依赖
├── .env                     # 环境变量配置
├── .env.example            # 环境变量模板
├── daily_quotes.db         # SQLite数据库文件
├── DEPLOYMENT.md          # 部署指南
├── SECURITY.md           # 安全配置说明
└── README.md            # 项目说明
```

## 特色功能

### 🧠 真实哲学家名言
系统从AI知识库中提取真实的哲学家名言

### 📏 深度思考内容
- 最低30字以上的完整思想表达
- 避免简短格言，注重哲学思辨
- 具有启发性和思考价值

### 🔒 安全配置
- 可通过环境变量控制手动生成接口
- 适合公开API部署
- 防止接口滥用

### 🐳 灵活部署
- **仅API模式**：适合开源分发，用户可自行开发前端
- **完整模式**：包含美观的前端预览页面
- **Docker支持**：一键部署，环境隔离

## 使用场景

1. **API服务提供商**：部署仅API模式，为其他应用提供语录服务
2. **个人博客/网站**：集成API获取每日语录
3. **移动应用**：调用API为APP提供内容
4. **企业内部系统**：部署完整模式，提供内部使用的语录系统

## 详细文档

- [部署指南](DEPLOYMENT.md) - 详细的Docker部署说明
- [安全配置](SECURITY.md) - 安全相关的配置说明
- [API文档](http://localhost:8000/docs) - 在线API文档（启动后访问）

## 开源协议

MIT License - 欢迎贡献代码和提出建议！
