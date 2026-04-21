# Tech Spec：Scene 表达力与节奏数据优化方案（完整版）

**文档版本**: v1.0
**创建日期**: 2026-04-21
**技术负责人**: 系统架构师
**文档状态**: 可执行技术方案

---

## 1. 技术目标

### 1.1 系统需要支撑的能力
- **阶段 1**: LLM 标注重点词 + TTS 时间戳 + 自动计算时间轴 + 渲染强调动效
- **阶段 2**: 根据场景类型应用预设节奏规则（Hook/解释/对比）
- **阶段 3**: 前端时间轴编辑器，用户可视化调整节奏

### 1.2 非功能需求
- **性能**: 时间轴计算延迟 < 500ms，编辑器响应 < 100ms
- **稳定性**: LLM 输出成功率 ≥ 90%
- **精度**: 音频视觉同步误差 < 300ms
- **扩展性**: 支持后续增加新动效类型，不改 Schema

---

## 2. 系统整体架构

### 2.1 架构类型
**模块化单体架构**（不做微服务拆分）

### 2.2 三阶段架构演进

```
阶段 1（MVP）:
├── 后端服务
│   ├── SceneGenerateService（扩展）
│   ├── TTSService（扩展）
│   ├── TimelineCalculateService（新增）
│   └── RenderService（微调）
└── 前端：无改动

阶段 2（节奏规则）:
├── 后端服务
│   └── TimelineCalculateService（扩展规则引擎）
└── 前端：无改动

阶段 3（编辑器）:
├── 后端服务
│   ├── TimelineUpdateAPI（新增）
│   └── PreviewService（新增）
└── 前端
    ├── TimelineEditor 组件（新增）
    ├── KeyframeTrack 组件（新增）
    └── EffectSelector 组件（新增）
```

## 3. 阶段 1：MVP（后端为主，5 天）

### 3.1 核心模块设计

#### 模块 1: SceneGenerateService 扩展

**职责**: 让 LLM 标注每个场景的重点词

**输入**:
```python
{
    "article_content": str,
    "hook": str,
    "narrative_structure": dict
}
```

**输出**:
```python
{
    "scenes": [
        {
            "voiceover": "这个方法能让你的效率提升 3 倍",
            "screen_text": ["方法", "效率提升"],
            "emphasis_words": ["方法", "效率", "3 倍"],  # 新增
            "duration_sec": 8,
            "pace": "medium"
        }
    ]
}
```

**内部逻辑**:
1. 构建 Prompt，增加 `emphasis_words` 标注要求
2. 调用 LLM API
3. 解析 JSON，校验 `emphasis_words`（2-3 个词）
4. 失败重试 3 次，仍失败则降级为空数组

**依赖**: LLM API（Claude Opus 4.5）

**代码位置**: `src/services/scene_generate_service.py`

#### 模块 2: TTSService 扩展

**职责**: 调用 TTS API 生成音频，并获取 word-level timestamps

**输入**:
```python
{"text": "这个方法能让你的效率提升 3 倍", "voice": "zh-CN-XiaoxiaoNeural"}
```

**输出**:
```python
{
    "audio_url": "https://...",
    "duration_sec": 8.2,
    "word_timestamps": [
        {"word": "这个", "start": 0.0, "end": 0.3},
        {"word": "方法", "start": 0.3, "end": 0.7},
        {"word": "效率", "start": 1.4, "end": 1.8},
        {"word": "3倍", "start": 2.2, "end": 2.7}
    ]
}
```

**内部逻辑**:
1. 调用 TTS API，请求 `return_word_timestamps=True`
2. 如果不支持，调用 forced alignment 工具（Gentle）
3. 如果都不支持，降级：按字数均匀分布估算

**依赖**: Azure TTS / ElevenLabs

**代码位置**: `src/services/tts_service.py`

**关键风险**: TTS 服务可能不支持 word-level timestamps，需立即验证

#### 模块 3: TimelineCalculateService（新增）

**职责**: 根据 TTS timestamps 和 emphasis_words 计算时间轴

**输入**:
```python
{
    "scene": {"voiceover": "...", "emphasis_words": ["方法", "效率", "3倍"]},
    "tts_metadata": {"word_timestamps": [...]}
}
```

