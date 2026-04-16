# 1. 技术目标

本系统只解决一个问题：

- 用户提交一篇 `text` 或 `markdown` 文章，系统在 10 分钟内生成一条 45 到 60 秒、`1080x1920`、`30fps`、带配音和字幕的 MP4 初版视频。

系统必须支撑的能力：

- 创建项目并保存原文
- 异步执行文章解析、分镜生成、规则校验、TTS、字幕、视频渲染
- 返回任务状态和错误信息
- 允许用户编辑 Scene 后重新整片渲染
- 保存中间产物，支持排错和回滚

非功能需求：

- 单任务端到端生成时间目标：`<= 10 分钟`
- 单个任务失败后必须可定位到具体阶段
- Job 不允许无限卡在 `running`
- 单实例支持至少 `3` 个并发渲染任务，超出进入队列
- 所有结构化结果必须可校验，不接受自由文本直接进入渲染

明确边界：

- 不做文章链接抓取
- 不做批量生成 UI
- 不做 Scene 局部重生成
- 不做多 TTS 供应商抽象
- 不做 LLM 生成前端代码

---

# 2. 系统整体架构

架构类型：

- `模块化单体 + 异步 Worker`

原因：

- 当前是 MVP，模块边界要清楚，但没有必要拆成微服务。
- 真正重任务只有渲染和生成流水线，拆成独立 Worker 进程即可。
- 如果现在上微服务，程序员很容易把时间浪费在服务治理、RPC、部署编排，而不是成片质量。

核心服务列表：

## 1. `web-app`

- 职责：React 前端，提供文章输入、Scene 编辑、任务状态轮询、视频预览
- 技术：React + Remotion Player

## 2. `api-server`

- 职责：FastAPI 主服务，提供项目 API、Scene API、Job API、结果查询 API
- 技术：FastAPI

## 3. `pipeline-worker`

- 职责：执行文章解析、分镜生成、规则校验、TTS、字幕生成、渲染前准备
- 技术：FastAPI 同仓库下独立 worker 进程 + LangChain / LangGraph

## 4. `render-worker`

- 职责：执行 Remotion 渲染，产出 MP4、SRT、Scene JSON
- 技术：Node.js + Remotion CLI

## 5. `postgres`

- 职责：保存项目、Scene、Job、版本、日志、产物元数据

## 6. `redis`

- 职责：任务队列、短期状态缓存、幂等锁

## 7. `object-storage`

- 职责：保存音频、字幕、视频、Scene JSON、原始日志
- MVP 可先用本地文件系统目录，接口层按对象存储方式设计

职责边界说明：

- `api-server` 不直接做耗时生成，只负责写库、发任务、查状态
- `pipeline-worker` 不直接渲染视频，只负责生成结构化资产
- `render-worker` 不调用 LLM，只消费固定 JSON 输入做渲染

---

# 3. 核心模块设计

## 模块名：Project API

- 职责：
  - 创建项目
  - 保存文章原文
  - 返回基础统计信息
- 输入（Input）：

```json
{
  "title": "什么是 RAG",
  "source_type": "markdown",
  "content": "# 什么是 RAG\n\nRAG 是..."
}
```

- 输出（Output）：

```json
{
  "project_id": "proj_001",
  "status": "created",
  "article_stats": {
    "char_count": 2140,
    "estimated_reading_sec": 320
  }
}
```

- 内部逻辑（简要流程）：
  1. 校验 `source_type`
  2. 统计字数
  3. 校验长度范围
  4. 保存原文和元数据
  5. 初始化 `project` 记录
- 依赖：
  - PostgreSQL
  - 内容长度校验器

## 模块名：Generation Job API

- 职责：
  - 启动生成任务
  - 启动重渲染任务
  - 查询任务状态
  - 取消旧任务
- 输入（Input）：

```json
{
  "project_id": "proj_001",
  "trigger_type": "initial_generate"
}
```

- 输出（Output）：

```json
{
  "job_id": "job_001",
  "status": "queued"
}
```

- 内部逻辑（简要流程）：
  1. 检查项目是否存在
  2. 检查是否已有运行中任务
  3. 如有旧任务则标记 `cancelled`
  4. 创建 `generation_job`
  5. 推送队列
- 依赖：
  - PostgreSQL
  - Redis

## 模块名：Article Parse Module

