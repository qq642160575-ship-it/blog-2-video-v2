# Step 13 测试指南 - TTS 语音合成

## ✅ Step 13 已完成

已接入 TTS 服务（Edge TTS），可以将旁白文本转换为高质量的中文语音。

**注意：** 目前使用 Edge TTS（微软免费 TTS 服务），完全免费，无需 API Key。

## 📁 新增文件

```
backend/
├── app/services/
│   └── tts_service.py              # TTS 服务（Edge TTS）
├── scripts/
│   └── test_tts.py                 # TTS 测试脚本
└── requirements.txt                # 添加 edge-tts 依赖
```

## 🔧 功能特性

### TTSService
- 使用 Edge TTS（微软免费服务）
- **完全免费，无需 API Key**
- 支持中文语音合成（默认：zh-CN-XiaoxiaoNeural）
- 支持语速调节（0.5-2.0倍速）
- 输出格式：MP3
- 批量合成支持
- 自动根据场景节奏调整语速：
  - fast → 1.2x
  - medium → 1.0x
  - slow → 0.85x

### Pipeline Worker 集成
- 自动尝试使用 Edge TTS
- 如果 TTS 调用失败（网络问题等），自动降级到 Mock
- 保证系统稳定性

## 🧪 如何测试

### 方式 1: 单独测试 TTS

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_tts.py
```

**预期输出（成功）：**
```
======================================================================
Test TTS Service (Edge TTS - Free)
======================================================================

Test text:
----------------------------------------------------------------------
你好，这是一个语音合成测试。RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。
----------------------------------------------------------------------

Synthesizing speech with Edge TTS (Free, no API key needed)...

Test 1: Basic synthesis (normal speed)
✓ Audio generated: storage/audio/test_normal.mp3

Test 2: Fast pace synthesis
✓ Audio generated: storage/audio/test_fast.mp3

Test 3: Slow pace synthesis
✓ Audio generated: storage/audio/test_slow.mp3

Test 4: Scene audio synthesis
✓ Scene audio generated: storage/audio/sc_test_001.mp3

Test 5: Batch synthesis
✓ Generated 3 audio files:
  - sc_batch_001: storage/audio/sc_batch_001.mp3
  - sc_batch_002: storage/audio/sc_batch_002.mp3
  - sc_batch_003: storage/audio/sc_batch_003.mp3

----------------------------------------------------------------------
✓ All tests completed successfully!

Audio files saved to: storage/audio/

Note: Edge TTS is completely FREE and requires no API key!
```

**如果遇到网络问题：**
Edge TTS 可能因为网络限制返回 403 错误。这种情况下，Pipeline Worker 会自动降级到 Mock 模式，不影响系统运行。

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
```

如果看到 `(Edge TTS)` 标记，说明使用了真实 TTS。
如果看到 `(Mock fallback)` 标记，说明 TTS 失败，降级到了 Mock。

## 🔍 验证

### 检查是否使用了真实 TTS

1. 查看 Pipeline Worker 日志，确认有 `(Edge TTS)` 标记
2. 检查 `storage/audio/` 目录，确认生成了 MP3 文件
3. 播放音频文件，验证语音质量

### 音频质量检查

生成的音频应该：
- 格式：MP3
- 语音清晰、自然
- 语速符合场景节奏（fast/medium/slow）
- 中文发音准确

### 播放音频文件

```bash
# Linux
mpg123 storage/audio/test_normal.mp3

# macOS
afplay storage/audio/test_normal.mp3

# 或使用任何音频播放器
```

## ✨ 技术实现

### Edge TTS 集成
```python
import edge_tts
import asyncio

async def synthesize_async(text, output_path, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

# Sync wrapper
asyncio.run(synthesize_async(text, path, voice, rate))
```

### 语速控制
```python
# Convert speaking_rate to percentage
# 1.0 = +0%, 1.2 = +20%, 0.85 = -15%
rate_percent = int((speaking_rate - 1.0) * 100)
rate_str = f"{rate_percent:+d}%"
```

