# 博文生成视频系统 - 单人开发任务列表

## 核心原则
- 按"最快看到结果"的顺序执行
- 每一步都能验证（可运行/可测试）
- 先 Mock 打通，再替换真实实现

---

# 1. 开发主链路（按时间顺序）

## Step 1：项目初始化和环境搭建
**做什么：**
- 创建后端目录结构（按 Tech Spec 第10节）
- 创建前端目录结构（React + Remotion）
- 配置 Python 依赖（FastAPI、SQLAlchemy、Redis、LangChain）
- 配置 Node.js 依赖（Remotion、React）
- 配置 PostgreSQL 和 Redis 连接

**产出：**
- 可运行的空项目骨架
- 依赖安装完成

**验证方式：**
```bash
# 后端能启动
uvicorn app.main:app --reload

# 前端能启动
npm run dev
```

---

## Step 2：数据库表创建（最小集合）
**做什么：**
- 创建 3 个核心表：`projects`、`generation_jobs`、`scenes`
- 创建对应的 SQLAlchemy Model
- 编写数据库迁移脚本

**产出：**
- `models/project.py`
- `models/generation_job.py`
- `models/scene.py`
- 数据库表创建成功

**验证方式：**
```bash
# 运行迁移
alembic upgrade head

# 检查表是否创建
psql -d your_db -c "\dt"
```

---

## Step 3：第一个 API - 创建项目
**做什么：**
- 实现 `POST /projects`
- 实现 `GET /projects/{project_id}`
- 实现基础的字数统计和校验

**产出：**
- `api/projects.py`
- `services/project_service.py`
- `repositories/project_repo.py`

**验证方式：**
```bash
# 创建项目
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"测试文章","source_type":"text","content":"这是一篇测试文章..."}'

# 查询项目
curl http://localhost:8000/projects/{project_id}
```

---

## Step 4：Redis + 任务队列基础
**做什么：**
- 配置 Redis 连接
- 实现简单的任务发布函数
- 实现简单的任务消费函数（先只打印日志）

**产出：**
- `core/redis.py`
- `services/job_service.py`（任务发布）
- `workers/pipeline_worker.py`（任务消费框架）

**验证方式：**
```python
# 在 Python shell 中测试
from app.core.redis import redis_client
redis_client.lpush("test_queue", "hello")
print(redis_client.rpop("test_queue"))  # 输出: hello
```

---

## Step 5：创建生成任务 API
**做什么：**
- 实现 `POST /projects/{project_id}/jobs/generate`
- 创建 `generation_job` 记录
- 将任务推送到 Redis 队列

**产出：**
- `api/jobs.py`
- Job 创建逻辑

**验证方式：**
```bash
# 创建生成任务
curl -X POST http://localhost:8000/projects/{project_id}/jobs/generate

# 检查 Redis 队列
redis-cli LLEN generation_queue
```

---

## Step 6：查询任务状态 API
**做什么：**
- 实现 `GET /jobs/{job_id}`
- 返回任务状态、阶段、进度

**产出：**
- Job 查询接口

**验证方式：**
```bash
curl http://localhost:8000/jobs/{job_id}
# 应返回: {"job_id":"xxx","status":"queued",...}
```

---

## Step 7：Pipeline Worker 消费任务（Mock 版本）
**做什么：**
- Worker 从队列取任务
- 执行 Mock 的文章解析（返回固定 JSON）
- 执行 Mock 的分镜生成（返回 3 个固定 Scene）
- 更新 Job 状态为 `completed`

**产出：**
- `workers/pipeline_worker.py` 完整逻辑
- Mock 数据生成函数

**验证方式：**
```bash
# 启动 worker
python scripts/run_worker.py

# 提交任务后，检查 job 状态变为 completed
# 检查数据库中是否有 scenes 记录
```

---

## Step 8：创建最简单的 Remotion 模板
**做什么：**
- 初始化 Remotion 项目
- 创建一个 `hook_title` 模板（只显示标题和副标题文字）
- 不加音频、不加字幕，只验证能渲染

