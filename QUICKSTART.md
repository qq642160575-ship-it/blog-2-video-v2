# 快速开始指南

## ✅ 环境已配置完成

- Python 虚拟环境：已创建
- 依赖包：已安装
- 数据库：SQLite（已初始化）
- Redis：正在运行

## 🚀 启动服务

### 方式 1：手动启动（推荐用于开发）

**终端 1 - 启动后端：**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 方式 2：一键启动
```bash
./run.sh
```

## 🧪 测试 API

**终端 3 - 运行测试：**
```bash
cd backend
source venv/bin/activate

# 测试 Redis 连接
python scripts/test_redis.py

# 测试完整 API 流程
python scripts/test_flow.py
```

## 📍 访问地址

- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs （Swagger UI）
- **前端页面**: http://localhost:3000

## 🔍 测试步骤

1. 访问 http://localhost:8000/docs
2. 测试 `POST /projects` - 创建项目
3. 测试 `POST /projects/{id}/jobs/generate` - 创建生成任务
4. 测试 `GET /jobs/{id}` - 查询任务状态

## 📊 当前进度

- ✅ Step 1-6: 基础架构完成
- ⏳ Step 7: Pipeline Worker（下一步）
- ⏳ Step 8-10: 视频生成流程

## 🐛 常见问题

### Redis 连接失败
```bash
# 启动 Redis
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 端口被占用
修改端口：
- 后端：`uvicorn app.main:app --reload --port 8001`
- 前端：修改 `frontend/vite.config.js` 中的 `port`

## 📝 数据库文件

SQLite 数据库文件位置：`backend/blog_video.db`

如需重置数据库：
```bash
cd backend
rm blog_video.db
python scripts/init_db.py
```