### 批量合成
```python
def synthesize_batch(scenes):
    results = {}
    for scene in scenes:
        audio_path = synthesize_scene_audio(
            scene_id=scene["scene_id"],
            voiceover=scene["voiceover"],
            pace=scene["pace"]
        )
        results[scene_id] = audio_path
    return results
```

## 💡 关于 Edge TTS

### 优点
- **完全免费**，无限制使用
- 无需注册账号或 API Key
- 语音质量接近 Azure Speech
- 支持多种中文语音
- 集成简单

### 缺点
- 非官方 API，可能不稳定
- 依赖微软服务器，可能有网络限制
- 没有官方技术支持

### 支持的中文语音

- `zh-CN-XiaoxiaoNeural` - 女声，温柔自然（默认）
- `zh-CN-YunxiNeural` - 男声，沉稳专业
- `zh-CN-YunyangNeural` - 男声，新闻播报风格
- `zh-CN-XiaoyiNeural` - 女声，活泼可爱

## 🎯 下一步：Step 14

接入字幕生成服务，根据音频时长和文本生成精确的字幕时间轴。

## 📝 已完成的步骤

- ✅ Step 1-10: Milestone 1 完整流程（Mock）
- ✅ Step 11: 真实 LLM 文章解析
- ✅ Step 12: 真实 LLM 分镜生成
- ✅ Step 13: TTS 语音合成（Edge TTS）
- ⏳ Step 14: 字幕生成

## 🔧 故障排除

### 如果 Edge TTS 返回 403 错误

这通常是网络限制导致的。解决方案：

1. **使用代理**：配置 HTTP/HTTPS 代理
2. **等待重试**：有时是临时限制，稍后再试
3. **接受 Mock 模式**：系统会自动降级，不影响开发

系统已经实现了自动降级机制，即使 TTS 失败也不会影响整体流程。

## 📁 新增文件

```
backend/
├── app/services/
│   └── tts_service.py              # TTS 服务（Azure Speech SDK）
├── scripts/
│   └── test_tts.py                 # TTS 测试脚本
└── requirements.txt                # 添加 azure-cognitiveservices-speech
```

## 🔧 功能特性

### TTSService
- 使用 Azure Cognitive Services Speech SDK
- 支持中文语音合成（默认：zh-CN-XiaoxiaoNeural）
- 支持语速调节（0.5-2.0倍速）
- 支持 SSML 标记语言
- 输出格式：16kHz, 16-bit, Mono WAV
- 批量合成支持
- 自动根据场景节奏调整语速：
  - fast → 1.2x
  - medium → 1.0x
  - slow → 0.85x

### Pipeline Worker 集成
- 优先使用真实 Azure Speech
- 如果 API Key 未配置，自动降级到 Mock
- 如果 TTS 调用失败，自动降级到 Mock
- 保证系统稳定性

## 🧪 如何测试

### 前提条件

需要配置 Azure Speech API Key：

```bash
# 编辑 .env 文件
cd backend
nano .env

# 添加或修改以下行
AZURE_SPEECH_KEY=your-azure-speech-key-here
AZURE_SPEECH_REGION=eastus  # 或其他区域
```