**产出：**
- `remotion/src/compositions/HookTitle.tsx`
- 可手动渲染的视频

**验证方式：**
```bash
# 手动渲染测试
npx remotion render src/index.ts HookTitle out/test.mp4
```

---

## Step 9：Render Worker 基础框架
**做什么：**
- 创建 Node.js 渲染进程
- 从 Redis 队列接收渲染任务
- 调用 Remotion CLI 渲染
- 保存 MP4 文件到本地

**产出：**
- `render-worker/index.js`
- 渲染任务消费逻辑

**验证方式：**
```bash
# 启动 render worker
node render-worker/index.js

# 手动推送渲染任务到队列
# 检查是否生成 MP4 文件
```

---

## Step 10：打通端到端 Mock 流程
**做什么：**
- Pipeline Worker 完成后，推送渲染任务到 Render Worker
- Render Worker 渲染完成后，更新 Job 状态
- 实现 `GET /projects/{project_id}/result` 返回视频 URL

**产出：**
- 完整的端到端流程（虽然是 Mock 数据）

**验证方式：**
```bash
# 1. 创建项目
# 2. 启动生成任务
# 3. 等待 10 秒
# 4. 查询结果，应该能拿到视频 URL
# 5. 打开视频，能看到画面（虽然内容是固定的）
```

**🎉 里程碑：第一个视频生成成功！**

---

## Step 11：接入真实 LLM - 文章解析
**做什么：**
- 实现 `ArticleAnalysis` Pydantic Schema
- 编写文章解析 Prompt
- 使用 LangChain 调用 OpenAI GPT-4
- 实现 JSON Schema 校验和重试

**产出：**
- `services/article_parse_service.py`
- `schemas/article_analysis.py`

**验证方式：**
```python
# 输入真实文章，检查返回的 ArticleAnalysis
# 应包含: topic, audience, core_message, key_points 等
```

---

## Step 12：接入真实 LLM - 分镜生成
**做什么：**
- 实现 `SceneSpec` Pydantic Schema
- 编写分镜生成 Prompt
- 调用 LLM 生成 6-10 个 Scene
- 保存到数据库

**产出：**
- `services/scene_generate_service.py`
- `schemas/scene_spec.py`

**验证方式：**
```python
# 输入 ArticleAnalysis，检查生成的 Scene 列表
# 每个 Scene 应包含: voiceover, screen_text, template_type 等
```

---

## Step 13：实现 Scene 规则校验器
**做什么：**
- 校验 Scene 数量（6-10）
- 校验单个 Scene 时长（4-9秒）
- 校验总时长（45-60秒）
- 校验 voiceover 长度（≤90字符）
- 校验 screen_text 数量和长度

**产出：**
- `services/scene_validate_service.py`

**验证方式：**
```python
# 输入不合规的 Scene，应返回错误列表
# 输入合规的 Scene，应返回 ok=True
```

---

## Step 14：接入真实 TTS
**做什么：**
- 接入 Azure Speech 或其他 TTS
- 为每个 Scene 生成音频文件
- 保存到本地文件系统
- 记录音频时长

**产出：**
- `services/tts_service.py`
- 音频文件（MP3）

**验证方式：**
```bash
# 检查生成的音频文件
ls assets/audio/
# 播放音频，确认内容正确
```

---

## Step 15：实现字幕生成
**做什么：**
- 基于 TTS 时间戳或字符估算
- 按标点切句
- 生成 SRT 格式字幕

**产出：**
- `services/subtitle_service.py`
- `utils/subtitle_splitter.py`
- 字幕文件（SRT）

**验证方式：**
```bash
# 检查生成的字幕文件
cat assets/subtitles/proj_001.srt
# 格式应符合 SRT 标准
```

---

## Step 16：完善 Remotion 模板（加音频和字幕）
**做什么：**
- 修改 `HookTitle` 模板，支持音频和字幕
- 实现字幕显示组件
- 实现音频同步

**产出：**
- 完整的 `HookTitle` 模板
- 字幕组件