**输出**:
```python
{
    "timeline_data": [
        {"time": 0.2, "element": "方法", "action": "pop", "duration": 0.3},
        {"time": 1.3, "element": "效率", "action": "pop", "duration": 0.3}
    ]
}
```

**内部逻辑**:
1. 遍历 `emphasis_words`，在 TTS timestamps 中查找时间点
2. 提前 0.1 秒显示（预判）
3. 为 `screen_text` 生成均匀分布的出现时机
4. 按时间排序

**依赖**: 无（纯计算）

**代码位置**: `src/services/timeline_calculate_service.py`（新建）

---

## 4. 阶段 2：节奏规则（后端扩展，3 天）

### 4.1 核心改动

### 4.2 节奏规则引擎

**扩展模块**: TimelineCalculateService

**新增功能**: 根据 `scene.scene_type` 应用不同节奏规则

**规则定义**:
```python
RHYTHM_RULES = {
    "hook": {
        "emphasis_density": "high",      # 关键词密集出现
        "effect_speed": "fast",          # 快速动效（duration=0.2）
        "pause_after": True              # 结尾停顿
    },
    "explanation": {
        "emphasis_density": "medium",    # 关键词均匀分布
        "effect_speed": "medium",        # 中速动效（duration=0.3）
        "pause_after": False
    },
    "contrast": {
        "emphasis_density": "paired",    # 关键词成对出现
        "effect_speed": "alternating",   # 交替动效（快慢交替）
        "pause_after": False
    }
}
```

**实现逻辑**:
```python
def calculate_with_rhythm(scene, tts_metadata):
    # 获取场景类型的节奏规则
    rule = RHYTHM_RULES.get(scene.scene_type, RHYTHM_RULES["explanation"])

    # 应用规则调整时间轴
    timeline = calculate_timeline(scene, tts_metadata)
    timeline = apply_rhythm_rule(timeline, rule)

    return timeline
```

**代码位置**: `src/services/timeline_calculate_service.py`（扩展）

---

## 5. 阶段 3：可视化编辑器（前端为主，5 天）

### 5.1 前端架构设计

**技术栈**:
- React 18 + TypeScript
- Zustand（状态管理）
- Framer Motion（动画）
- WaveSurfer.js（音频波形显示）

**组件树**:
```
TimelineEditorPage
├── AudioWaveform（音频波形）
├── TimelineEditor（时间轴编辑器）
│   ├── TimelineRuler（时间刻度尺）
│   ├── KeyframeTrack（关键帧轨道）
│   │   └── KeyframeMarker（关键帧标记）
│   └── PlayheadCursor（播放头）
├── EmphasisWordSelector（重点词选择器）
├── EffectSelector（动效选择器）
└── PreviewPanel（预览面板）
```

### 5.2 核心组件设计

#### 组件 1: TimelineEditor（时间轴编辑器）

**职责**: 显示时间轴，支持拖拽调整关键帧

**Props**:
```typescript
interface TimelineEditorProps {
  sceneId: string;
  duration: number;           // 场景总时长（秒）
  keyframes: Keyframe[];      // 关键帧列表
  audioUrl: string;           // 音频 URL
  onKeyframeUpdate: (keyframes: Keyframe[]) => void;
}

interface Keyframe {
  id: string;
  time: number;               // 时间点（秒）
  element: string;            // 元素内容
  action: 'pop' | 'fade_in' | 'slide_in';
  duration: number;
}
```

**功能**:
1. 显示时间刻度尺（0-duration 秒）
2. 显示音频波形（WaveSurfer.js）
3. 显示关键帧标记（可拖拽）
4. 拖拽关键帧时实时更新时间
5. 播放音频时，播放头同步移动

**交互**:
- 拖拽关键帧：调整出现时机
- 点击关键帧：选中，显示详情面板
- 双击时间轴：添加新关键帧

**代码位置**: `src/components/TimelineEditor/TimelineEditor.tsx`

#### 组件 2: EmphasisWordSelector（重点词选择器）

**职责**: 让用户点击词语标记为重点词

