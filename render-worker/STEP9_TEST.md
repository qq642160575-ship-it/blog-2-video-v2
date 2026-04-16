# Step 9 测试指南 - Render Worker

## ✅ Step 9 已完成

Render Worker 已实现，可以从渲染队列消费任务并调用 Remotion 渲染视频。

## 📁 项目结构

```
render-worker/
├── index.js           # Render Worker 主程序
├── package.json
└── node_modules/
```

## 🔧 工作原理

1. 从 Redis `render_queue` 队列消费任务
2. 读取渲染清单 (manifest.json)
3. 调用 Remotion CLI 渲染视频
4. 保存 MP4 文件到 `backend/storage/videos/{project_id}/`

## 🧪 如何测试

### 准备工作

确保以下服务正在运行：
- ✅ Redis（端口 6379）

### 测试步骤

**终端 1 - 准备测试数据：**
```bash
cd backend
source venv/bin/activate
python scripts/test_render_worker.py
```

这会创建：
- 测试 manifest 文件
- 推送一个渲染任务到队列

**终端 2 - 启动 Render Worker：**
```bash
cd render-worker
npm start
```

## 📊 预期结果

Worker 会：
1. 从队列接收渲染任务
2. 读取 manifest 文件
3. 调用 Remotion 渲染第一个场景（HookTitle）
4. 保存视频到 `backend/storage/videos/proj_test_123/proj_test_123.mp4`

Worker 输出示例：
```
============================================================
Rendering Video
Job ID: job_test_render
Project ID: proj_test_123
Manifest: storage/manifests/proj_test_123_manifest.json
============================================================

[1/3] Reading manifest...
  ✓ Loaded manifest with 1 scenes

[2/3] Rendering scene...
  Scene: sc_proj_test_123_001
  Template: hook_title
  Duration: 6s

  Running: npx remotion render src/index.tsx HookTitle ...

[Remotion 渲染进度...]

[3/3] Render complete!
  ✓ Video saved: /path/to/backend/storage/videos/proj_test_123/proj_test_123.mp4

============================================================
✓ Job job_test_render completed successfully!
============================================================
```

## 🔍 验证

检查生成的视频：
```bash
ls -lh backend/storage/videos/proj_test_123/
# 应该看到 proj_test_123.mp4 文件
```

播放视频验证内容：
- 标题: "测试渲染"
- 副标题: "Render Worker 测试"
- 时长: 6秒
- 分辨率: 1080x1920

## ✨ 已实现的功能

- ✅ 从 Redis 队列消费渲染任务
- ✅ 读取渲染清单
- ✅ 调用 Remotion CLI 渲染
- ✅ 保存视频文件到本地存储
- ✅ 错误处理和日志输出

## 🎯 下一步：Step 10

打通端到端 Mock 流程，实现完整的视频生成链路（里程碑1）。