**验证方式：**
```bash
# 渲染带音频和字幕的视频
# 播放视频，确认声音和字幕同步
```

---

## Step 17：实现另外两个模板
**做什么：**
- 实现 `bullet_explain` 模板（要点列表）
- 实现 `compare_process` 模板（对比/流程）
- 实现模板映射逻辑

**产出：**
- `remotion/src/compositions/BulletExplain.tsx`
- `remotion/src/compositions/CompareProcess.tsx`
- `services/template_mapping_service.py`

**验证方式：**
```bash
# 手动渲染三种模板，确认样式正确
```

---

## Step 18：端到端真实流程测试
**做什么：**
- 输入真实文章
- 走完整流程：解析 → 分镜 → TTS → 字幕 → 渲染
- 生成真实视频

**产出：**
- 第一个真实视频成果

**验证方式：**
```bash
# 提交一篇真实技术文章
# 等待 10 分钟
# 下载视频，检查质量
```

**🎉 里程碑：真实 AI 生成的视频！**

---

## Step 19：实现 Scene 编辑 API
**做什么：**
- 实现 `GET /projects/{project_id}/scenes`
- 实现 `PATCH /scenes/{scene_id}`
- 实现版本控制（scene_versions 表）
- 实现编辑时的规则校验

**产出：**
- `api/scenes.py`
- Scene 编辑逻辑

**验证方式：**
```bash
# 修改某个 Scene 的 voiceover
curl -X PATCH http://localhost:8000/scenes/{scene_id} \
  -d '{"voiceover":"新的旁白","version":1}'

# 查询 Scene，确认版本号变为 2
```

---

## Step 20：实现重渲染功能
**做什么：**
- 实现 `POST /projects/{project_id}/jobs/rerender`
- 读取最新 Scene 版本
- 对修改的 Scene 重新生成 TTS
- 重新生成字幕和时间轴
- 整片重新渲染

**产出：**
- 重渲染逻辑

**验证方式：**
```bash
# 1. 编辑 Scene
# 2. 触发重渲染
# 3. 等待完成
# 4. 下载新视频，确认修改生效
```

---

## Step 21：前端 - 文章输入页
**做什么：**
- 创建表单组件（标题、正文、source_type）
- 调用 `POST /projects`
- 显示字数统计

**产出：**
- `pages/CreateProject.tsx`

**验证方式：**
- 在浏览器中提交文章，能创建项目

---

## Step 22：前端 - 生成中页
**做什么：**
- 调用 `POST /jobs/generate`
- 轮询 `GET /jobs/{job_id}`（每 2 秒）
- 显示当前阶段和进度条
- 显示错误信息

**产出：**
- `pages/GenerationProgress.tsx`

**验证方式：**
- 能看到实时进度更新

---

## Step 23：前端 - 结果预览页
**做什么：**
- 调用 `GET /projects/{project_id}/result`
- 显示视频播放器
- 调用 `GET /projects/{project_id}/scenes`
- 显示 Scene 列表

**产出：**
- `pages/Result.tsx`
- 视频播放组件

**验证方式：**
- 能播放视频，能看到 Scene 列表

---

## Step 24：前端 - Scene 编辑页
**做什么：**
- 创建编辑表单
- 调用 `PATCH /scenes/{scene_id}`
- 触发重渲染按钮
- 显示重渲染进度

**产出：**
- `pages/EditScene.tsx`

**验证方式：**
- 能编辑 Scene，能触发重渲染，能看到新视频

---

## Step 25：引入 LangGraph 状态机（重构）
**做什么：**
- 将 Pipeline Worker 改造为 LangGraph
- 定义 `GenerationState`
- 实现状态节点和路由规则

**产出：**
- `graph/generation_graph.py`
- `graph/generation_state.py`

**验证方式：**
- 流程仍然正常，但代码更清晰

---

## Step 26：完善错误处理和日志
**做什么：**
- 创建 `job_logs` 表
- 每个阶段记录日志
- 实现错误码和错误信息
- 实现重试逻辑

