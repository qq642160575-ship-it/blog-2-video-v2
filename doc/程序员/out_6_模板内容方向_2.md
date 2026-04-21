# 开发任务列表：Scene 表达力与节奏数据优化（单人可执行版）

**文档版本**: v1.0
**创建日期**: 2026-04-21
**目标**: 从 0 到 MVP，一步一步能走通
**预计完成**: 5 天（仅阶段 1）

---

## 🎯 核心目标

让视频从"机器念稿"变成"像人说话"：
- LLM 标注重点词
- TTS 提供精确时间戳
- 自动计算时间轴
- 渲染时强调关键词

---

## 1. 开发主链路（核心）

### Step 1：验证 TTS 能力（最高优先级）
**做什么**：
- 测试当前 TTS 服务是否支持 word-level timestamps
- 如果不支持，评估 forced alignment 工具（Gentle）
- 如果都不行，设计降级方案（按字数均匀分布）

**产出**：
- 测试脚本：`backend/scripts/test_tts_timestamps.py`
- 测试报告：能/不能/需要换服务

**验证方式**：
```bash
python backend/scripts/test_tts_timestamps.py
# 输出：TTS 返回的 word-level timestamps JSON
```

**为什么第一步做这个**：
- 这是最大的技术风险
- 如果不支持，整个方案需要调整
- 必须立即验证，避免后期返工

---

### Step 2：定义核心数据结构
**做什么**：
- 在 Scene 模型中增加 3 个新字段
- 编写数据库迁移脚本
- 执行迁移

**产出**：
```python
# backend/app/models/scene.py
class Scene(BaseModel):
    # 现有字段...
    voiceover: str
    screen_text: List[str]
    duration_sec: float

    # 新增字段
    emphasis_words: List[str] = Field(default_factory=list, max_items=3)
    tts_metadata: Optional[dict] = None
    timeline_data: Optional[dict] = None
```

**验证方式**：
```bash
# 执行数据库迁移
alembic revision --autogenerate -m "add emphasis fields to scene"
alembic upgrade head

# 验证字段已添加
python -c "from app.models.scene import Scene; print(Scene.model_fields.keys())"
```

**为什么现在做**：
- 数据结构是后续所有开发的基础
- 先定义好，避免后期改表

---

### Step 3：实现时间轴计算服务（用 mock 数据）
**做什么**：
- 创建 `TimelineCalculateService`
- 实现核心算法：根据 emphasis_words 和 TTS timestamps 计算时间轴
- 先用 mock 数据测试

**产出**：
```python
# backend/app/services/timeline_calculate_service.py
def calculate_timeline(scene: Scene, tts_metadata: dict) -> dict:
    """根据 TTS timestamps 计算时间轴"""
    timeline = []

    # 为每个重点词生成强调动效
    for word in scene.emphasis_words:
        timestamp = find_word_timestamp(word, tts_metadata)
        if timestamp:
            timeline.append({
                'time': timestamp - 0.1,
                'element': word,
                'action': 'pop',
                'duration': 0.3
            })

    return {'keyframes': timeline}
```

**验证方式**：
```python
# 单元测试
mock_scene = Scene(
    voiceover="这个方法能让你的效率提升3倍",
    emphasis_words=["方法", "效率", "3倍"]
)
mock_tts = {
    'word_timestamps': [
        {'word': '方法', 'start': 0.3, 'end': 0.7},
        {'word': '效率', 'start': 1.4, 'end': 1.8}
    ]
}
result = calculate_timeline(mock_scene, mock_tts)
print(result)  # 应该输出 2 个关键帧
```

**为什么现在做**：
- 这是纯计算逻辑，不依赖外部服务
- 可以用 mock 数据快速验证算法正确性
- 先打通核心逻辑，再接入真实数据

---

### Step 4：扩展 LLM Prompt（让它标注重点词）
**做什么**：
- 修改 `SceneGenerateService` 的 Prompt
- 增加 `emphasis_words` 标注要求
- 解析 LLM 输出，提取 `emphasis_words`

