# TTS 服务架构说明

## 概述

TTS（Text-to-Speech）服务已重构为可插拔式架构，支持多个 TTS 提供商。

## 架构设计

### 1. 抽象基类 (BaseTTSService)

位置: `app/services/tts/base.py`

定义了所有 TTS 服务必须实现的接口：
- `synthesize_speech()` - 基础语音合成
- `synthesize_scene_audio()` - 场景音频合成
- `synthesize_batch()` - 批量合成

### 2. 具体实现

#### Edge TTS (免费)
- 位置: `app/services/tts/edge_tts_service.py`
- 特点: 完全免费，无需 API 密钥
- 音色: zh-CN-XiaoxiaoNeural 等

#### Volcengine TTS (火山云)
- 位置: `app/services/tts/volcengine_tts_service.py`
- 特点: 商业级质量，需要付费账号
- 音色: BV700_streaming 等

### 3. 工厂模式 (TTSFactory)

位置: `app/services/tts/factory.py`

根据配置自动创建对应的 TTS 服务实例。

### 4. 兼容层 (TTSService)

位置: `app/services/tts_service.py`

保持向后兼容，现有代码无需修改即可使用新架构。

## 配置方式

### 环境变量配置

在 `.env` 文件中设置：

```bash
# TTS 提供商选择
TTS_PROVIDER=volcengine  # 可选: 'edge', 'volcengine'

# 火山云配置（使用 volcengine 时需要）
VOLCENGINE_APP_ID=your_app_id
VOLCENGINE_ACCESS_TOKEN=your_access_token
VOLCENGINE_CLUSTER=volcano_tts
VOLCENGINE_API_KEY=your_api_key
```

### 代码中使用

```python
from app.services.tts_service import TTSService

# 方式1: 使用配置文件中的默认提供商
service = TTSService()

# 方式2: 显式指定提供商
service = TTSService(provider="volcengine")

# 使用服务
audio_path = service.synthesize_speech(
    text="你好，世界",
    speaking_rate=1.0
)
```

## 添加新的 TTS 提供商

1. 创建新的服务类，继承 `BaseTTSService`
2. 实现所有抽象方法
3. 在 `TTSFactory` 中注册新提供商
4. 更新配置文件和文档

## 测试

```bash
# 测试 Edge TTS
python scripts/test_tts.py

# 测试火山云 TTS
python scripts/test_volcengine_tts.py
```

## 优势

1. **可插拔**: 轻松切换不同的 TTS 提供商
2. **可扩展**: 添加新提供商只需实现接口
3. **向后兼容**: 现有代码无需修改
4. **统一接口**: 所有提供商使用相同的 API
5. **配置驱动**: 通过环境变量控制行为
