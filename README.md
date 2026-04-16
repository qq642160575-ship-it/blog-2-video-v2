# 博文生成视频系统

AI 驱动的博文转视频系统，将技术文章自动转换为短视频。

## 项目结构

```
.
├── backend/          # FastAPI 后端
├── frontend/         # React 前端
├── doc/             # 文档
│   ├── 产品/        # PRD
│   ├── 技术/        # Tech Spec
│   └── 程序员/      # 开发任务列表
└── docker-compose.yml
```

## 快速开始

### 1. 启动基础服务（PostgreSQL + Redis）

```bash
docker-compose up -d
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库和 API keys
uvicorn app.main:app --reload
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 开发进度

按照 `doc/程序员/out_3.md` 中的任务列表顺序开发。

当前进度：Step 1 - 项目初始化和环境搭建 ✅