**产出**：
```python
# backend/app/services/scene_generate_service.py
PROMPT_TEMPLATE = """
你是短视频脚本专家。基于文章分析和 Hook，生成 6-10 个场景。

【核心要求】
每个场景必须包含：
1. voiceover: 旁白文本（口语化、简洁）
2. screen_text: 屏幕文字（2-4 个关键词）
3. emphasis_words: 需要强调的关键词（2-3 个）

【emphasis_words 标注规则】
- 从 voiceover 中选择最重要的 2-3 个词
- 这些词应该是：核心概念、数字、对比词、结论词
"""
```

**验证方式**：
```python
# 调用 LLM，检查输出
result = scene_generate_service.generate(article, hook)
for scene in result['scenes']:
    assert 'emphasis_words' in scene
    assert 2 <= len(scene['emphasis_words']) <= 3
```

---

### Step 5：扩展 TTS 服务（获取 word-level timestamps）
**做什么**：
- 修改 `TTSService`，调用 TTS API 时请求 word-level timestamps
- 解析 TTS 返回的时间戳数据
- 实现降级方案（如果不支持）

**产出**：
```python
# backend/app/services/tts_service.py
def generate_audio(text: str, voice: str) -> dict:
    # 调用 TTS API
    response = tts_api.synthesize(
        text=text,
        voice=voice,
        return_word_timestamps=True  # 关键参数
    )

    return {
        'audio_url': response.audio_url,
        'duration_sec': response.duration,
        'word_timestamps': response.word_timestamps  # 新增
    }
```

**验证方式**：
```python
result = tts_service.generate_audio("这个方法能让你的效率提升3倍", "zh-CN")
print(result['word_timestamps'])
# 应该输出：[{'word': '这个', 'start': 0.0, 'end': 0.3}, ...]
```

**降级方案**（如果 TTS 不支持）：
```python
# 按字数均匀分布估算
def estimate_timestamps(text: str, duration: float) -> list:
    words = text.split()
    time_per_word = duration / len(words)
    return [
        {'word': w, 'start': i * time_per_word, 'end': (i+1) * time_per_word}
        for i, w in enumerate(words)
    ]
```

---

### Step 6：集成主流程（串联所有模块）
**做什么**：
- 在视频生成主流程中，串联所有新模块
- LLM 生成 scenes → TTS 生成音频 → 计算时间轴 → 保存到数据库

**产出**：
```python
# backend/app/services/video_generate_service.py
async def generate_video(article: str, hook: str):
    # 1. LLM 生成场景（包含 emphasis_words）
    scenes = await scene_generate_service.generate(article, hook)

    for scene in scenes:
        # 2. TTS 生成音频（获取 timestamps）
        tts_result = await tts_service.generate_audio(scene.voiceover)
        scene.tts_metadata = tts_result

        # 3. 计算时间轴
        timeline = timeline_calculate_service.calculate_timeline(
            scene, tts_result
        )
        scene.timeline_data = timeline

        # 4. 保存到数据库
        await scene.save()

    # 5. 渲染视频（下一步）
    return await render_service.render(scenes)
```

**验证方式**：
```bash
# 端到端测试
curl -X POST http://localhost:8000/api/videos/generate \
  -d '{"article": "...", "hook": "..."}'

# 检查数据库，每个 scene 应该有 emphasis_words, tts_metadata, timeline_data
```

---

### Step 7：渲染层适配（在指定时间点触发动效）
**做什么**：
- 修改 `RenderService`，读取 `timeline_data`
- 在指定时间点触发 pop 动效
- 测试音频视觉同步精度

**产出**：
```python
# backend/app/services/render_service.py
def render_scene(scene: Scene):
    # 读取时间轴数据
    timeline = scene.timeline_data['keyframes']

    # 为每个关键帧生成动效
    for keyframe in timeline:
        add_effect(
            time=keyframe['time'],
            element=keyframe['element'],
            action=keyframe['action'],  # 'pop'
            duration=keyframe['duration']
        )

    # 渲染视频
    return render_video(scene)
```

