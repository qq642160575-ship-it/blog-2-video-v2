# 博文生成视频系统

一个将博文自动拆解、生成分镜、合成语音与字幕，并最终渲染为短视频的多模块项目。

## 项目约定（强制）

- 任何功能、架构、写法的变更，必须在当次工作结束后同步更新对应目录的 `README.md`
- 文档不是说明书，而是系统的一部分；文档落后于代码，等于系统已经不一致
- 本项目采用分形自指结构：根目录约束全局，子目录约束局部，文件头注释约束单文件

当前仓库已经包含：

- `backend/`：FastAPI API、任务调度、LangGraph 生成流程、数据库模型
- `frontend/`：React + Vite 前端，覆盖创建项目、生成进度、结果页、分镜编辑
- `render-worker/`：独立渲染 Worker，消费 Redis 渲染队列并调用 Remotion/FFmpeg
- `remotion/`：视频模板与合成逻辑
- `doc/`：产品、技术和研发任务文档

## 核心能力

- 输入文章标题和正文，创建视频生成项目
- 后端异步执行文章解析、分镜生成、音频生成、字幕生成、清单产出
- 前端查看任务进度、结果页和分镜编辑页面
- 渲染 Worker 调用 Remotion 模板生成场景视频并拼接为最终 MP4
- 通过 `/storage` 暴露生成后的音频、字幕、manifest 和视频文件

## 技术栈

- 后端：FastAPI、SQLAlchemy、Alembic、Redis、LangGraph
- 前端：React、React Router、Vite、Axios
- 渲染：Remotion、Node.js、FFmpeg
- 基础设施：PostgreSQL、Redis、Docker Compose

## 项目结构

```text
.
├── backend/                # API、任务处理、数据模型、脚本
├── frontend/               # Web 前端
├── render-worker/          # 渲染任务消费者
├── remotion/               # 视频模板
├── doc/                    # 产品/技术/开发文档
├── docker-compose.yml      # PostgreSQL + Redis
├── run.sh                  # 一键启动前后端
├── setup.sh                # 环境初始化脚本
└── QUICKSTART.md           # 较早期的快速开始说明
```

## 运行依赖

本项目本地开发至少需要：

- Python 3.11 或兼容版本
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- FFmpeg

如果只想先启动基础依赖，可以直接使用 Docker：

```bash
docker-compose up -d
```

这会启动：

- PostgreSQL：`localhost:5432`
- Redis：`localhost:6379`

## 环境变量

后端读取 `backend/.env`，可从示例文件复制：

```bash
cd backend
cp .env.example .env
```

关键变量如下：

```env
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/blog_video_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus
STORAGE_PATH=./storage
```

说明：

- `DATABASE_URL` 和 `REDIS_URL` 需要与本地服务保持一致
- `OPENAI_API_KEY` 用于文章解析/分镜生成等 AI 流程
- `AZURE_SPEECH_*` 当前示例文件提供占位配置；实际语音能力请按后端服务实现和你使用的供应商配置
- `STORAGE_PATH` 默认指向 `backend/storage`

## 本地开发启动

推荐按下面顺序启动。

### 1. 启动基础服务

```bash
docker-compose up -d
```

### 2. 启动后端 API

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

后端地址：

- API：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

- `http://localhost:3000`

### 4. 启动生成流程 Worker

生成任务不是在 API 进程中执行，开发时还需要单独启动 pipeline worker：

```bash
cd backend
source venv/bin/activate
python scripts/run_worker.py
```

这个 Worker 会消费 Redis 中的 `generation_queue`，执行文章解析、分镜、TTS、字幕和 manifest 产出流程。

### 5. 启动渲染 Worker

最终视频渲染由独立的 Node Worker 处理：

```bash
cd render-worker
npm install
node index.js
```

它会：

- 消费 Redis 中的 `render_queue`
- 调用 `remotion/` 中的模板渲染各分镜
- 使用 `ffmpeg` 拼接成最终视频
- 通过后端接口回写任务状态

### 6. 可选：启动 Remotion Studio

如果你要单独调试模板：

```bash
cd remotion
npm install
npm run start
```

## 一键启动脚本

仓库提供了两个辅助脚本：

- `start.sh`：只打印开发环境启动说明
- `run.sh`：直接启动后端和前端

注意：

- `run.sh` 不会自动启动 PostgreSQL、Redis、pipeline worker、render worker
- 如果你要验证完整的视频生成链路，仍然需要把 Worker 和基础依赖一起拉起

## API 概览

根应用注册了以下路由模块：

- `projects`
- `jobs`
- `scenes`
- `job_logs`
- `assets`
- `logs`

可直接访问 Swagger UI 查看完整接口定义：

```text
http://localhost:8000/docs
```

## 数据与产物

项目运行后，生成文件会落在 `backend/storage/` 下，通常包括：

- `audio/`
- `subtitles/`
- `manifests/`
- `videos/`

后端会在存在该目录时挂载静态资源：

- `/storage/...`

## 现状说明

从当前仓库内容看，项目已经不再是“Step 1 初始化”状态，至少已经实现了以下模块：

- 多个后端 API 路由与数据库迁移
- 基于 LangGraph 的生成流程 Worker
- 前端项目创建、进度页、结果页、分镜编辑页
- Remotion 模板：`HookTitle`、`BulletExplain`、`CompareProcess`
- 独立渲染 Worker 与视频拼接流程
- 多个阶段性测试脚本和里程碑文档

换句话说，当前 README 应该按“可运行的多进程开发项目”理解，而不是仅仅作为初始化说明。

## 常用命令

```bash
# 基础服务
docker-compose up -d

# 后端
cd backend && uvicorn app.main:app --reload --port 8000

# 生成任务 Worker
cd backend && python scripts/run_worker.py

# 前端
cd frontend && npm run dev

# 渲染 Worker
cd render-worker && node index.js

# Remotion 模板调试
cd remotion && npm run start
```

## 调试与排错

- 看不到任务执行结果时，先确认 Redis、pipeline worker、render worker 是否都已启动
- 后端能启动但接口报配置错误时，优先检查 `backend/.env`
- 渲染阶段失败时，优先检查本机是否安装 `ffmpeg`，以及 `remotion/` 依赖是否已安装
- 如果数据库表缺失，执行 `alembic upgrade head`
- 如果只启动了 `run.sh`，那只能访问前后端，完整异步链路仍然不会工作

## 日志说明

项目日志统一落在根目录 `logs/` 下，如果目录不存在会自动创建。

主要文件：

- `logs/app.log`：应用通用日志
- `logs/api.log`：FastAPI 请求访问日志
- `logs/worker.log`：pipeline worker 和任务阶段日志
- `logs/ai.log`：AI 输入输出、状态和错误日志
- `logs/error.log`：未捕获异常和严重错误

数据库日志：

- `job_logs`：按任务阶段记录流程日志
- `ai_logs`：记录重要 AI 输入输出、耗时、状态和错误

排查建议：

- 接口报错先看 `logs/api.log` 和 `logs/error.log`
- 任务卡住先看 `logs/worker.log` 和 `GET /jobs/{job_id}/logs`
- AI 结果异常先看 `logs/ai.log` 和 `GET /logs/ai?job_id=xxx`

## 相关文档

- `QUICKSTART.md`
- `backend/README.md`
- `STEP10_MILESTONE1.md`
- `doc/产品/`
- `doc/技术/`
- `doc/程序员/`
