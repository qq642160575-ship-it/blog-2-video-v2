# 程序员实现方案

基于 `doc/产品/out_1.md` 和 `doc/技术/out_1.md`，不建议按产品文档里的“大 MVP”做。真正能落地的版本应该是：

> 输入一篇 Markdown / 纯文本文章，生成 6 到 10 个 Scene，使用 3 个固定模板，生成 TTS、字幕、9:16 MP4。用户可编辑 Scene 文案、屏幕文字、视觉类型，然后整片重渲染。

---

## 1. 功能实现拆解

### P0 真正要做的功能

1. 文章输入
   - 支持纯文本 / Markdown。
   - 不做 URL 抓取。
   - 限制 1000 到 3000 中文字，超出直接提示或截断前让用户确认。
   - 存储原文、标题、语言、字数、创建时间。

2. 文章解析
   - LLM 输出结构化摘要。
   - 输出字段：主题、受众、核心观点、关键论点、可视化点、丢弃内容。
   - 必须 JSON Schema 校验，不合格自动重试一次。

3. 分镜生成
   - LLM 基于文章摘要生成 `SceneSpec[]`。
   - 固定 6 到 10 个 Scene。
   - 每个 Scene 必须包含旁白、屏幕文案、模板类型、建议时长、节奏标签。
   - 生成后跑规则校验，失败就让 LLM 修复，不要直接进入渲染。

4. 模板渲染
   - 第一版只做 3 个模板：
   - `hook_title`：开头钩子 / 观点冲击。
   - `bullet_explain`：要点解释 / 列表讲解。
   - `compare_process`：对比 / 流程 / 步骤说明。
   - 不允许 LLM 生成 React / Remotion 代码，只允许生成模板参数。

5. TTS 和字幕
   - P0 只接一个 TTS 供应商。
   - 字幕粒度先做到句级或短语级，不追求字级精准。
   - 如果 TTS 供应商返回 timestamps，就用供应商时间戳。
   - 如果没有 timestamps，就按字符数估算切分。

6. 视频渲染
   - Remotion 异步渲染。
   - API 只返回 `job_id`，前端轮询状态。
   - 输出 MP4。
   - 固定 1080x1920，30fps。
   - P0 不支持横屏、不支持多平台版本。

7. Scene 编辑
   - 用户可编辑：
   - `voiceover`
   - `screen_text`
   - `template_type`
   - `duration_sec`
   - 修改后整片重渲染。
   - 不做真正的局部重生成，对外不要承诺“只重渲染某一段”。

8. 任务和存储
   - 所有阶段都保存中间结果。
   - 保存 LLM 输入、LLM 输出、校验错误、TTS 文件、字幕文件、渲染日志。
   - 否则生成质量出问题时根本没法排查。

---

## 2. API 设计（示例）

### 创建项目

```http
POST /api/projects
Content-Type: application/json
```

```json
{
  "title": "什么是 RAG",
  "source_type": "markdown",
  "content": "# 什么是 RAG\n\nRAG 是..."
}
```

返回：

```json
{
  "project_id": "proj_01HZX...",
  "status": "created",
  "article_stats": {
    "char_count": 2140,
    "estimated_reading_sec": 320
  }
}
```

### 启动生成任务

```http
POST /api/projects/{project_id}/generate
Content-Type: application/json
```

```json
{
  "target_duration_sec": 55,
  "aspect_ratio": "9:16",
  "voice": {
    "provider": "azure",
    "voice_id": "zh-CN-XiaoxiaoNeural",
    "speed": 1.08
  },
  "style": {
    "theme": "clean_tech",
    "font_family": "Noto Sans SC",
    "primary_color": "#1E88E5"
  }
}
```

返回：

```json
{
  "job_id": "job_01HZY...",
  "status": "queued"
}
```

### 查询任务状态

```http
GET /api/jobs/{job_id}
```

返回：

```json
{
  "job_id": "job_01HZY...",
  "project_id": "proj_01HZX...",
  "status": "rendering",
  "stage": "remotion_render",
  "progress": 0.72,
  "error": null,
  "outputs": {
    "video_url": null,
    "preview_url": null
  }
}
```