**如何获取 Azure Speech Key：**
1. 访问 [Azure Portal](https://portal.azure.com)
2. 创建 "Speech Services" 资源
3. 在 "Keys and Endpoint" 中获取 Key 和 Region

### 方式 1: 单独测试 TTS

**运行测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_tts.py
```

**预期输出：**
```
======================================================================
Test TTS Service (Azure Speech)
======================================================================

Azure Speech Region: eastus

Test text:
----------------------------------------------------------------------
你好，这是一个语音合成测试。RAG 技术通过结合检索和生成，显著提升了 AI 系统的准确性。
----------------------------------------------------------------------

Synthesizing speech...

Test 1: Basic synthesis (normal speed)
✓ Audio generated: storage/audio/test_normal.wav

Test 2: Fast pace synthesis
✓ Audio generated: storage/audio/test_fast.wav

Test 3: Slow pace synthesis
✓ Audio generated: storage/audio/test_slow.wav

Test 4: Scene audio synthesis
✓ Scene audio generated: storage/audio/sc_test_001.wav

Test 5: Batch synthesis
✓ Generated 3 audio files:
  - sc_batch_001: storage/audio/sc_batch_001.wav
  - sc_batch_002: storage/audio/sc_batch_002.wav
  - sc_batch_003: storage/audio/sc_batch_003.wav

----------------------------------------------------------------------
✓ All tests completed successfully!

Audio files saved to: storage/audio/
```

### 方式 2: 端到端测试（完整流程）

**启动服务：**
```bash
# 终端 1 - API Server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端 2 - Pipeline Worker（会自动使用 TTS）
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
  ✓ Generated audio for 7 scenes (Real TTS)
```

如果看到 `(Real TTS)` 标记，说明使用了真实 Azure Speech。

## 🔍 验证

### 检查是否使用了真实 TTS

1. 查看 Pipeline Worker 日志，确认有 `(Real TTS)` 标记
2. 检查 `storage/audio/` 目录，确认生成了 WAV 文件
3. 播放音频文件，验证语音质量
4. 观察处理时间：真实 TTS 调用需要 5-15 秒，Mock 只需 1 秒

### 音频质量检查

生成的音频应该：
- 格式：WAV (16kHz, 16-bit, Mono)
- 语音清晰、自然
- 语速符合场景节奏（fast/medium/slow）
- 中文发音准确
- 无明显机器感

### 播放音频文件

```bash
# Linux
aplay storage/audio/test_normal.wav

# macOS
afplay storage/audio/test_normal.wav

# 或使用任何音频播放器
```

## ✨ 技术实现

### Azure Speech SDK 集成
```python
import azure.cognitiveservices.speech as speechsdk

# Configure speech synthesis
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key,
    region=speech_region
)

# Set voice
speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"

# Create synthesizer
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)

# Synthesize with SSML
result = synthesizer.speak_ssml_async(ssml).get()
```

### SSML 语速控制
```python
ssml = f"""
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
    <voice name='zh-CN-XiaoxiaoNeural'>
        <prosody rate='{speaking_rate}'>
            {text}
        </prosody>
    </voice>
</speak>
"""
```

### 批量合成
```python
def synthesize_batch(scenes):
    results = {}
    for scene in scenes:
        audio_path = synthesize_scene_audio(
            scene_id=scene["scene_id"],
            voiceover=scene["voiceover"],
            pace=scene["pace"]
        )
        results[scene_id] = audio_path
    return results
```

## 🎯 下一步：Step 14

接入字幕生成服务，根据音频时长和文本生成精确的字幕时间轴。

## 📝 已完成的步骤

- ✅ Step 1-10: Milestone 1 完整流程（Mock）
- ✅ Step 11: 真实 LLM 文章解析
- ✅ Step 12: 真实 LLM 分镜生成
- ✅ Step 13: 真实 TTS 语音合成
- ⏳ Step 14: 字幕生成

## 💡 提示

### 如果没有 Azure Speech Key

系统会自动降级到 Mock 模式，不会报错：
```
[4/6] TTS Generate...
  ✓ Generated audio for 7 scenes (Mock)
```

### 支持的中文语音

Azure Speech 支持多种中文语音：
- `zh-CN-XiaoxiaoNeural` - 女声，温柔自然（默认）
- `zh-CN-YunxiNeural` - 男声，沉稳专业
- `zh-CN-YunyangNeural` - 男声，新闻播报风格
- `zh-CN-XiaoyiNeural` - 女声，活泼可爱

可以在 `TTSService.synthesize_speech()` 中通过 `voice_name` 参数指定。

### 成本估算

Azure Speech 定价（2024）：
- 免费层：每月 500,000 字符
- 标准层：$1 / 100万字符

一个 60 秒视频约 200-300 字符，成本约 $0.0002-0.0003。