- 职责：
  - 将文章转换为 `ArticleAnalysis`
- 输入（Input）：
  - `project_id`
  - 原文内容
- 输出（Output）：

```json
{
  "topic": "RAG 基础概念",
  "audience": "对大模型应用有基础认知的技术读者",
  "core_message": "RAG 的核心价值在于解决知识更新和引用可信问题",
  "key_points": ["知识更新", "可信引用"],
  "visualizable_points": ["知识库更新", "答案引用来源"],
  "discarded_parts": ["背景铺垫"],
  "content_type": "tutorial",
  "confidence": 0.86
}
```

- 内部逻辑（简要流程）：
  1. 构造固定 Prompt
  2. 调用 LangChain LLM
  3. 解析结构化 JSON
  4. 进行 Schema 校验
  5. 失败则重试一次
  6. 成功后落库
- 依赖：
  - LangChain
  - 拟定 LLM：`OpenAI GPT-4.1`
  - Pydantic Schema

## 模块名：Scene Generate Module

- 职责：
  - 根据 `ArticleAnalysis` 生成 `SceneSpec[]`
- 输入（Input）：
  - `project_id`
  - `ArticleAnalysis`
  - 目标时长 `45-60 sec`
- 输出（Output）：

```json
[
  {
    "scene_id": "sc_001",
    "order": 1,
    "template_type": "hook_title",
    "goal": "开头钩子",
    "voiceover": "你以为 RAG 只是知识库？其实它解决的是知识更新和引用可信。",
    "screen_text": ["RAG 不只是知识库", "它解决引用可信"],
    "duration_sec": 6,
    "pace": "fast",
    "transition": "cut",
    "visual_params": {
      "emphasis": "RAG"
    }
  }
]
```

- 内部逻辑（简要流程）：
  1. 读取文章解析结果
  2. 让 LLM 输出 `SceneSpec[]`
  3. 执行规则校验
  4. 校验失败时生成修复提示并重试一次
  5. 成功后保存 Scene 版本 `v1`
- 依赖：
  - LangChain / LangGraph
  - Pydantic Schema
  - Scene Rule Validator

## 模块名：Scene Rule Validator

- 职责：
  - 对 Scene 做硬规则校验
- 输入（Input）：
  - `SceneSpec[]`
- 输出（Output）：

```json
{
  "ok": true,
  "errors": [],
  "warnings": []
}
```

- 内部逻辑（简要流程）：
  1. 校验 Scene 数是否在 `6-10`
  2. 校验 `template_type` 是否在允许集合
  3. 校验 `voiceover` 长度、`screen_text` 数量和长度
  4. 校验 `duration_sec` 是否在 `4-9`
  5. 计算总时长是否在 `45-60`
- 依赖：
  - 本地规则函数

## 模块名：Template Mapping Module

- 职责：
  - 将 `SceneSpec` 转为 Remotion 模板 props
- 输入（Input）：
  - `SceneSpec[]`
- 输出（Output）：

```json
[
  {
    "scene_id": "sc_001",
    "template_type": "hook_title",
    "template_props": {
      "title": "RAG 不只是知识库",
      "subtitle": "它解决引用可信",
      "emphasis": "RAG"
    }
  }
]
```

- 内部逻辑（简要流程）：
  1. 按模板类型选择对应 mapper
  2. 校验模板参数 Schema
  3. 缺少字段时做有限补全
  4. 无法补全则报错
- 依赖：
  - 模板参数 Schema

## 模块名：TTS Module

- 职责：
  - 为每个 Scene 生成音频
- 输入（Input）：

```json
{
  "scene_id": "sc_001",
  "text": "你以为 RAG 只是知识库？其实它解决的是知识更新和引用可信。",
  "voice_id": "zh-CN-XiaoxiaoNeural",
  "speed": 1.08
}
```

- 输出（Output）：

```json
{
  "scene_id": "sc_001",
  "audio_url": "/assets/audio/sc_001.mp3",
  "duration_ms": 5820,
  "timestamps": []
}
```

- 内部逻辑（简要流程）：
  1. 按 Scene 顺序生成音频
  2. 保存音频文件
  3. 记录时长
  4. 若供应商返回时间戳则保存
  5. 更新 Scene 实际时长
- 依赖：
  - 拟定 TTS：`Azure Speech`
  - 对象存储