状态枚举：

```ts
type JobStatus =
  | "queued"
  | "running"
  | "waiting_retry"
  | "failed"
  | "completed"
  | "cancelled";
```

阶段枚举：

```ts
type PipelineStage =
  | "article_parse"
  | "scene_generate"
  | "scene_validate"
  | "tts_generate"
  | "subtitle_generate"
  | "render_prepare"
  | "remotion_render"
  | "export";
```

### 获取 Scene 列表

```http
GET /api/projects/{project_id}/scenes
```

返回：

```json
{
  "project_id": "proj_01HZX...",
  "version": 3,
  "scenes": [
    {
      "scene_id": "sc_001",
      "order": 1,
      "template_type": "hook_title",
      "goal": "用反常识观点建立开头钩子",
      "voiceover": "你以为 RAG 只是给大模型接一个知识库？其实它真正解决的是模型不会持续记忆的问题。",
      "screen_text": ["RAG 不是外挂知识库", "它解决的是记忆问题"],
      "duration_sec": 6,
      "pace": "fast",
      "transition": "cut",
      "visual_params": {
        "emphasis": "RAG",
        "badge": "核心概念"
      }
    }
  ]
}
```

### 修改 Scene

```http
PATCH /api/projects/{project_id}/scenes/{scene_id}
Content-Type: application/json
```

```json
{
  "voiceover": "很多人以为 RAG 只是知识库问答，但它真正解决的是大模型知识更新和可信引用的问题。",
  "screen_text": ["RAG 不只是知识库问答", "它解决知识更新与引用可信"],
  "template_type": "bullet_explain",
  "duration_sec": 7
}
```

返回：

```json
{
  "scene_id": "sc_001",
  "version": 4,
  "validation": {
    "ok": true,
    "warnings": []
  }
}
```

### 重渲染视频

```http
POST /api/projects/{project_id}/render
Content-Type: application/json
```

```json
{
  "scene_version": 4,
  "reuse_assets": true
}
```

返回：

```json
{
  "job_id": "job_01HZZ...",
  "status": "queued"
}
```

### 下载结果

```http
GET /api/projects/{project_id}/outputs/latest
```

返回：

```json
{
  "video_url": "https://cdn.example.com/videos/proj_01HZX/final.mp4",
  "subtitle_url": "https://cdn.example.com/videos/proj_01HZX/subtitles.srt",
  "scene_json_url": "https://cdn.example.com/videos/proj_01HZX/scenes.json",
  "duration_sec": 57,
  "resolution": "1080x1920"
}
```

---

## 3. 数据结构设计

### Project

```ts
interface Project {
  id: string;
  title: string;
  sourceType: "text" | "markdown";
  sourceContent: string;
  language: "zh-CN" | "en-US";
  status: "draft" | "generating" | "ready" | "failed";
  currentSceneVersion: number;
  createdAt: string;
  updatedAt: string;
}
```

### ArticleAnalysis

```ts
interface ArticleAnalysis {
  projectId: string;
  version: number;
  topic: string;
  audience: string;
  coreMessage: string;
  keyPoints: string[];
  visualizablePoints: string[];
  discardedParts: string[];
  contentType: "tutorial" | "comparison" | "opinion" | "process_explain";
  confidence: number;
}
```

### SceneSpec

```ts
interface SceneSpec {
  sceneId: string;
  projectId: string;
  version: number;
  order: number;

  templateType: "hook_title" | "bullet_explain" | "compare_process";

  goal: string;
  voiceover: string;
  screenText: string[];

  durationSec: number;
  pace: "slow" | "medium" | "fast";
  transition: "cut" | "slide" | "fade";

  visualParams: Record<string, unknown>;

  validationStatus: "valid" | "warning" | "invalid";
  validationMessages: string[];
}
```

### Template Params

