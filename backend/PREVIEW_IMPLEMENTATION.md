# 预览功能实现说明

## 概述

预览功能允许用户在时间轴编辑器中快速生成低分辨率预览视频，用于验证时间轴调整效果。

## 架构设计

```
用户请求 → API 端点 → PreviewService → Remotion CLI → 预览视频
```

### 核心组件

1. **API 端点** (`app/api/timeline.py`, `app/api/scenes.py`)
   - `POST /scenes/{scene_id}/preview` - 生成预览视频

2. **PreviewService** (`app/services/preview_service.py`)
   - 管理预览生成流程
   - 创建 Remotion props
   - 调用 Remotion CLI 渲染

3. **Remotion 模板** (`../remotion/src/compositions/`)
   - HookTitle - 标题场景
   - BulletExplain - 要点说明
   - CompareProcess - 对比流程

## 实现细节

### 1. 模板类型映射

```python
template_type → Composition ID
"hook_title" → "HookTitle"
"bullet_explain" → "BulletExplain"
"compare_process" → "CompareProcess"
```

### 2. Props 数据结构

#### HookTitle
```json
{
  "title": "主标题",
  "subtitle": "副标题"
}
```

#### BulletExplain
```json
{
  "title": "标题",
  "bullets": ["要点1", "要点2", "要点3"],
  "accentColor": "#f97316"
}
```

#### CompareProcess
```json
{
  "title": "对比标题",
  "leftTitle": "左侧标题",
  "rightTitle": "右侧标题",
  "leftPoints": ["左侧要点1", "左侧要点2"],
  "rightPoints": ["右侧要点1", "右侧要点2"],
  "footerText": "底部说明"
}
```

### 3. 渲染参数

- **低质量** (low): scale=0.5, crf=28 → 540x960
- **中等质量** (medium): scale=0.75, crf=23 → 810x1440
- **超时时间**: 120 秒
- **输出格式**: H.264 MP4

## 使用方法

### API 调用示例

```bash
# 生成预览
curl -X POST "http://localhost:8000/scenes/{scene_id}/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": 0,
    "end_time": null,
    "quality": "low"
  }'
```

### 响应示例

```json
{
  "success": true,
  "scene_id": "sc_proj_xxx_001",
  "preview_url": "/storage/previews/sc_proj_xxx_001_preview.mp4",
  "duration": 6.0
}
```

## 测试

### 运行测试脚本

```bash
cd backend
source venv/bin/activate
python scripts/test_preview.py
```

### 测试内容

1. 基础预览生成测试
2. 所有模板类型测试
3. 文件生成验证
4. 错误处理测试

## 故障排查

### 常见问题

#### 1. "Remotion directory not found"
**原因**: Remotion 项目路径配置错误
**解决**: 检查项目结构，确保 `remotion` 目录在项目根目录

#### 2. "Preview render failed"
**原因**: Remotion CLI 执行失败
**解决**:
- 检查 Remotion 是否正确安装：`cd ../remotion && npm install`
- 查看详细错误日志
- 验证 composition ID 是否正确

#### 3. "Preview render timeout"
**原因**: 渲染时间超过 120 秒
**解决**:
- 减少预览时长
- 降低质量设置
- 检查系统资源

#### 4. Props 数据不匹配
**原因**: scene_data 中的数据结构与模板期望不符
**解决**:
- 检查 `screen_text` 数组长度
- 验证 `visual_params` 字段
- 参考上面的 Props 数据结构

### 调试技巧

1. **查看日志**
   ```bash
   # 日志位置
   tail -f logs/app.log
   ```

2. **手动测试 Remotion**
   ```bash
   cd ../remotion
   npx remotion render src/index.tsx HookTitle out/test.mp4 \
     --props '{"title":"测试","subtitle":"副标题"}'
   ```

3. **检查生成的 manifest**
   ```bash
   cat storage/previews/*_preview_manifest.json
   ```

## 性能优化

### 当前实现
- 低质量预览：~2-5 秒
- 中等质量预览：~5-10 秒

### 优化建议
1. 使用 Remotion Lambda 进行云端渲染
2. 实现预览缓存机制
3. 支持增量渲染（仅渲染修改部分）
4. 添加渲染队列管理

## 扩展功能

### 未来改进
1. **实时预览**: WebSocket 推送渲染进度
2. **部分预览**: 仅渲染指定时间段
3. **多场景预览**: 支持多个场景连续预览
4. **预览历史**: 保存历史预览版本
5. **A/B 对比**: 并排对比不同版本

## 相关文件

- `app/api/timeline.py` - 时间轴 API
- `app/api/scenes.py` - 场景 API
- `app/services/preview_service.py` - 预览服务
- `scripts/test_preview.py` - 测试脚本
- `../remotion/src/index.tsx` - Remotion 入口
- `../remotion/src/compositions/` - 模板组件

## 更新日志

### 2026-04-23
- ✅ 修复 Remotion 项目路径配置
- ✅ 修正入口文件名 (index.ts → index.tsx)
- ✅ 实现模板类型映射
- ✅ 添加 Props 数据转换
- ✅ 改进错误日志输出
- ✅ 增加超时时间到 120 秒
- ✅ 创建测试脚本

### 已知限制
- 不支持音频同步（需要 TTS 集成）
- 不支持自定义字体
- 不支持复杂动画时间轴