## 模块名：Subtitle Module

- 职责：
  - 基于最终旁白和 TTS 结果生成字幕
- 输入（Input）：
  - Scene 最终旁白
  - TTS 时间戳或字符估算信息
- 输出（Output）：

```json
[
  {
    "cue_id": "sub_001",
    "scene_id": "sc_001",
    "start_ms": 0,
    "end_ms": 1800,
    "text": "RAG 不只是知识库。"
  }
]
```

- 内部逻辑（简要流程）：
  1. 优先读取 TTS 时间戳
  2. 若无时间戳则按标点切句
  3. 用字符比例估算起止时间
  4. 检查单次展示不超过两行
- 依赖：
  - TTS 结果
  - 字幕切分工具

## 模块名：Render Prepare Module

- 职责：
  - 拼装渲染所需完整输入
- 输入（Input）：
  - `SceneSpec[]`
  - `template_props[]`
  - `audio_assets[]`
  - `subtitle_cues[]`
- 输出（Output）：

```json
{
  "project_id": "proj_001",
  "resolution": "1080x1920",
  "fps": 30,
  "scenes": [],
  "subtitles": [],
  "audio_tracks": []
}
```

- 内部逻辑（简要流程）：
  1. 计算每个 Scene 的时间轴
  2. 根据音频时长重算总时长
  3. 生成渲染清单 JSON
  4. 存储到对象存储
- 依赖：
  - 时间轴计算器
  - 对象存储

## 模块名：Render Module

- 职责：
  - 使用 Remotion 生成 MP4
- 输入（Input）：
  - 渲染清单 JSON
- 输出（Output）：

```json
{
  "video_url": "/assets/video/proj_001/final.mp4",
  "subtitle_url": "/assets/video/proj_001/subtitles.srt",
  "scene_json_url": "/assets/video/proj_001/scenes.json",
  "duration_sec": 57
}
```

- 内部逻辑（简要流程）：
  1. 读取渲染清单
  2. 选择单一 Remotion Composition
  3. 传入模板 props、音频、字幕
  4. 输出 MP4 和 SRT
  5. 回写结果
- 依赖：
  - Remotion
  - Node.js
  - 对象存储

## 模块名：Scene Edit Module

- 职责：
  - 修改 Scene 并创建新版本
- 输入（Input）：

```json
{
  "scene_id": "sc_001",
  "voiceover": "很多人以为 RAG 只是知识库问答，但它真正解决的是知识更新和引用可信的问题。",
  "screen_text": ["RAG 不只是知识库问答", "它解决知识更新与引用可信"],
  "template_type": "bullet_explain",
  "duration_sec": 7,
  "version": 4
}
```

- 输出（Output）：

```json
{
  "scene_id": "sc_001",
  "version": 5,
  "validation": {
    "ok": true,
    "warnings": []
  }
}
```

- 内部逻辑（简要流程）：
  1. 检查版本号
  2. 只允许修改白名单字段
  3. 执行规则校验
  4. 保存新版本
  5. 标记项目需要重渲染
- 依赖：
  - PostgreSQL
  - Scene Rule Validator

## 模块名：Job Status Module

- 职责：
  - 返回 Job 进度、阶段和错误
- 输入（Input）：
  - `job_id`
- 输出（Output）：

```json
{
  "job_id": "job_001",
  "status": "running",
  "stage": "tts_generate",
  "progress": 0.64,
  "error": null
}
```

- 内部逻辑（简要流程）：
  1. 读取 Job 当前状态
  2. 返回阶段、进度、错误
  3. 若已完成则附带结果 URL
- 依赖：
  - PostgreSQL
  - Redis

---

# 4. 数据流设计

数据流只保留一条主链路，不做分叉工作流。

## 首次生成

1. 前端调用 `POST /projects`
2. `Project API` 保存原文并返回 `project_id`
3. 前端调用 `POST /projects/{project_id}/jobs/generate`
4. `Generation Job API` 创建 `job`
5. `pipeline-worker` 消费任务并执行：
   - `article_parse`
   - `scene_generate`
   - `scene_validate`
   - `tts_generate`
   - `subtitle_generate`
   - `render_prepare`