**Props**:
```typescript
interface EmphasisWordSelectorProps {
  voiceover: string;
  emphasisWords: string[];
  onEmphasisWordsChange: (words: string[]) => void;
}
```

**功能**:
1. 将 voiceover 分词显示
2. 点击词语，标记为重点词（高亮显示）
3. 再次点击，取消标记
4. 最多选择 3 个词

**UI 设计**:
```
旁白：这个 [方法] 能让你的 [效率] 提升 [3倍]
      ↑ 已选中（蓝色背景）
```

**代码位置**: `src/components/TimelineEditor/EmphasisWordSelector.tsx`

---

#### 组件 3: EffectSelector（动效选择器）

**职责**: 让用户选择动效类型

**Props**:
```typescript
interface EffectSelectorProps {
  selectedKeyframe: Keyframe | null;
  onEffectChange: (action: string) => void;
}
```

**功能**:
1. 显示 3 种动效选项：pop / fade_in / slide_in
2. 每个选项显示预览动画
3. 点击选项，应用到选中的关键帧

**UI 设计**:
```
动效类型：
[ Pop ]  [ Fade In ]  [ Slide In ]
  ↑ 当前选中
```

**代码位置**: `src/components/TimelineEditor/EffectSelector.tsx`

### 5.3 后端 API 设计

#### API 1: 更新时间轴

**端点**: `PUT /api/scenes/{scene_id}/timeline`

**请求**:
```json
{
  "emphasis_words": ["方法", "效率", "3倍"],
  "timeline_data": [
    {"time": 0.5, "element": "方法", "action": "pop", "duration": 0.3},
    {"time": 2.0, "element": "效率", "action": "fade_in", "duration": 0.4}
  ]
}
```

**响应**:
```json
{
  "success": true,
  "scene_id": "scene_123",
  "updated_at": "2026-04-21T10:30:00Z"
}
```

**职责**: 保存用户编辑的时间轴数据

**代码位置**: `src/api/timeline_api.py`（新建）

---

#### API 2: 预览视频片段

**端点**: `POST /api/scenes/{scene_id}/preview`

**请求**:
```json
{
  "start_time": 0,
  "end_time": 5
}
```

**响应**:
```json
{
  "preview_url": "https://.../preview.mp4",
  "duration": 5
}
```

**职责**: 生成指定时间段的预览视频（快速渲染）

**代码位置**: `src/api/preview_api.py`（新建）

---

## 6. 数据流设计（完整三阶段）

### 6.1 阶段 1 数据流

```
用户输入 → SceneGenerateService（LLM 标注 emphasis_words）
         → TTSService（获取 word_timestamps）
         → TimelineCalculateService（计算时间轴）
         → RenderService（渲染视频）
         → 返回视频
```

### 6.2 阶段 2 数据流

```
用户输入 → SceneGenerateService（LLM 标注 + scene_type）
         → TTSService
         → TimelineCalculateService（应用节奏规则）
         → RenderService
         → 返回视频
```

### 6.3 阶段 3 数据流

```
用户输入 → 生成视频（阶段 1/2 流程）
         → 前端显示编辑器
         → 用户拖拽调整关键帧
         → PUT /api/scenes/{id}/timeline（保存修改）
         → POST /api/scenes/{id}/preview（预览）
         → 用户确认 → 重新渲染最终视频
```

## 7. 异常处理机制

### 7.1 阶段 1 异常处理

**LLM 输出异常**:
- 重试 3 次
- 仍失败则降级：`emphasis_words = []`
- 记录日志，继续流程

**TTS 不支持 timestamps**:
- 尝试 forced alignment 工具（Gentle）
- 仍失败则降级：按字数均匀分布估算
- 记录日志，继续流程

**词匹配失败**:
- 尝试模糊匹配
- 仍失败则跳过该词
- 记录日志，继续流程

### 7.2 阶段 3 异常处理

**前端编辑器加载失败**:
- 显示错误提示："编辑器加载失败，请刷新页面"
- 提供"跳过编辑"按钮，直接使用自动生成的时间轴

**预览生成超时**:
- 超时时间：30 秒
- 超时后显示："预览生成中，请稍后刷新"
- 后台继续生成，用户可以稍后查看