**验证方式**：
- 生成一个测试视频
- 播放视频，检查重点词是否在正确时间点出现 pop 动效
- 测量音频视觉同步误差（应 < 300ms）

---

### Step 8：端到端测试与调优
**做什么**：
- 用真实文章测试完整流程
- 检查 LLM 输出成功率
- 检查时间轴计算准确性
- 调整参数（提前时间、动效时长等）

**验证方式**：
```bash
# 生成 10 个测试视频
for i in {1..10}; do
    curl -X POST http://localhost:8000/api/videos/generate \
      -d @test_article_$i.json
done

# 检查成功率
# 目标：LLM 输出成功率 ≥ 90%
```

**调优参数**：
- 提前时间：0.1 秒 → 可能需要调整为 0.05 或 0.15
- 动效时长：0.3 秒 → 可能需要调整
- 词匹配阈值：精确匹配 → 可能需要模糊匹配

---

## 2. 数据结构优先定义

### Scene 模型（完整版）
```python
# backend/app/models/scene.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Scene(BaseModel):
    # 现有字段
    id: str
    voiceover: str
    screen_text: List[str]
    duration_sec: float
    pace: str  # 'slow' | 'medium' | 'fast'

    # 新增字段（阶段 1）
    emphasis_words: List[str] = Field(
        default_factory=list,
        description="需要强调的关键词，2-3 个",
        min_items=0,
        max_items=3
    )

    tts_metadata: Optional[dict] = Field(
        default=None,
        description="TTS 返回的 word-level timestamps"
    )

    timeline_data: Optional[dict] = Field(
        default=None,
        description="根据 TTS timestamps 计算的时间轴"
    )
```

---

### TTS Metadata 结构
```json
{
  "audio_url": "https://...",
  "duration_sec": 8.2,
  "word_timestamps": [
    {"word": "这个", "start": 0.0, "end": 0.3},
    {"word": "方法", "start": 0.3, "end": 0.7},
    {"word": "能让", "start": 0.7, "end": 1.1},
    {"word": "你的", "start": 1.1, "end": 1.4},
    {"word": "效率", "start": 1.4, "end": 1.8},
    {"word": "提升", "start": 1.8, "end": 2.2},
    {"word": "3倍", "start": 2.2, "end": 2.7}
  ]
}
```

### Timeline Data 结构
```json
{
  "keyframes": [
    {
      "time": 0.2,
      "element": "方法",
      "action": "pop",
      "duration": 0.3
    },
    {
      "time": 1.3,
      "element": "效率",
      "action": "pop",
      "duration": 0.3
    },
    {
      "time": 2.1,
      "element": "3倍",
      "action": "pop",
      "duration": 0.3
    }
  ]
}
```

---

## 3. 接口开发顺序

### 第一个接口：无需新增
- 使用现有的 `POST /api/videos/generate`
- 只需在内部流程中增加新模块

### 内部服务调用顺序
1. `SceneGenerateService.generate()` - 生成场景 + 标注重点词
2. `TTSService.generate_audio()` - 生成音频 + 获取时间戳
3. `TimelineCalculateService.calculate_timeline()` - 计算时间轴
4. `RenderService.render()` - 渲染视频

---

## 4. AI 集成步骤（关键）

### 4.1 LLM 集成步骤

**Step 1：先用 mock 数据测试**
```python
# 测试时间轴计算逻辑
mock_scene = Scene(
    voiceover="这个方法能让你的效率提升3倍",
    emphasis_words=["方法", "效率", "3倍"]
)
mock_tts = {...}  # mock TTS 数据
result = calculate_timeline(mock_scene, mock_tts)
```

**Step 2：替换为真实 LLM 调用**
```python
# 修改 Prompt，增加 emphasis_words 标注要求
# 调用 LLM API
# 解析输出
```

**Step 3：处理失败**
```python
# 重试 3 次
# 如果仍失败，降级为空数组
emphasis_words = []
```

---

### 4.2 TTS 集成步骤