6. `pipeline-worker` 生成渲染清单后，创建 `render` 子任务
7. `render-worker` 执行 `remotion_render`
8. 结果写入对象存储
9. Job 标记 `completed`
10. 前端轮询 `GET /jobs/{job_id}`，获取视频 URL 和 Scene 数据

## 编辑后重渲染

1. 前端调用 `PATCH /scenes/{scene_id}`
2. 后端创建 `scene_version`
3. 前端调用 `POST /projects/{project_id}/jobs/rerender`
4. `pipeline-worker` 读取最新 Scene 版本
5. 对变更 Scene 重新生成 TTS
6. 重建字幕和时间轴
7. `render-worker` 重新整片渲染
8. 返回新视频版本

关键数据结构：

## `Project`

```json
{
  "id": "proj_001",
  "title": "什么是 RAG",
  "source_type": "markdown",
  "content": "# 什么是 RAG\n\nRAG 是...",
  "char_count": 2140,
  "status": "draft",
  "created_at": "2026-04-16T15:00:00Z"
}
```

## `ArticleAnalysis`

```json
{
  "project_id": "proj_001",
  "version": 1,
  "topic": "RAG 基础概念",
  "audience": "技术读者",
  "core_message": "RAG 解决知识更新和引用可信",
  "key_points": ["知识更新", "引用可信"],
  "visualizable_points": ["引用来源", "知识库更新"],
  "discarded_parts": ["背景铺垫"],
  "content_type": "tutorial",
  "confidence": 0.86
}
```

## `SceneSpec`

```json
{
  "scene_id": "sc_001",
  "project_id": "proj_001",
  "version": 1,
  "order": 1,
  "template_type": "hook_title",
  "goal": "开头钩子",
  "voiceover": "你以为 RAG 只是知识库？其实它解决的是知识更新和引用可信。",
  "screen_text": ["RAG 不只是知识库", "它解决引用可信"],
  "duration_sec": 6,
  "pace": "fast",
  "transition": "cut",
  "visual_params": {
    "emphasis": "RAG"
  }
}
```

## `GenerationJob`

```json
{
  "job_id": "job_001",
  "project_id": "proj_001",
  "job_type": "generate",
  "status": "running",
  "stage": "scene_generate",
  "progress": 0.3,
  "attempt": 1,
  "error_code": null,
  "error_message": null
}
```

## `RenderManifest`

```json
{
  "project_id": "proj_001",
  "resolution": "1080x1920",
  "fps": 30,
  "scenes": [
    {
      "scene_id": "sc_001",
      "start_ms": 0,
      "end_ms": 5820,
      "template_type": "hook_title",
      "template_props": {},
      "audio_url": "/assets/audio/sc_001.mp3"
    }
  ],
  "subtitles": [],
  "total_duration_ms": 57000
}
```

建议 API：

- `POST /projects`
- `GET /projects/{project_id}`
- `POST /projects/{project_id}/jobs/generate`
- `POST /projects/{project_id}/jobs/rerender`
- `GET /jobs/{job_id}`
- `GET /projects/{project_id}/scenes`
- `PATCH /scenes/{scene_id}`
- `GET /projects/{project_id}/result`

---

# 5. 关键技术选型

- 后端框架：`FastAPI`
  - 理由：Pydantic 校验强，适合结构化 JSON 和异步 API。

- LLM 编排：`LangGraph`
  - 理由：当前流水线是多阶段任务，LangGraph 比单纯链式调用更适合显式状态流转和失败重试。

- LLM 调用封装：`LangChain`
  - 理由：便于统一 Prompt、结构化输出和供应商替换。

- 前端：`React`
  - 理由：表单、轮询、Scene 编辑和预览页面足够直接。

- 视频渲染：`Remotion`
  - 理由：前端模板可复用，适合固定模板视频渲染。

- 数据库：`PostgreSQL`
  - 理由：项目、Scene 版本、Job 状态、日志都需要事务和查询能力。

- 缓存与队列：`Redis`
  - 理由：实现简单，足够支撑 MVP 的任务队列和短期状态缓存。

- 对象存储：`本地文件系统抽象层`
  - 理由：MVP 先降低部署复杂度，但接口保持对象存储风格，后续可切 S3/OSS。

- AI 调用方式：`异步`
  - 理由：LLM、TTS、渲染都不是低延迟操作，不应阻塞 API 请求。

- 拟定 LLM：`OpenAI GPT-4.1`
  - 理由：结构化输出稳定，适合摘要和 SceneSpec 生成。