**保存时间轴失败**:
- 重试 2 次
- 仍失败则显示错误提示
- 本地缓存用户修改，避免丢失

---

## 8. 性能优化

### 8.1 前端性能优化

**虚拟滚动**:
- 如果关键帧 > 50 个，使用虚拟滚动
- 只渲染可见区域的关键帧

**防抖处理**:
- 拖拽关键帧时，300ms 防抖后才保存
- 避免频繁调用 API

**音频波形缓存**:
- 使用 IndexedDB 缓存音频波形数据
- 避免重复计算

### 8.2 后端性能优化

**预览视频缓存**:
- 预览视频缓存 10 分钟
- 相同参数的预览请求直接返回缓存

**时间轴计算缓存**:
- 计算结果缓存到 Redis（1 小时）
- Key: `timeline:{scene_id}:{tts_metadata_hash}`

---

## 9. 实施计划（13 天）

### 阶段 1：MVP（5 天）

**Day 1**:
- [ ] 验证 TTS 能力（word-level timestamps）
- [ ] Scene 模型增加字段
- [ ] 数据库迁移

**Day 2**:
- [ ] SceneGenerateService 扩展 Prompt
- [ ] 增加 emphasis_words 解析
- [ ] 单元测试

**Day 3**:
- [ ] TTSService 扩展（timestamps 提取）
- [ ] 实现降级方案
- [ ] 单元测试

**Day 4**:
- [ ] TimelineCalculateService 实现
- [ ] 词匹配算法
- [ ] 单元测试

**Day 5**:
- [ ] RenderService 适配
- [ ] 集成测试
- [ ] 性能测试

### 阶段 2：节奏规则（3 天）

**Day 6**:
- [ ] 定义节奏规则（RHYTHM_RULES）
- [ ] TimelineCalculateService 增加规则引擎
- [ ] 单元测试

**Day 7**:
- [ ] 实现 3 种节奏规则（hook/explanation/contrast）
- [ ] 集成测试

**Day 8**:
- [ ] 调优规则参数
- [ ] 人工测试 20 个视频
- [ ] 修复问题

### 阶段 3：可视化编辑器（5 天）

**Day 9**:
- [ ] 前端：TimelineEditor 组件骨架
- [ ] 前端：时间刻度尺 + 音频波形
- [ ] 后端：TimelineUpdateAPI

**Day 10**:
- [ ] 前端：KeyframeTrack + 拖拽功能
- [ ] 前端：Zustand 状态管理
- [ ] 集成前后端

**Day 11**:
- [ ] 前端：EmphasisWordSelector 组件
- [ ] 前端：EffectSelector 组件
- [ ] 交互联调

**Day 12**:
- [ ] 后端：PreviewService 实现
- [ ] 前端：PreviewPanel 组件
- [ ] 集成测试

**Day 13**:
- [ ] 性能优化（虚拟滚动、防抖、缓存）
- [ ] UI 优化
- [ ] 端到端测试

---

## 10. 验收标准

### 阶段 1 验收标准

**技术指标**:
- LLM 输出成功率 ≥ 90%
- TTS timestamps 获取成功率 ≥ 95%
- 词匹配成功率 ≥ 80%
- 音频视觉同步误差 < 300ms

**业务指标**:
- 用户认为"关键信息被强调"的比例 ≥ 60%
- 用户修改率下降 ≥ 5%

### 阶段 2 验收标准

**业务指标**:
- 用户认为"节奏有起伏"的比例 ≥ 50%
- 用户修改率下降 ≥ 10%

### 阶段 3 验收标准

**技术指标**:
- 编辑器加载时间 < 2 秒
- 拖拽响应延迟 < 100ms
- 预览生成时间 < 10 秒

**业务指标**:
- 使用编辑器的用户比例 ≥ 20%
- 使用编辑器后的满意度 ≥ 4.5 分

---

## 11. 风险与降级方案

### 风险 1: TTS 不支持 word-level timestamps

**影响**: 无法获取精确时间点

**降级方案**:
1. 使用 forced alignment 工具（Gentle）
2. 按字数均匀分布估算
3. 最坏情况：不做重点词强调

**验证**: Day 1 立即测试