```ts
type TemplateParams =
  | HookTitleParams
  | BulletExplainParams
  | CompareProcessParams;

interface HookTitleParams {
  templateType: "hook_title";
  title: string;
  subtitle?: string;
  emphasisWords: string[];
  badge?: string;
}

interface BulletExplainParams {
  templateType: "bullet_explain";
  heading: string;
  bullets: string[];
  highlightIndex?: number;
}

interface CompareProcessParams {
  templateType: "compare_process";
  heading: string;
  leftTitle?: string;
  rightTitle?: string;
  leftItems?: string[];
  rightItems?: string[];
  steps?: string[];
}
```

### SubtitleCue

```ts
interface SubtitleCue {
  cueId: string;
  sceneId: string;
  startMs: number;
  endMs: number;
  text: string;
}
```

### Asset

```ts
interface Asset {
  id: string;
  projectId: string;
  sceneId?: string;
  type: "tts_audio" | "subtitle" | "preview_image" | "video";
  url: string;
  durationMs?: number;
  metadata: Record<string, unknown>;
  createdAt: string;
}
```

### GenerationJob

```ts
interface GenerationJob {
  id: string;
  projectId: string;
  type: "full_generate" | "render_only" | "tts_only";
  status: "queued" | "running" | "waiting_retry" | "failed" | "completed" | "cancelled";
  stage: PipelineStage;
  progress: number;
  inputSnapshot: Record<string, unknown>;
  outputSnapshot?: Record<string, unknown>;
  errorCode?: string;
  errorMessage?: string;
  retryCount: number;
  createdAt: string;
  updatedAt: string;
}
```

### Scene 校验规则

```ts
interface SceneValidationRule {
  minScenes: 6;
  maxScenes: 10;
  minDurationSec: 4;
  maxDurationSec: 9;
  maxVoiceoverCharsPerScene: 90;
  maxScreenTextItems: 3;
  maxScreenTextCharsPerItem: 18;
  allowedTemplates: ["hook_title", "bullet_explain", "compare_process"];
}
```

这些规则必须写进代码，不要只写在 Prompt 里。Prompt 只能提高成功率，不能保证正确性。

---

## 4. 核心流程（步骤 or 时序）

### 首次生成流程

```text
用户提交文章
  ↓
后端创建 Project
  ↓
校验文章长度、空内容、语言
  ↓
创建 GenerationJob
  ↓
LLM 生成 ArticleAnalysis
  ↓
JSON Schema 校验
  ↓
LLM 生成 SceneSpec[]
  ↓
Scene 规则校验
  ↓
失败则要求 LLM 修复一次
  ↓
仍失败则返回人工可读错误
  ↓
为每个 Scene 生成 TTS
  ↓
基于 TTS 生成字幕时间轴
  ↓
将 SceneSpec + Audio + Subtitle 转成 Remotion props
  ↓
异步渲染 MP4
  ↓
保存视频 Asset
  ↓
Project 状态变为 ready
  ↓
前端展示视频和 Scene 编辑器
```

### 编辑后重渲染流程

```text
用户修改 Scene
  ↓
后端校验 Scene 字段
  ↓
创建新的 scene_version
  ↓
如果旁白没变，复用原 TTS
  ↓
如果旁白变了，重新生成该 Scene TTS
  ↓
重新生成字幕时间轴
  ↓
整片重新渲染
  ↓
生成新 MP4
  ↓
旧版本保留，可回滚
```

注意：产品上说“局部重生成”会很诱人，但 P0 实现上建议只是“局部更新资产 + 整片重渲染”。这样用户感知上已经够用，技术复杂度低很多。

### 渲染 Props 生成

```ts
interface RemotionVideoProps {
  width: 1080;
  height: 1920;
  fps: 30;
  scenes: Array<{
    sceneId: string;
    startFrame: number;
    durationFrames: number;
    templateType: SceneSpec["templateType"];
    templateParams: TemplateParams;
    audioUrl: string;
    subtitles: SubtitleCue[];
    transition: SceneSpec["transition"];
  }>;
  style: {
    theme: string;
    fontFamily: string;
    primaryColor: string;
    backgroundColor: string;
  };
}
```

---

## 5. 边界情况（必须列出）