- 拟定 TTS：`Azure Speech`
  - 理由：中文语音成熟，返回音频和时间戳能力较稳。

程序员约束：

- 不允许因为用了 LangGraph 就把每一步都做成独立 agent；这里只需要固定状态机。
- 不允许为了“未来扩展”引入 Kafka、微服务网关、向量数据库。

---

# 6. 异常处理机制

## AI 接口失败

- 文章解析失败：
  - 重试 1 次
  - 仍失败则 Job 标记 `failed`
  - 错误码：`ARTICLE_PARSE_FAILED`

- 分镜生成失败：
  - 原始生成失败重试 1 次
  - 规则修复失败再重试 1 次
  - 仍失败则停止，不进入 TTS
  - 错误码：`SCENE_GENERATE_FAILED`

- TTS 失败：
  - 单 Scene 重试 2 次
  - 某个 Scene 持续失败则整 Job 失败
  - 错误码：`TTS_FAILED`

## 超时

- 文章解析超时：`30s`
- 分镜生成超时：`45s`
- 单 Scene TTS 超时：`20s`
- 单次渲染超时：`8min`

超时处理：

- 当前阶段标记失败
- Job 状态改为 `failed`
- 保存阶段名、超时秒数、请求 ID

## 数据异常

- LLM 返回非 JSON：
  - 尝试 JSON 修复一次
  - 修复失败则重试模型调用

- Scene 缺字段：
  - 模板映射前强校验
  - 缺失关键字段直接拒绝

- 编辑版本冲突：
  - 返回 `409 Conflict`
  - 前端提示用户刷新最新版本

- 音频时长与建议时长偏差过大：
  - 以音频时长为准重算时间轴
  - 若总时长超出 `60s`，渲染前终止

## 重试策略

- 只对外部依赖失败重试：LLM、TTS、渲染进程
- 不对校验失败盲目无限重试
- 所有重试都必须记录 `attempt`
- 重试间隔：`2s -> 5s`

---

# 7. 性能与扩展性设计

可能的瓶颈：

- `LLM`：文章解析和分镜生成最不稳定
- `TTS`：Scene 数多时耗时线性增长
- `render-worker`：CPU 和内存消耗最高
- `PostgreSQL`：频繁写 Job 日志时可能放大压力

当前扩展方案：

- `pipeline-worker` 可多实例横向扩展，共享 Redis 队列
- `render-worker` 单独扩容，按机器 CPU 数限制并发
- `api-server` 可多实例部署，保持无状态

并发策略：

- 同一 `project_id` 同时只允许一个活跃生成任务
- 全局渲染并发默认 `3`
- 超出并发的任务进入 `queued`

存储策略：

- 大文件不入库，只存 URL 和元数据
- Job 日志按阶段写入，不记录无意义心跳

程序员约束：

- 不要为了“性能”提前做分布式锁系统，Redis 锁足够
- 不要把字幕、Scene、模板 props 全放缓存，数据库才是事实来源

---

# 8. 风险与降级方案

## 风险点 1：文章结构差，导致解析质量低

- 风险：
  - LLM 无法提炼出稳定论点
  - 后续 Scene 质量失控
- 降级方案（fallback）：
  - 若 `confidence < 0.75`，直接终止生成
  - 前端提示“文章结构不清晰，请补充论点或缩短内容”

## 风险点 2：分镜生成不符合规则

- 风险：
  - Scene 过长、文案过密、模板类型不匹配
- 降级方案（fallback）：
  - 先让 LLM 按校验错误修复一次
  - 再失败则不进入渲染，直接返回结构化错误列表

## 风险点 3：TTS 时间戳不可用

- 风险：
  - 无法做精确字幕时间轴
- 降级方案（fallback）：
  - 改为按标点切句 + 字符数估算
  - 只保证句级字幕，不做精准卡点

## 风险点 4：渲染失败

- 风险：
  - Remotion 进程崩溃
  - 字体、资源、音频异常导致导出失败
- 降级方案（fallback）：
  - 重试渲染 1 次
  - 再失败则返回 Scene JSON + 音频 + 字幕，不返回 MP4
  - 前端展示“视频导出失败，但脚本和音频已生成”

## 风险点 5：用户编辑过多，导致时间轴失衡