**产出：**
- `models/job_log.py`
- 完善的错误处理

**验证方式：**
- 故意输入错误数据，检查日志记录

---

## Step 27：并发控制和任务管理
**做什么：**
- 限制全局渲染并发为 3
- 实现任务取消逻辑
- 防止同一项目多任务冲突

**产出：**
- 并发控制逻辑

**验证方式：**
- 同时提交 5 个任务，确认只有 3 个在运行

---

## Step 28：资产管理和存储
**做什么：**
- 创建 `assets` 表
- 记录所有音频、字幕、视频元数据
- 实现文件清理逻辑

**产出：**
- `models/asset.py`
- 资产管理逻辑

**验证方式：**
- 检查数据库，所有文件都有记录

---

## Step 29：端到端测试和修复
**做什么：**
- 测试各种边界情况
- 修复发现的 bug
- 优化性能

**产出：**
- 稳定的 MVP 系统

**验证方式：**
- 连续生成 10 个视频，成功率 > 80%

---

# 2. 数据结构优先定义

在 Step 2 之前，先定义核心数据结构：

## `Project`
```python
class Project(Base):
    id: str  # proj_xxx
    title: str
    source_type: str  # text / markdown
    content: str
    char_count: int
    status: str  # draft / generated / failed
    created_at: datetime
```

## `SceneSpec`
```python
class SceneSpec(BaseModel):
    scene_id: str
    order: int
    template_type: str  # hook_title / bullet_explain / compare_process
    goal: str
    voiceover: str  # ≤90 字符
    screen_text: List[str]  # ≤3 条，每条 ≤18 字符
    duration_sec: int  # 4-9
    pace: str
    transition: str
    visual_params: dict
```

## `GenerationJob`
```python
class GenerationJob(Base):
    id: str  # job_xxx
    project_id: str
    job_type: str  # generate / rerender
    status: str  # queued / running / failed / completed
    stage: str  # article_parse / scene_generate / ...
    progress: float  # 0-1
    error_code: str
    error_message: str
```

---

# 3. 接口开发顺序

1. `POST /projects` - Step 3
2. `GET /projects/{id}` - Step 3
3. `POST /projects/{id}/jobs/generate` - Step 5
4. `GET /jobs/{id}` - Step 6
5. `GET /projects/{id}/result` - Step 10
6. `GET /projects/{id}/scenes` - Step 19
7. `PATCH /scenes/{id}` - Step 19
8. `POST /projects/{id}/jobs/rerender` - Step 20

---

# 4. AI 集成步骤

## Mock 阶段（Step 7）
- 返回固定的 `ArticleAnalysis` JSON
- 返回固定的 3 个 `SceneSpec`

## 真实调用阶段（Step 11-12）
- 替换为 LangChain + OpenAI
- 实现 Schema 校验
- 实现重试逻辑

## 失败处理（Step 13）
- 规则校验失败 → 让 LLM 修复一次
- 仍失败 → 终止任务，返回错误

---

# 5. 延后事项（刻意不做）

以下功能在 MVP 阶段不实现：

- ❌ 文章链接输入和抓取
- ❌ 5-8 个模板（只做 3 个）
- ❌ Scene 局部重生成（只做整片重渲染）
- ❌ 多 TTS 供应商抽象
- ❌ 字级精准字幕（只做句级）
- ❌ 横屏视频
- ❌ 多平台适配
- ❌ 批量处理 UI
- ❌ 数据看板
- ❌ 素材混剪

**原因：** 避免分心，专注核心链路验证。

---

# 关键里程碑

- ✅ **里程碑 1**（Step 10）：第一个 Mock 视频生成成功
- ✅ **里程碑 2**（Step 18）：第一个真实 AI 视频生成成功
- ✅ **里程碑 3**（Step 24）：前端完整流程打通
- ✅ **里程碑 4**（Step 29）：MVP 可交付

---

这份任务列表严格按照"最快看到结果"的原则排序，每一步都可以验证，不会卡住。建议严格按顺序执行，不要跳步。
