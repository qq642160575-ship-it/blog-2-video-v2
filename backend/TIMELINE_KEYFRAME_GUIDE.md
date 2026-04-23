# 时间轴关键帧功能说明

## 问题分析

你遇到的三个问题：

### 1. 关键帧只有一个

**原因**：场景缺少必要的数据
- ❌ `emphasis_words` 为 null（没有关键词）
- ❌ `tts_metadata` 为 null（没有 TTS 时间戳）
- ❌ `timeline_data` 为 null（没有时间轴数据）

**解决方案**：需要先生成这些数据

```bash
# 更新场景的关键词
curl -X PUT "http://localhost:8000/scenes/{scene_id}/timeline" \
  -H "Content-Type: application/json" \
  -d '{
    "emphasis_words": ["AI模型", "天差地别", "为什么"]
  }'
```

**注意**：这需要场景有 `tts_metadata`。如果没有，需要先运行 TTS 生成。

### 2. 字幕消失了

**原因**：
- Remotion 模板需要 `subtitles` prop
- 之前的 PreviewService 没有传递字幕数据

**已修复**：
- ✅ 添加了 `_generate_subtitles_from_voiceover()` 方法
- ✅ 从 `voiceover` 文本自动生成字幕
- ✅ 如果有 `tts_metadata`，使用精确的词级时间戳
- ✅ 否则，按标点符号分段并估算时间

### 3. 关键帧不起作用（视频没有区别）

**原因**：
- Remotion 模板只有简单的淡入动画
- 没有实现基于 `timeline_data` 的关键帧效果