**Step 1：验证 TTS 能力（Day 1 必做）**
```bash
python backend/scripts/test_tts_timestamps.py
```

**Step 2：如果支持，直接调用**
```python
response = tts_api.synthesize(
    text=text,
    voice=voice,
    return_word_timestamps=True
)
```

**Step 3：如果不支持，使用降级方案**
```python
# 方案 A：使用 forced alignment 工具（Gentle）
# 方案 B：按字数均匀分布估算
def estimate_timestamps(text, duration):
    words = text.split()
    time_per_word = duration / len(words)
    return [...]
```

---

## 5. 延后事项（刻意不做）

### 阶段 1 不做的功能

**不做停顿、语气、语速控制**
- 原因：LLM 输出成功率会下降
- 等阶段 1 验证通过后再考虑

**不做复杂动效**
- 原因：先验证 pop 动效是否有效
- 只做 pop，不做 fade_in / slide_in / zoom

**不做可视化编辑器**
- 原因：阶段 1 是自动生成，不需要编辑
- 等阶段 2 验证通过后再做

**不做节奏规则**
- 原因：先验证"重点词强调"是否有效
- 等阶段 1 验证通过后再做

---

## 6. 关键风险与应对

### 风险 1：TTS 不支持 word-level timestamps
**影响**：无法获取精确时间点
**应对**：
- Day 1 立即验证
- 如果不支持，使用 forced alignment 工具
- 最坏情况：按字数均匀分布估算

### 风险 2：LLM 标注的词在 TTS 中找不到
**影响**：时间轴计算失败
**应对**：
- 实现模糊匹配算法
- 如果找不到，跳过该词
- 记录日志，人工审核

### 风险 3：LLM 输出成功率下降
**影响**：从 95% 降到 < 90%
**应对**：
- 如果 < 90%，立即回退到规则方案
- 不增加 emphasis_words 字段

---

## 7. 验收标准（阶段 1）

### 技术指标
- LLM 输出成功率 ≥ 90%
- TTS timestamps 获取成功率 ≥ 95%
- 词匹配成功率 ≥ 80%
- 音频视觉同步误差 < 300ms

### 业务指标
- 用户认为"关键信息被强调"的比例 ≥ 60%
- 用户修改率下降 ≥ 5%（从 30% 降到 25%）

### 如果失败
- 如果成功率 < 90%，回退到规则方案
- 如果用户感知 < 60%，调整动效参数
- 如果修改率没下降，停止开发

---

## 8. 开发时间估算

| 步骤 | 任务 | 预计时间 |
|------|------|----------|
| Step 1 | 验证 TTS 能力 | 0.5 天 |
| Step 2 | 定义数据结构 + 数据库迁移 | 0.5 天 |
| Step 3 | 实现时间轴计算服务 | 1 天 |
| Step 4 | 扩展 LLM Prompt | 1 天 |
| Step 5 | 扩展 TTS 服务 | 1 天 |
| Step 6 | 集成主流程 | 0.5 天 |
| Step 7 | 渲染层适配 | 0.5 天 |
| Step 8 | 端到端测试与调优 | 1 天 |
| **总计** | | **5 天** |

---

## 9. 每日检查清单

### Day 1
- [ ] 验证 TTS 能力（word-level timestamps）
- [ ] 定义 Scene 模型新字段
- [ ] 执行数据库迁移

### Day 2
- [ ] 实现 TimelineCalculateService
- [ ] 用 mock 数据测试时间轴计算
- [ ] 单元测试

### Day 3
- [ ] 扩展 LLM Prompt
- [ ] 解析 emphasis_words
- [ ] 测试 LLM 输出成功率

### Day 4
- [ ] 扩展 TTS 服务
- [ ] 实现降级方案
- [ ] 测试 timestamps 获取成功率

### Day 5
- [ ] 集成主流程
- [ ] 渲染层适配
- [ ] 端到端测试
- [ ] 调优参数

---

**文档状态**：可执行开发任务列表
**下一步**：立即开始 Step 1（验证 TTS 能力）
**预计完成**：5 个工作日