1. 文章太短
   - 少于 500 字时，LLM 很可能编内容。
   - 应提示“内容不足，建议补充论点”，不要硬生成。

2. 文章太长
   - 超过 3000 到 5000 字会导致摘要质量波动。
   - P0 直接限制长度，别做复杂长文分块。

3. Markdown 里有代码块
   - 技术文章常见。
   - 代码块不能直接塞进字幕。
   - 需要提取代码意图，而不是逐行讲代码。

4. 文章结构混乱
   - 没标题、没段落、观点跳跃。
   - LLM 会生成“看似合理但偏题”的分镜。
   - 要在 ArticleAnalysis 里返回 `confidence`，低于阈值提示用户先整理文章。

5. Scene 旁白过长
   - TTS 会拖长，字幕也会爆屏。
   - 必须限制单 Scene 字数。

6. 屏幕文案过长
   - 9:16 竖屏安全区有限。
   - 每条屏幕文案建议不超过 18 个中文字符。

7. 总时长不准
   - LLM 给的 `duration_sec` 只是建议。
   - 实际时长应以 TTS 音频为准。
   - 渲染时需要重新计算 Scene duration。

8. TTS 失败
   - 供应商限流、文本非法、网络失败都可能发生。
   - 必须支持重试和错误落库。

9. 字幕和语音不同步
   - 如果靠估算时间，长句会明显不同步。
   - 至少按标点切短句，不要整段字幕一次性出现。

10. 模板参数缺字段
    - LLM 可能漏掉 `bullets` 或给空数组。
    - 渲染前必须做模板参数补全或拒绝渲染。

11. 用户修改后破坏约束
    - 用户可能把一句旁白改成 300 字。
    - 前端要限制，后端也要校验，不能只相信前端。

12. 同时发起多个渲染
    - 用户连续点击“重新生成”。
    - 要取消旧 job 或标记旧 job 结果过期。

13. 视频渲染超时
    - Remotion 卡住或资源不足。
    - Job 必须有 timeout，不然任务永远 running。

14. 文件存储丢失
    - DB 有记录但音频文件不存在。
    - 渲染前检查资产可访问性。

15. 中文字体缺失
    - 服务器环境没有字体会导致乱码或 fallback 很丑。
    - 渲染容器必须内置字体。

16. 特殊字符
    - Emoji、数学公式、HTML 标签、Markdown 表格可能造成布局异常。
    - 输入清洗时要转义或降级。

17. 敏感内容
    - TTS 或平台可能拒绝生成某些文本。
    - 需要返回明确错误，不要只显示“生成失败”。

18. 成本失控
    - 用户重复生成会消耗 LLM、TTS、渲染资源。
    - 每个项目限制生成次数，记录 token、字符数、渲染耗时。

---

## 6. 潜在 bug 点

1. LLM 输出不是合法 JSON
   - 解决：JSON Schema + 自动修复 + 最大重试次数。

2. Scene 顺序错乱
   - 解决：使用显式 `order` 字段，保存前排序并检查连续性。

3. Scene duration 和音频 duration 不一致
   - 解决：渲染时以音频时长为准，`duration_sec` 只作为生成参考。

4. 字幕越界
   - 解决：统一字幕安全区，超过两行自动缩小字号或拆分 cue。

5. 模板拿到错误参数直接崩溃
   - 解决：每个模板有自己的参数 schema，渲染前 validate。

6. 用户编辑覆盖了新版本
   - 解决：PATCH 时带 `version`，版本不一致返回冲突。

```http
409 Conflict
```

```json
{
  "error": "SCENE_VERSION_CONFLICT",
  "message": "Scene 已被更新，请刷新后重试"
}
```

7. 重渲染用了旧资产
   - 解决：资产按 `scene_version` 关联，不要只按 `scene_id` 查最新。

8. 多任务并发污染状态
   - 解决：Job 输出不能直接覆盖 Project，只有最新有效 job 可以更新 `current_output_id`。

9. 渲染容器本地路径和线上 URL 混用
   - 解决：统一 Asset Resolver，Remotion props 里只放可访问 URL 或已挂载路径。

