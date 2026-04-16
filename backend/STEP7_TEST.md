# Step 7 测试指南 - Pipeline Worker

## ✅ Step 7 已完成

Pipeline Worker 已实现，可以消费任务队列并处理生成流程（Mock 版本）。

## 🧪 如何测试

### 准备工作

确保以下服务正在运行：
- ✅ Redis（端口 6379）
- ✅ 数据库已初始化

### 测试步骤

**终端 1 - 启动 API 服务器：**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**终端 2 - 启动 Pipeline Worker：**
```bash
cd backend
source venv/bin/activate
python scripts/run_worker.py
```

**终端 3 - 运行端到端测试：**
```bash
cd backend
source venv/bin/activate
python scripts/test_e2e.py
```

## 📊 预期结果

测试脚本会：
1. 创建一个项目
2. 创建一个生成任务
3. Worker 自动接收任务并处理
4. 显示处理进度（6个阶段）
5. 完成后保存 3 个 Scene 到数据库
6. 生成 render manifest

Worker 输出示例：
```
============================================================
Processing Job: job_abc123
Project: proj_xyz789
Type: generate
============================================================

[1/6] Article Parse...
  ✓ Topic: RAG 基础概念
  ✓ Confidence: 0.86

[2/6] Scene Generate...
  ✓ Generated 3 scenes

[3/6] Scene Validate...
  ✓ Scenes saved to database

[4/6] TTS Generate...
  ✓ Generated audio for 3 scenes

[5/6] Subtitle Generate...
  ✓ Generated subtitles

[6/6] Render Prepare...
  ✓ Render manifest created

[Next] Pushing to render queue...
  ✓ Render task queued

============================================================
✓ Job job_abc123 completed successfully!
============================================================
```

## 🔍 验证

测试完成后，可以通过 API 查看结果：

```bash
# 查看 Scenes
curl http://localhost:8000/projects/{project_id}/scenes

# 查看 Job 状态
curl http://localhost:8000/jobs/{job_id}
```

或访问 Swagger UI：http://localhost:8000/docs

## 📁 生成的文件

- `storage/manifests/{project_id}_manifest.json` - 渲染清单
- 数据库中的 3 条 Scene 记录

## ✨ 已实现的功能

- ✅ 从 Redis 队列消费任务
- ✅ Mock 文章解析
- ✅ Mock 分镜生成（3个场景）
- ✅ Scene 规则校验
- ✅ Scene 保存到数据库
- ✅ Mock TTS 生成
- ✅ Mock 字幕生成
- ✅ 渲染清单生成
- ✅ 推送到渲染队列
- ✅ Job 状态更新
- ✅ 错误处理

## 🎯 下一步：Step 8

创建 Remotion 模板，为视频渲染做准备。