- 风险：
  - 修改后总时长超限
  - 字幕超屏
- 降级方案（fallback）：
  - 保存前直接拒绝
  - 返回具体哪一个 Scene 超限

## 风险点 6：产品经理继续追加非核心需求

- 风险：
  - 模板数量膨胀
  - 想提前做多平台、品牌系统、批量处理
- 降级方案（fallback）：
  - 明确 P0 冻结边界
  - 新需求只能进入 `P1 backlog`
  - 不允许插入当前开发 Sprint

## 风险点 7：程序员过度工程化

- 风险：
  - 把模块化单体做成微服务
  - 引入 Kafka、向量库、多供应商抽象
  - 把 LangGraph 用成多 agent 系统
- 降级方案（fallback）：
  - 代码仓库只允许两类后端进程：`api-server` 和 `worker`
  - 只允许一个数据库、一个 Redis、一个渲染 Worker
  - 评审时直接拒绝“未来可能需要”的复杂依赖

最终开发落地建议：

1. 先完成后端数据模型、Job 流水线和结构化 Schema。
2. 再完成 3 个固定 Remotion 模板。
3. 然后接入 TTS 和字幕。
4. 最后做前端输入、轮询、Scene 编辑和预览。

这是最短闭环路径。先把系统跑通，再谈美化和扩展。  

---

# 9. 数据库表设计

以下表足够支撑 MVP，不要继续拆表。

## 表：`projects`

- 用途：保存项目和原文

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | varchar(32) | 主键，`proj_xxx` |
| title | varchar(255) | 文章标题 |
| source_type | varchar(16) | `text` / `markdown` |
| content | text | 原文 |
| char_count | int | 字数 |
| language | varchar(16) | 默认 `zh-CN` |
| status | varchar(16) | `draft` / `generated` / `failed` |
| latest_job_id | varchar(32) | 当前最新任务 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

索引：

- `idx_projects_created_at`
- `idx_projects_latest_job_id`

## 表：`generation_jobs`

- 用途：保存任务状态和阶段

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | varchar(32) | 主键，`job_xxx` |
| project_id | varchar(32) | 关联项目 |
| job_type | varchar(16) | `generate` / `rerender` |
| status | varchar(16) | `queued` / `running` / `waiting_retry` / `failed` / `completed` / `cancelled` |
| stage | varchar(32) | 当前阶段 |
| progress | numeric(4,2) | 0 到 1 |
| attempt | int | 当前尝试次数 |
| error_code | varchar(64) | 错误码 |
| error_message | text | 错误说明 |
| result_video_url | text | 视频地址 |
| result_subtitle_url | text | 字幕地址 |
| result_scene_json_url | text | Scene JSON 地址 |
| started_at | timestamptz | 开始时间 |
| finished_at | timestamptz | 结束时间 |
| created_at | timestamptz | 创建时间 |

索引：

- `idx_generation_jobs_project_id`
- `idx_generation_jobs_status`
- `idx_generation_jobs_stage`

## 表：`article_analyses`

- 用途：保存文章解析结构化结果

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigserial | 主键 |
| project_id | varchar(32) | 关联项目 |
| version | int | 版本号 |
| topic | varchar(255) | 主题 |
| audience | text | 受众 |
| core_message | text | 核心结论 |
| key_points | jsonb | 关键论点 |
| visualizable_points | jsonb | 可视觉化信息点 |
| discarded_parts | jsonb | 丢弃内容 |
| content_type | varchar(32) | `tutorial` 等 |
| confidence | numeric(4,2) | 置信度 |
| llm_raw_output | jsonb | 原始模型输出 |
| created_at | timestamptz | 创建时间 |

索引：

- `idx_article_analyses_project_id_version`

## 表：`scenes`

- 用途：保存 Scene 当前版本快照

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | varchar(32) | 主键，`sc_xxx` |
| project_id | varchar(32) | 关联项目 |
| current_version | int | 当前版本 |
| scene_order | int | 顺序 |
| template_type | varchar(32) | 模板类型 |
| goal | text | 场景目标 |
| voiceover | text | 旁白 |
| screen_text | jsonb | 屏幕文案数组 |
| duration_sec | int | 建议时长 |
| pace | varchar(16) | 节奏 |
| transition | varchar(16) | 转场 |
| visual_params | jsonb | 可视参数 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