### 风险 2: 前端编辑器性能差

**影响**: 拖拽卡顿，用户体验差

**降级方案**:
1. 限制关键帧数量 < 20 个
2. 使用虚拟滚动
3. 最坏情况：简化编辑器功能

**验证**: Day 13 性能测试

### 风险 3: 预览生成太慢

**影响**: 用户等待时间长

**降级方案**:
1. 降低预览视频分辨率（720p → 480p）
2. 只渲染关键帧附近 ±1 秒
3. 最坏情况：不提供预览，直接渲染最终视频

**验证**: Day 12 性能测试

---

## 12. 技术选型总结

| 模块 | 技术选择 | 理由 |
|------|---------|------|
| 后端框架 | FastAPI | 现有技术栈 |
| 数据库 | PostgreSQL | 现有技术栈 |
| 缓存 | Redis | 时间轴计算结果缓存 |
| TTS 服务 | Azure TTS | 支持 word-level timestamps（需验证） |
| 前端框架 | React 18 + TypeScript | 现有技术栈 |
| 状态管理 | Zustand | 轻量级，适合编辑器场景 |
| 音频波形 | WaveSurfer.js | 成熟的音频可视化库 |
| 动画库 | Framer Motion | 流畅的拖拽动画 |

---

## 13. 代码示例

### 13.1 TimelineEditor 组件（核心代码）

```typescript
// src/components/TimelineEditor/TimelineEditor.tsx

import { useState, useRef, useEffect } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { useTimelineStore } from '@/stores/timelineStore';

export function TimelineEditor({ sceneId, duration, audioUrl }: Props) {
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);
  const { keyframes, updateKeyframe } = useTimelineStore();

  // 初始化音频波形
  useEffect(() => {
    if (waveformRef.current) {
      wavesurfer.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#ddd',
        progressColor: '#3b82f6',
        height: 80
      });
      wavesurfer.current.load(audioUrl);
    }
  }, [audioUrl]);

  // 处理关键帧拖拽
  const handleKeyframeDrag = (keyframeId: string, newTime: number) => {
    updateKeyframe(keyframeId, { time: newTime });
  };

  return (
    <div className="timeline-editor">
      <div ref={waveformRef} className="waveform" />
      <div className="keyframe-track">
        {keyframes.map(kf => (
          <KeyframeMarker
            key={kf.id}
            keyframe={kf}
            duration={duration}
            onDrag={(newTime) => handleKeyframeDrag(kf.id, newTime)}
          />
        ))}
      </div>
    </div>
  );
}
```

### 13.2 TimelineUpdateAPI（后端）

```python
# src/api/timeline_api.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TimelineUpdateRequest(BaseModel):
    emphasis_words: list[str]
    timeline_data: list[dict]

@router.put("/scenes/{scene_id}/timeline")
async def update_timeline(scene_id: str, request: TimelineUpdateRequest):
    # 查询场景
    scene = await Scene.get(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    # 更新数据
    scene.emphasis_words = request.emphasis_words
    scene.timeline_data = request.timeline_data
    await scene.save()

    return {
        "success": True,
        "scene_id": scene_id,
        "updated_at": scene.updated_at
    }
```

---

## 14. 监控指标

### 14.1 关键指标

```python
# 需要监控的指标
METRICS = {
    # 阶段 1
    'llm_success_rate': 'LLM 输出成功率',
    'tts_timestamp_success_rate': 'TTS timestamps 获取成功率',
    'word_match_success_rate': '词匹配成功率',
    'timeline_calculate_latency': '时间轴计算延迟',

    # 阶段 3
    'editor_load_time': '编辑器加载时间',
    'keyframe_drag_latency': '关键帧拖拽延迟',
    'preview_generate_time': '预览生成时间',
    'timeline_save_success_rate': '时间轴保存成功率'
}
```

### 14.2 告警规则

- LLM 成功率 < 90%：立即告警
- 编辑器加载时间 > 5 秒：告警
- 预览生成时间 > 30 秒：告警

---

**文档状态**: 可执行技术方案
**下一步**: 产品确认后，立即开始 Day 1 任务
**预计完成**: 13 个工作日

