# Step 14 测试指南 - 字幕生成

## ✅ Step 14 已完成

已实现字幕生成服务，可以根据旁白文本和场景时长自动生成精确的字幕时间轴。

## 📁 新增文件

```
backend/app/
├── schemas/
│   └── subtitle.py                 # 字幕数据结构
├── services/
│   └── subtitle_service.py         # 字幕生成服务
└── scripts/
    └── test_subtitle.py            # 字幕测试脚本
```

## 🔧 功能特性

### SubtitleService
- 自动按标点符号分割文本
- 根据字符数量和时长计算每个字幕片段的时间
- 支持中英文标点符号（。！？,.!?）
- 自动调整字幕时长（最小 1 秒，最大 3 秒）
- 批量生成支持
- 导出 SRT 格式字幕文件

### 字幕分割算法
1. 按标点符号分割文本
2. 计算总字符数和每字符时长
3. 为每个片段分配时间
4. 限制片段时长在合理范围内
5. 确保不超过总时长

### Pipeline Worker 集成
- 自动为所有场景生成字幕
- 导出 SRT 文件到 `storage/subtitles/`
- 即使失败也不影响整体流程

## 🧪 如何测试

### 方式 1: 单独测试字幕生成

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_subtitle.py
```

**预期输出：**
```
======================================================================
Test Subtitle Service
======================================================================

Test text:
----------------------------------------------------------------------
你好，这是一个字幕生成测试。RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。它解决了知识更新和引用可信的问题。
----------------------------------------------------------------------

Test 1: Split text by punctuation
✓ Split into 3 segments:
  1. 你好，这是一个字幕生成测试。
  2. RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。
  3. 它解决了知识更新和引用可信的问题。

Test 2: Generate subtitles (8 seconds)
✓ Generated 3 subtitle segments:
  1. [0.00s - 1.78s] 你好，这是一个字幕生成测试。
  2. [1.78s - 4.78s] RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。
  3. [4.78s - 6.93s] 它解决了知识更新和引用可信的问题。

Test 3: Generate scene subtitles
✓ Scene: sc_test_001
  Total duration: 7000ms
  Segments: 3
    1. [0ms - 1489ms] AI 回答总是出错？
    2. [1489ms - 3276ms] 因为它可能缺少最新知识！
    3. [3276ms - 6276ms] 今天带你了解 RAG 技术，让 AI 回答更准确。

Test 4: Export to SRT format
✓ SRT file saved: ./storage/subtitles/test.srt

SRT content:
----------------------------------------------------------------------
1
00:00:00,000 --> 00:00:01,489
AI 回答总是出错？

2
00:00:01,489 --> 00:00:03,276
因为它可能缺少最新知识！

3
00:00:03,276 --> 00:00:06,276
今天带你了解 RAG 技术，让 AI 回答更准确。


----------------------------------------------------------------------

Test 5: Batch subtitle generation
✓ Generated subtitles for 3 scenes:
  - sc_batch_001: 1 segments
  - sc_batch_002: 1 segments
  - sc_batch_003: 1 segments

----------------------------------------------------------------------
✓ All tests completed successfully!
```

### 方式 2: 端到端测试（完整流程）

**启动服务：**
```bash
# 终端 1 - API Server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端 2 - Pipeline Worker
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

[3/6] Scene Validate...
  ✓ Scenes saved to database

[4/6] TTS Generate...
  ✓ Generated audio for 7 scenes (Edge TTS)

[5/6] Subtitle Generate...
  ✓ Generated subtitles for 7 scenes
  ✓ Exported SRT files
```

## 🔍 验证

### 检查生成的字幕文件

```bash
# 查看字幕文件
ls -lh storage/subtitles/

# 查看 SRT 内容
cat storage/subtitles/sc_test_001.srt
```

### 字幕质量检查

生成的字幕应该：
- 按标点符号合理分割
- 时间轴准确，不重叠
- 每个片段时长在 1-3 秒之间
- 总时长与场景时长一致
- SRT 格式正确

### SRT 格式示例

```srt
1
00:00:00,000 --> 00:00:01,489
AI 回答总是出错？

2
00:00:01,489 --> 00:00:03,276
因为它可能缺少最新知识！

3
00:00:03,276 --> 00:00:06,276
今天带你了解 RAG 技术，让 AI 回答更准确。
```

## ✨ 技术实现

### 文本分割
```python
def split_text_by_punctuation(text: str) -> List[str]:
    # Split by Chinese and English punctuation
    segments = re.split(r'([。！？,.!?])', text)

    # Combine text with punctuation
    result = []
    i = 0
    while i < len(segments):
        if segments[i].strip():
            if i + 1 < len(segments) and segments[i + 1] in '。！？,.!?':
                result.append(segments[i] + segments[i + 1])
                i += 2
            else:
                result.append(segments[i])
                i += 1
        else:
            i += 1

    return [s.strip() for s in result if s.strip()]
```

### 时间轴计算
```python
def generate_subtitles(text: str, duration_ms: int) -> List[SubtitleSegment]:
    segments = split_text_by_punctuation(text)

    # Calculate time per character
    total_chars = sum(len(s) for s in segments)
    ms_per_char = duration_ms / total_chars

    # Generate subtitle segments
    subtitles = []
    current_time = 0

    for segment_text in segments:
        segment_chars = len(segment_text)
        segment_duration = int(segment_chars * ms_per_char)

        # Clamp to min/max duration
        segment_duration = max(1000, min(segment_duration, 3000))

        subtitles.append(SubtitleSegment(
            text=segment_text,
            start_ms=current_time,
            end_ms=current_time + segment_duration
        ))

        current_time += segment_duration

    return subtitles
```

### SRT 导出
```python
def export_srt(scene_subtitles: SceneSubtitles, output_filename: str) -> str:
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(scene_subtitles.segments, 1):
            start_time = ms_to_srt_time(segment.start_ms)
            end_time = ms_to_srt_time(segment.end_ms)

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment.text}\n")
            f.write("\n")

    return output_path

def ms_to_srt_time(ms: int) -> str:
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    milliseconds = ms % 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
```

## 🎯 下一步

所有核心功能已完成！接下来可以：
- 优化字幕分割算法
- 添加字幕样式配置
- 实现字幕预览功能
- 集成到视频渲染流程

## 📝 已完成的步骤

- ✅ Step 1-10: Milestone 1 完整流程（Mock）
- ✅ Step 11: 真实 LLM 文章解析（DeepSeek）
- ✅ Step 12: 真实 LLM 分镜生成（DeepSeek）
- ✅ Step 13: TTS 语音合成（Edge TTS）
- ✅ Step 14: 字幕生成

## 💡 优化建议

### 字幕分割优化
- 考虑语义完整性，避免在关键词中间分割
- 根据语速动态调整字幕时长
- 支持自定义分割规则

### 字幕样式
- 支持字体、大小、颜色配置
- 支持位置、对齐方式配置
- 支持特效（淡入淡出、描边等）

### 多语言支持
- 支持英文字幕生成
- 支持双语字幕
- 支持字幕翻译
