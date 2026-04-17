# Step 20 测试报告

## 测试目标
实现重渲染功能，允许用户在编辑场景后重新生成视频。

## 测试结果

### 1. 场景更新 ✓
- 成功更新场景旁白和时长
- 场景版本从 4 升级到 5
- 新旁白："这是重新渲染测试的旁白文本，内容已经被修改。"
- 新时长：7秒

### 2. 重渲染任务创建 ✓
- 成功创建重渲染任务 (job_d76860f3)
- 任务类型：rerender
- 初始状态：queued

### 3. 任务处理流程 ✓
- queued → running → completed
- 进度：0% → 95% (rendering) → 100% (export)
- 最终状态：completed

### 4. 视频生成 ✓
- 视频文件：`storage/videos/c4f46fd789d84c4b8284d856b62fe4c9/c4f46fd789d84c4b8284d856b62fe4c9.mp4`
- 文件大小：3.1 MB
- 生成时间：2026-04-17 11:27

## 代码变更

### 修改文件：app/workers/pipeline_worker.py

#### 1. 重构 process_task 方法
```python
def process_task(self, task: dict):
    job_type = task.get("job_type", "generate")
    job_id = task["job_id"]
    project_id = task["project_id"]

    if job_type == "generate":
        return self.process_generate(job_id, project_id)
    elif job_type == "rerender":
        return self.process_rerender(job_id, project_id)
```

#### 2. 新增 process_rerender 方法
重渲染流程：
1. 从数据库加载现有场景（而不是重新生成）
2. 为所有场景重新生成 TTS 音频
3. 重新生成字幕
4. 创建新的渲染清单
5. 推送到渲染队列

关键特性：
- 保留原有场景结构和内容
- 只重新生成音频和字幕
- 使用最新版本的场景数据
- 复用现有的渲染管道

## API 使用

### 更新场景
```bash
curl -X PATCH http://localhost:8000/projects/scenes/{scene_id} \
  -H "Content-Type: application/json" \
  -d '{
    "voiceover": "新的旁白文本",
    "duration_sec": 7
  }'
```

### 触发重渲染
```bash
curl -X POST http://localhost:8000/projects/{project_id}/jobs/rerender
```

### 查询任务状态
```bash
curl http://localhost:8000/jobs/{job_id}
```

## 系统架构

### 工作流程
1. **用户编辑场景** → Scene API (PATCH /scenes/{scene_id})
2. **触发重渲染** → Jobs API (POST /projects/{project_id}/jobs/rerender)
3. **Pipeline Worker** → 处理重渲染任务
   - 加载场景
   - 生成 TTS
   - 生成字幕
   - 创建渲染清单
4. **Render Worker** → 渲染视频
   - 从 Redis 队列获取任务
   - 使用 Remotion 渲染
   - 保存视频文件

### 依赖服务
- **FastAPI Server** (port 8000) - REST API
- **Pipeline Worker** (Python) - 任务处理
- **Render Worker** (Node.js) - 视频渲染
- **Redis** (port 6379) - 任务队列
- **SQLite** - 数据存储

## 重要发现

### 问题：渲染任务卡在 95%
**原因**：Render Worker (Node.js) 未启动

**解决方案**：
```bash
cd render-worker && npm start
```

### 完整启动流程
```bash
# 1. 启动 FastAPI 服务器
uvicorn app.main:app --reload --port 8000

# 2. 启动 Pipeline Worker
python scripts/run_worker.py

# 3. 启动 Render Worker
cd render-worker && npm start
```

## 测试脚本

创建了两个新的测试脚本：

1. **scripts/test_step20_rerender.py** - 完整的重渲染测试
2. **scripts/monitor_job.py** - 任务状态监控工具

## 结论

✅ **第20步完成**

重渲染功能已成功实现并通过测试：
- 场景编辑后可以触发重渲染
- 重渲染流程正确处理现有场景
- 视频成功生成并保存
- 所有三个服务（API、Pipeline Worker、Render Worker）协同工作

下一步可以进入第21步。