**已修复**：
- ✅ 更新 HookTitle 组件支持 `timeline` prop
- ✅ 实现 `getKeyframeEffect()` 函数
- ✅ 关键词高亮时：
  - 放大 1.2 倍（pop 效果）
  - 颜色变为金色 (#ffd700)
  - 持续时间由 timeline_data 控制

## 完整工作流程

### 步骤 1: 生成场景（带 TTS）

场景生成时需要包含 TTS 处理：

```python
# 在生成流程中
scene_data = {
    "voiceover": "为什么同样的AI模型，有人能写出惊艳的文案...",
    "screen_text": ["AI模型相同", "结果天差地别", "为什么？"],
    # ... 其他字段
}

# 调用 TTS 服务
tts_result = tts_service.generate(scene_data["voiceover"])

# 保存 TTS 元数据
scene.tts_metadata = {
    "word_timestamps": [
        {"word": "为什么", "start_time": 0.0, "end_time": 0.5},
        {"word": "同样", "start_time": 0.5, "end_time": 0.8},
        {"word": "的", "start_time": 0.8, "end_time": 0.9},
        {"word": "AI", "start_time": 0.9, "end_time": 1.2},
        {"word": "模型", "start_time": 1.2, "end_time": 1.6},
        # ... 更多词
    ]
}
```

### 步骤 2: 设置关键词

通过 API 设置需要强调的关键词：

```bash
curl -X PUT "http://localhost:8000/scenes/sc_proj_21c89dcb_001/timeline" \
  -H "Content-Type: application/json" \
  -d '{
    "emphasis_words": ["AI模型", "惊艳", "平庸"]
  }'
```

这会自动：
1. 在 `tts_metadata.word_timestamps` 中查找这些词
2. 计算每个词的触发时间
3. 生成 `timeline_data`：

```json
{
  "keyframes": [
    {
      "time": 0.8,
      "element": "AI模型",
      "action": "pop",
      "duration": 0.3,
      "word_start": 0.9,
      "word_end": 1.6
    },
    {
      "time": 2.5,
      "element": "惊艳",
      "action": "pop",
      "duration": 0.3,
      "word_start": 2.6,
      "word_end": 3.0
    }
  ]
}
```

### 步骤 3: 生成预览

```bash
curl -X POST "http://localhost:8000/scenes/sc_proj_21c89dcb_001/preview" \
  -H "Content-Type: application/json" \
  -d '{"quality": "low"}'
```

预览视频会包含：
- ✅ 字幕（从 voiceover 生成）
- ✅ 关键词高亮效果（如果有 timeline_data）
- ✅ 基础动画（淡入等）

## 当前场景的问题

你的场景 `sc_proj_21c89dcb_001` 缺少：

```json
{
  "emphasis_words": null,  // ❌ 需要设置
  "tts_metadata": null,    // ❌ 需要 TTS 生成
  "timeline_data": null    // ❌ 会在设置 emphasis_words 后自动生成
}
```

## 解决方案

### 方案 A: 手动添加 TTS 元数据（用于测试）

```bash
# 1. 手动设置 TTS 元数据（模拟）
curl -X PATCH "http://localhost:8000/scenes/sc_proj_21c89dcb_001" \
  -H "Content-Type: application/json" \
  -d '{
    "tts_metadata": {
      "word_timestamps": [
        {"word": "为什么", "start_time": 0.0, "end_time": 0.4},
        {"word": "同样", "start_time": 0.4, "end_time": 0.7},
        {"word": "的", "start_time": 0.7, "end_time": 0.8},
        {"word": "AI", "start_time": 0.8, "end_time": 1.0},
        {"word": "模型", "start_time": 1.0, "end_time": 1.4},
        {"word": "有人", "start_time": 1.5, "end_time": 1.8},
        {"word": "能", "start_time": 1.8, "end_time": 2.0},
        {"word": "写出", "start_time": 2.0, "end_time": 2.3},
        {"word": "惊艳", "start_time": 2.3, "end_time": 2.7},
        {"word": "的", "start_time": 2.7, "end_time": 2.8},
        {"word": "文案", "start_time": 2.8, "end_time": 3.2},
        {"word": "有人", "start_time": 3.3, "end_time": 3.6},
        {"word": "却", "start_time": 3.6, "end_time": 3.8},
        {"word": "只能", "start_time": 3.8, "end_time": 4.1},
        {"word": "得到", "start_time": 4.1, "end_time": 4.4},
        {"word": "平庸", "start_time": 4.4, "end_time": 4.8},
        {"word": "的", "start_time": 4.8, "end_time": 4.9},
        {"word": "回答", "start_time": 4.9, "end_time": 5.3}
      ]
    }
  }'

# 2. 设置关键词（会自动生成 timeline_data）
curl -X PUT "http://localhost:8000/scenes/sc_proj_21c89dcb_001/timeline" \
  -H "Content-Type: application/json" \
  -d '{
    "emphasis_words": ["AI模型", "惊艳", "平庸"]
  }'

# 3. 生成预览
curl -X POST "http://localhost:8000/scenes/sc_proj_21c89dcb_001/preview" \
  -H "Content-Type: application/json" \
  -d '{"quality": "low"}'
```

### 方案 B: 重新生成场景（推荐）

重新运行完整的生成流程，确保包含 TTS 处理：

```bash
# 创建新项目并生成场景
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "article_url": "https://example.com/article",
    "style": "educational"
  }'
```

## 测试关键帧效果

生成预览后，你应该看到：

1. **字幕显示**：底部黑色背景的字幕条
2. **关键词高亮**：
   - "AI模型" 在 ~1.0s 时放大并变金色
   - "惊艳" 在 ~2.3s 时放大并变金色
   - "平庸" 在 ~4.4s 时放大并变金色
3. **动画效果**：每个关键词持续 0.3 秒的 pop 效果

## 重启服务器

修改代码后需要重启：

```bash
# 如果使用 uvicorn --reload，会自动重启
# 否则手动重启：
pkill -f "uvicorn app.main:app"
uvicorn app.main:app --reload --port 8000
```

## 验证修复

```bash
# 1. 检查场景数据
curl "http://localhost:8000/scenes/sc_proj_21c89dcb_001" | jq '{
  emphasis_words,
  has_tts: (.tts_metadata != null),
  has_timeline: (.timeline_data != null)
}'

# 2. 查看 timeline_data
curl "http://localhost:8000/scenes/sc_proj_21c89dcb_001" | jq '.timeline_data'

# 3. 生成预览
curl -X POST "http://localhost:8000/scenes/sc_proj_21c89dcb_001/preview" \
  -H "Content-Type: application/json" \
  -d '{"quality": "low"}'

# 4. 检查生成的 manifest
cat storage/previews/sc_proj_21c89dcb_001_preview_manifest.json | jq '.'
```

## 下一步优化

1. **更精细的关键词匹配**：支持部分匹配和多词组合
2. **更多动画效果**：除了 pop，还可以有 slide、fade、bounce 等
3. **关键词分组**：同时高亮多个相关词
4. **自定义颜色**：根据情感或重要性使用不同颜色
5. **音频同步**：添加音频文件支持，实现真正的音画同步
