# 后端开发指南

## 环境准备

### 1. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等
```

### 3. 初始化数据库

确保 PostgreSQL 正在运行，然后：

```bash
# 方式1：使用脚本直接创建表
python scripts/init_db.py

# 方式2：使用 Alembic 迁移
alembic upgrade head
```

## 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 测试 API

```bash
# 测试项目创建和查询
python scripts/test_api.py
```

## 当前进度

- ✅ Step 1: 项目初始化和环境搭建
- ✅ Step 2: 数据库表创建（最小集合）
- ✅ Step 3: 第一个 API - 创建项目
- ⏳ Step 4: Redis + 任务队列基础

## 项目结构

```
backend/
├── app/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置（数据库、Redis）
│   ├── models/       # SQLAlchemy 模型
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # 业务逻辑
│   ├── repositories/ # 数据访问层
│   ├── workers/      # 异步 Worker
│   ├── graph/        # LangGraph 状态机
│   └── utils/        # 工具函数
├── scripts/          # 脚本
├── alembic/          # 数据库迁移
└── requirements.txt
```
