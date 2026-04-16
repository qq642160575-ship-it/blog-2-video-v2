# Step 12 测试指南 - 真实 LLM 分镜生成

## ✅ Step 12 已完成

已接入真实 LLM（DeepSeek）进行分镜生成，可以根据文章分析结果自动生成 6-10 个视频场景。

## 📁 新增文件

```
backend/app/
├── schemas/
│   └── scene_generation.py         # SceneGeneration Pydantic Schema
├── services/
│   └── scene_generate_service.py   # 分镜生成服务（LangChain + DeepSeek）
└── scripts/
    ├── test_scene_generate.py      # 完整测试脚本（文章解析 + 场景生成）
    └── test_scene_quick.py          # 快速测试脚本（仅场景生成）
```

## 🔧 功能特性

### SceneGeneration Schema
包含以下字段：
- `scenes`: 场景列表（6-10个）
  - `template_type`: 模板类型（hook_title/bullet_explain/compare_process/quote_highlight/summary_cta）
  - `goal`: 场景目标
  - `voiceover`: 旁白文本（口语化）
  - `screen_text`: 屏幕文字列表（2-4个关键词）
  - `duration_sec`: 场景时长（5-10秒）
  - `pace`: 节奏（fast/medium/slow）
  - `transition`: 转场效果（cut/fade/slide）
  - `visual_params`: 视觉参数（可选）
- `total_duration`: 总时长（45-60秒）
- `narrative_flow`: 叙事流程说明
- `confidence`: 置信度（0-1）
- `reasoning`: 生成推理（可选）

### SceneGenerateService
- 使用 LangChain + DeepSeek Chat
- 基于文章分析结果生成场景
- 专业的视频脚本编剧 Prompt
- 自动控制总时长在 45-60 秒
- 自动重试机制（最多3次）
- 错误处理和降级

### Pipeline Worker 集成
- 优先使用真实 LLM
- 如果 API Key 未配置，自动降级到 Mock
- 如果 LLM 调用失败，自动降级到 Mock
- 保证系统稳定性

## 🧪 如何测试

### 方式 1: 快速测试分镜生成

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_scene_quick.py
```

**预期输出：**
```
Testing scene generation...
Article Analysis: RAG技术原理与应用
Generating scenes...

✓ Generated 7 scenes
Total duration: 60s
Confidence: 0.95

Scene 1: hook_title - 用问题吸引注意力，引出RAG技术
  Duration: 7s, Pace: fast
  Voiceover: AI回答总是出错？因为它可能缺少最新知识！...

Scene 2: bullet_explain - 解释RAG的核心概念
  Duration: 8s, Pace: medium
  Voiceover: RAG，全称检索增强生成。简单说，就是让AI在回答前...
...
```

### 方式 2: 完整测试（文章解析 + 场景生成）

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_scene_generate.py
```

这个测试会：
1. 先调用 LLM 解析文章
2. 再根据解析结果生成场景
3. 显示完整的场景列表

**注意：** 这个测试需要调用两次 LLM API，可能需要 30-60 秒。

### 方式 3: 端到端测试（完整流程）

**启动服务：**
```bash
# 终端 1 - API Server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端 2 - Pipeline Worker（会自动使用 LLM）
cd backend
source venv/bin/activate
python scripts/run_worker.py

# 终端 3 - Render Worker
cd render-worker
npm start

# 终端 4 - 运行测试
cd backend
source venv/bin/activate
python scripts/test_milestone1.py
```

**观察 Pipeline Worker 输出：**
```
[1/6] Article Parse...
  ✓ Topic: RAG技术原理与应用 (Real LLM)
  ✓ Confidence: 0.95

[2/6] Scene Generate...
  ✓ Generated 7 scenes (Real LLM)
  ✓ Total duration: 60s
  ✓ Confidence: 0.95
```

如果看到 `(Real LLM)` 标记，说明使用了真实 LLM。

## 🔍 验证

### 检查是否使用了真实 LLM

1. 查看 Pipeline Worker 日志，确认有 `(Real LLM)` 标记
2. 观察处理时间：真实 LLM 调用需要 10-30 秒，Mock 只需 1 秒
3. 检查生成场景的多样性和质量

### 场景质量检查

生成的场景应该：
- 总时长在 45-60 秒之间
- 场景数量在 6-10 个之间
- 每个场景时长在 5-10 秒之间
- 旁白文本口语化、简洁
- 屏幕文字精炼（2-4个关键词）
- 节奏有快慢变化
- 叙事流程流畅（钩子→核心→展开→总结）

## ✨ 技术实现

### LangChain 集成
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.5,
    request_timeout=60
)
chain = prompt | llm | parser
result = chain.invoke({...})
```

### Pydantic Schema 校验
```python
class SceneData(BaseModel):
    template_type: str
    goal: str
    voiceover: str
    screen_text: List[str]
    duration_sec: int
    # ...

class SceneGeneration(BaseModel):
    scenes: List[SceneData]
    total_duration: int
    narrative_flow: str
    confidence: float
```

### 重试机制
```python
def generate_scenes_with_retry(analysis, max_retries=3):
    for attempt in range(max_retries):
        try:
            return generate_scenes(analysis)
        except Exception as e:
            if attempt < max_retries - 1:
                continue
            raise
```

## 🎯 下一步：Step 13

接入真实 TTS 服务（Azure Speech），将旁白文本转换为语音。

## 📝 已完成的步骤

- ✅ Step 1-10: Milestone 1 完整流程（Mock）
- ✅ Step 11: 真实 LLM 文章解析
- ✅ Step 12: 真实 LLM 分镜生成
- ⏳ Step 13: 真实 TTS 语音合成