索引：

- `idx_scenes_project_id`
- `idx_scenes_project_id_scene_order`

## 表：`scene_versions`

- 用途：保存 Scene 历史版本

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigserial | 主键 |
| scene_id | varchar(32) | 关联 Scene |
| version | int | 版本号 |
| template_type | varchar(32) | 模板类型 |
| voiceover | text | 旁白 |
| screen_text | jsonb | 屏幕文案 |
| duration_sec | int | 时长 |
| visual_params | jsonb | 可视参数 |
| edited_by | varchar(32) | MVP 可固定 `system` / `user` |
| created_at | timestamptz | 创建时间 |

索引：

- `idx_scene_versions_scene_id_version`

## 表：`assets`

- 用途：保存音频、字幕、视频、清单文件元数据

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigserial | 主键 |
| project_id | varchar(32) | 关联项目 |
| scene_id | varchar(32) | 可空，Scene 级资产才有 |
| asset_type | varchar(32) | `audio` / `subtitle` / `video` / `manifest` / `scene_json` |
| file_url | text | 文件地址 |
| file_size | bigint | 文件大小 |
| duration_ms | int | 音频/视频时长 |
| metadata | jsonb | 附加信息 |
| created_at | timestamptz | 创建时间 |

索引：

- `idx_assets_project_id_asset_type`
- `idx_assets_scene_id_asset_type`

## 表：`job_logs`

- 用途：保存阶段日志和错误

关键字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigserial | 主键 |
| job_id | varchar(32) | 关联任务 |
| stage | varchar(32) | 所属阶段 |
| level | varchar(16) | `info` / `warn` / `error` |
| message | text | 日志内容 |
| payload | jsonb | 结构化附加数据 |
| created_at | timestamptz | 创建时间 |

索引：

- `idx_job_logs_job_id_stage`

---

# 10. 后端目录结构

建议目录结构如下，不要再拆更多服务：

```text
backend/
  app/
    api/
      projects.py
      jobs.py
      scenes.py
      results.py
    core/
      config.py
      logging.py
      errors.py
      db.py
      redis.py
    models/
      project.py
      generation_job.py
      article_analysis.py
      scene.py
      scene_version.py
      asset.py
      job_log.py
    schemas/
      project.py
      article_analysis.py
      scene_spec.py
      template_props.py
      job.py
    services/
      project_service.py
      job_service.py
      article_parse_service.py
      scene_generate_service.py
      scene_validate_service.py
      template_mapping_service.py
      tts_service.py
      subtitle_service.py
      render_prepare_service.py
      result_service.py
    workers/
      pipeline_worker.py
      render_dispatcher.py
    graph/
      generation_graph.py
      generation_state.py
    repositories/
      project_repo.py
      job_repo.py
      scene_repo.py
      asset_repo.py
      log_repo.py
    utils/
      text_stats.py
      json_repair.py
      timeline.py
      subtitle_splitter.py
  scripts/
    run_worker.py
    run_render_dispatcher.py
```

约束：

- `services/` 只写业务逻辑
- `repositories/` 只做数据库读写
- `api/` 不允许直接写 LLM 调用
- `graph/` 只负责状态流转，不写具体业务细节

---

# 11. LangGraph 状态机设计

不要做多 agent。只做一条固定状态机。

## `GenerationState`

```json
{
  "job_id": "job_001",
  "project_id": "proj_001",
  "article_content": "",
  "analysis": null,
  "scenes": [],
  "validated_scenes": [],
  "tts_assets": [],
  "subtitles": [],
  "render_manifest_url": null,
  "error_code": null,
  "error_message": null
}
```

状态节点：

1. `load_project`
2. `article_parse`
3. `scene_generate`
4. `scene_validate`
5. `tts_generate`
6. `subtitle_generate`
7. `render_prepare`
8. `dispatch_render`
9. `complete`
10. `fail`

路由规则：

- `article_parse` 失败且可重试：回到 `article_parse`
- `scene_generate` 校验失败：进入 `scene_validate_fix`
- `scene_validate_fix` 失败：进入 `fail`
- `tts_generate` 某 Scene 失败且可重试：重试当前 Scene
- `dispatch_render` 只负责发渲染任务，不等待视频文件生成

实现要求：

- 每个节点必须更新 `generation_jobs.stage`
- 每个节点必须记录结构化日志
- 每个节点失败时必须写 `error_code`

