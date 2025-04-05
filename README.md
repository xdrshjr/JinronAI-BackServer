# Next.js 后端 API 服务

这是一个基于 Flask 的后端 API 服务，为 Next.js 前端应用提供支持。

## 功能特点

- 使用 Flask 框架构建的 RESTful API
- JWT 认证和授权
- 支持多种环境配置
- 模块化设计，易于扩展
- Agent 模式支持，可以方便地添加新的 Agent 服务
- SQLAlchemy ORM 数据库访问
- 错误处理和日志记录
- MCP（Model Context Protocol）服务支持，提供天气查询功能

## 项目结构

```
app/
  ├── api/               # API 路由模块
  │   └── v1/            # V1 版本 API
  ├── core/              # 核心功能模块
  ├── models/            # 数据模型
  ├── schemas/           # 序列化模式
  ├── services/          # 业务服务层
  ├── utils/             # 工具函数
  ├── config/            # 配置模块
  ├── agents/            # Agent 实现
  └── tests/             # 测试模块
```

## 安装和运行

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 初始化数据库

```bash
flask db init
flask db migrate
flask db upgrade
```

### 运行开发服务器

```bash
python run.py
```

或者

```bash
flask run
```

## API 文档

API 主要包括以下几个模块：

1. 认证 API
   - 登录: POST /api/v1/auth/login
   - 刷新 Token: POST /api/v1/auth/refresh
   - 获取用户信息: GET /api/v1/auth/profile

2. Agent API
   - 获取可用 Agent 列表: GET /api/v1/agents
   - 使用 Agent 处理请求: POST /api/v1/agents/process

## 添加新的 Agent

添加新的 Agent 非常简单：

1. 在 `app/agents/` 目录下创建一个新的 Agent 类，继承 `BaseAgent`
2. 实现 `process` 方法
3. 在 `app/agents/agent_factory.py` 的 `AGENT_TYPES` 字典中注册新的 Agent

## 部署

### 使用 Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### 使用 Docker (可选)

```bash
docker build -t nextjs-backend .
docker run -p 5000:5000 nextjs-backend
``` 