10. TTS 文本和字幕文本不一致
    - 解决：字幕必须基于最终 TTS 输入文本生成，不要基于用户原始输入另算。

11. LLM 幻觉补充文章没有的观点
    - 解决：Prompt 要求只基于原文，ArticleAnalysis 保留引用片段，低置信度提示人工检查。

12. 文章链接输入如果硬做会炸
    - 解决：P0 不做 URL。别把爬虫问题伪装成生成问题。

13. 局部重生成承诺过早
    - 解决：P0 对外只说“编辑后重新生成视频”，内部可以复用未变资产。

14. 批量处理过早
    - 解决：数据模型保留 job，但 UI 不做批量任务中心。

15. 质量预警只做 UI 不进 pipeline
    - 解决：质量规则必须是后端硬校验，不能只是前端提示。

---

## 7. 【关键】对产品 & 技术的吐槽 + 修改建议

### 对产品经理的吐槽

产品文档最大的问题是：把“最终产品愿景”塞进了“MVP”。这不是 MVP，这是缩小版内容生产平台。

具体问题：

1. P0 同时要文章链接、分镜、Visual DSL、5 到 8 个模板、TTS、字幕对齐、Remotion、成片导出、Scene 级编辑和局部重生成，范围过大。
2. “30 到 90 秒”跨度太大，30 秒和 90 秒的节奏策略完全不同。
3. “文章链接输入”不该进 P0，它会引入爬虫、反爬、正文抽取、版权和登录墙问题。
4. “局部重生成”描述得太轻松，实际会牵扯时间轴、TTS、字幕、缓存、版本一致性。
5. 用户画像太多，技术博主、小团队、AI 内容创业者的需求不是一回事。
6. 批量生产被反复强调，但 MVP 又说优先个人博主，定位摇摆。

修改建议：

1. MVP 用户只选技术 / 知识博主，不服务团队。
2. MVP 时长固定 45 到 60 秒。
3. P0 只支持纯文本和 Markdown。
4. P0 模板只做 3 个。
5. P0 做 Scene 编辑，但不承诺真正局部重生成。
6. 产品定位改成“文章转短视频初稿工具”，不要宣传成“全自动爆款视频系统”。

### 对技术经理的吐槽

技术方案比产品方案冷静，但也有几个容易翻车的地方。

具体问题：

1. 如果技术团队一上来做“通用 Visual DSL”，就是过度工程。
2. 如果为了快让 LLM 直接生成 Remotion 代码，后面会维护地狱。
3. 如果任务系统做得太平台化，MVP 会被队列、权限、工作流拖死。
4. 如果只做一种模板，产品会像 PPT 自动分页器，用户很快腻。
5. 如果不保存中间产物，生成质量问题无法 debug。
6. 如果渲染请求同步阻塞 API，稍微慢一点就超时。

修改建议：

1. 不要做完整 DSL，先做 `SceneSpec`。
2. 不要让 LLM 写代码，只让它写 JSON。
3. 后端必须异步 job 化，但不要做复杂工作流引擎。
4. 模板数量控制在 3 个，但每个模板要打磨到稳定可用。
5. 所有 LLM 输入输出、校验结果、TTS、字幕、渲染日志必须落库。
6. 渲染并发 P0 直接限制，别提前做大规模分布式渲染。

### 最终落地版

建议把第一版实现目标定成：

```text
输入：一篇 1000 到 3000 字 Markdown / 纯文本文章

输出：
- 6 到 10 个 Scene
- 45 到 60 秒
- 9:16
- 1080x1920
- TTS 配音
- 句级字幕
- MP4 成片
- Scene 可编辑
- 编辑后整片重渲染

不做：
- URL 抓取
- 批量任务 UI
- 多平台版本
- 横屏
- 复杂品牌系统
- 复杂 Visual DSL
- 真正局部重生成
- LLM 生成前端代码
```

这个版本才是“程序员能开工”的版本。产品价值还在，工程复杂度可控，后续也能平滑扩展到批量、更多模板、品牌配置和局部重生成。