---

# 12. 前端页面与接口契约

前端只需要 4 个页面，不要扩 UI。

## 页面 1：文章输入页

- 功能：
  - 输入标题
  - 输入正文
  - 提交项目
- 调用接口：
  - `POST /projects`

## 页面 2：生成中页

- 功能：
  - 展示当前阶段
  - 展示进度
  - 展示失败原因
- 调用接口：
  - `POST /projects/{project_id}/jobs/generate`
  - `GET /jobs/{job_id}`

轮询策略：

- 每 `2s` 轮询一次
- `completed` / `failed` / `cancelled` 后停止

## 页面 3：结果预览页

- 功能：
  - 视频播放
  - Scene 列表展示
  - 每个 Scene 的基础字段展示
- 调用接口：
  - `GET /projects/{project_id}/result`
  - `GET /projects/{project_id}/scenes`

## 页面 4：Scene 编辑页

- 功能：
  - 修改 `voiceover`
  - 修改 `screen_text`
  - 修改 `template_type`
  - 修改 `duration_sec`
  - 触发整片重渲染
- 调用接口：
  - `PATCH /scenes/{scene_id}`
  - `POST /projects/{project_id}/jobs/rerender`

关键接口契约：

## `POST /projects`

请求：

```json
{
  "title": "什么是 RAG",
  "source_type": "markdown",
  "content": "# 什么是 RAG\n\nRAG 是..."
}
```

响应：

```json
{
  "project_id": "proj_001",
  "status": "created",
  "article_stats": {
    "char_count": 2140,
    "estimated_reading_sec": 320
  }
}
```

## `POST /projects/{project_id}/jobs/generate`

响应：

```json
{
  "job_id": "job_001",
  "status": "queued"
}
```

## `GET /jobs/{job_id}`

响应：

```json
{
  "job_id": "job_001",
  "status": "running",
  "stage": "scene_generate",
  "progress": 0.32,
  "error": null
}
```

## `GET /projects/{project_id}/scenes`

响应：

```json
[
  {
    "scene_id": "sc_001",
    "version": 1,
    "order": 1,
    "template_type": "hook_title",
    "voiceover": "你以为 RAG 只是知识库？",
    "screen_text": ["RAG 不只是知识库", "它解决引用可信"],
    "duration_sec": 6
  }
]
```

## `PATCH /scenes/{scene_id}`

请求：

```json
{
  "voiceover": "很多人以为 RAG 只是知识库问答，但它真正解决的是知识更新和引用可信的问题。",
  "screen_text": ["RAG 不只是知识库问答", "它解决知识更新与引用可信"],
  "template_type": "bullet_explain",
  "duration_sec": 7,
  "version": 4
}
```

成功响应：

```json
{
  "scene_id": "sc_001",
  "version": 5,
  "validation": {
    "ok": true,
    "warnings": []
  }
}
```

冲突响应：

```json
{
  "error_code": "SCENE_VERSION_CONFLICT",
  "message": "scene version conflict"
}
```

## `GET /projects/{project_id}/result`

响应：

```json
{
  "video_url": "/assets/video/proj_001/final.mp4",
  "subtitle_url": "/assets/video/proj_001/subtitles.srt",
  "scene_json_url": "/assets/video/proj_001/scenes.json",
  "duration_sec": 57,
  "resolution": "1080x1920"
}
```

---

# 13. 开发顺序

按这个顺序开发，不要反过来。

1. 建 `PostgreSQL` 表和 Pydantic Schema
2. 实现 `POST /projects` 和 `GET /jobs/{job_id}`
3. 实现 `generation_jobs` 队列和 worker 框架
4. 实现 `article_parse` 和 `scene_generate`
5. 实现 `scene_validate`
6. 实现 3 个 Remotion 模板
7. 实现 `tts_generate` 和 `subtitle_generate`
8. 实现 `render_prepare` 和 `render-worker`
9. 实现 `GET /result`、`GET /scenes`
10. 实现 `PATCH /scenes/{scene_id}` 和重渲染
11. 最后接前端页面

原因：

- 先把数据结构和异步链路跑通，前端才不会反复返工
- 先做模板，再接渲染，避免后面 JSON 结构频繁变动
- Scene 编辑必须建立在稳定的版本模型上
