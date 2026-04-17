# Step 28 测试报告

## 测试目标
实现资产管理和存储系统，包括：
- 创建 assets 表追踪所有生成的文件
- 实现资产生命周期管理
- 提供资产查询和过滤 API
- 实现文件清理逻辑
- 提供存储统计功能

## 测试结果

### 1. 资产创建 ✓
- 测试场景: 创建资产记录
- 状态: 200 OK
- 资产类型: audio
- 文件大小: 25 bytes
- 元数据: 支持 JSON 格式

### 2. 资产检索 ✓
- 测试场景: 通过 ID 获取资产
- API: GET /assets/{asset_id}
- 状态: 200 OK
- 返回字段: asset_id, project_id, job_id, asset_type, file_path, file_url, file_size, mime_type, metadata, is_deleted, created_at

### 3. 项目资产查询 ✓
- 测试场景: 获取项目的所有资产
- API: GET /projects/{project_id}/assets
- 创建资产: 3 个（audio, subtitle, video）
- 查询结果: 3 个资产
- 排序: 按创建时间倒序

### 4. 任务资产查询 ✓
- 测试场景: 获取任务的所有资产
- API: GET /jobs/{job_id}/assets
- 创建资产: 1 个（video）
- 查询结果: 1 个资产

### 5. 类型过滤 ✓
- 测试场景: 按资产类型过滤
- API: GET /projects/{project_id}/assets?asset_type=audio
- 创建资产: 2 个 audio, 1 个 video
- 过滤结果: 2 个 audio 资产
- 过滤准确性: ✓

### 6. 软删除 ✓
- 测试场景: 软删除资产
- API: DELETE /assets/{asset_id}
- 删除状态: is_deleted = True
- 文件保留: ✓ 文件仍存在于磁盘
- 用途: 标记删除但保留文件用于审计

### 7. 存储统计 ✓
- 测试场景: 获取存储统计信息
- API: GET /assets/storage/stats
- 状态: 200 OK
- 统计信息:
  - 总资产数: 16
  - 总大小: 248 bytes
  - 按类型统计: audio (8), subtitle (2), video (6)

## 新增文件

### 1. app/models/asset.py
资产模型，追踪所有生成的文件：

```python
class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)  # asset_xxx
    project_id = Column(String, nullable=False, index=True)
    job_id = Column(String, nullable=False, index=True)

    # Asset type: audio, subtitle, video, scene_json, image
    asset_type = Column(String, nullable=False, index=True)

    # File information
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)

    # Metadata (JSON string)
    meta_data = Column(Text, nullable=True)

    # Status
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
```

### 2. app/services/asset_service.py
资产服务，管理资产生命周期：

#### 创建资产
```python
def create_asset(
    self,
    project_id: str,
    job_id: str,
    asset_type: str,
    file_path: str,
    file_url: Optional[str] = None,
    file_size: Optional[int] = None,
    mime_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> Asset:
    """Create a new asset record"""
    asset_id = f"asset_{uuid.uuid4().hex[:8]}"

    # Calculate file size if not provided
    if file_size is None and os.path.exists(file_path):
        file_size = os.path.getsize(file_path)

    # Serialize metadata to JSON
    metadata_json = json.dumps(metadata) if metadata else None

    asset = Asset(
        id=asset_id,
        project_id=project_id,
        job_id=job_id,
        asset_type=asset_type,
        file_path=file_path,
        file_url=file_url,
        file_size=file_size,
        mime_type=mime_type,
        meta_data=metadata_json
    )

    self.db.add(asset)
    self.db.commit()

    return asset
```

#### 查询资产
```python
def get_project_assets(
    self,
    project_id: str,
    asset_type: Optional[str] = None,
    include_deleted: bool = False
) -> List[Asset]:
    """Get all assets for a project"""
    query = self.db.query(Asset).filter(Asset.project_id == project_id)

    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    if not include_deleted:
        query = query.filter(Asset.is_deleted == False)

    return query.order_by(Asset.created_at.desc()).all()
```

#### 软删除
```python
def soft_delete_asset(self, asset_id: str) -> Asset:
    """Soft delete an asset"""
    asset = self.get_asset(asset_id)
    if not asset:
        raise ValueError(f"Asset {asset_id} not found")

    asset.is_deleted = True
    asset.deleted_at = datetime.utcnow()
    self.db.commit()

    return asset
```

#### 硬删除
```python
def hard_delete_asset(self, asset_id: str, delete_file: bool = False) -> bool:
    """Hard delete an asset and optionally delete the file"""
    asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return False

    # Delete physical file if requested
    if delete_file and asset.file_path and os.path.exists(asset.file_path):
        try:
            os.remove(asset.file_path)
        except Exception as e:
            print(f"Failed to delete file {asset.file_path}: {e}")

    # Delete database record
    self.db.delete(asset)
    self.db.commit()

    return True
```

#### 存储统计
```python
def get_storage_stats(self) -> dict:
    """Get storage statistics"""
    total_assets = self.db.query(Asset).filter(Asset.is_deleted == False).count()
    total_size = self.db.query(func.sum(Asset.file_size)).filter(
        Asset.is_deleted == False
    ).scalar() or 0

    # Get counts by type
    asset_types = self.db.query(
        Asset.asset_type,
        func.count(Asset.id).label('count'),
        func.sum(Asset.file_size).label('size')
    ).filter(
        Asset.is_deleted == False
    ).group_by(Asset.asset_type).all()

    type_stats = {
        asset_type: {
            'count': count,
            'size': size or 0
        }
        for asset_type, count, size in asset_types
    }

    return {
        'total_assets': total_assets,
        'total_size': total_size,
        'by_type': type_stats
    }
```

### 3. app/services/file_cleanup_service.py
文件清理服务：

#### 清理失败任务的文件
```python
def cleanup_failed_job_files(self, job_id: str) -> Dict[str, int]:
    """Clean up files from a failed job"""
    assets = self.db.query(Asset).filter(
        Asset.job_id == job_id,
        Asset.is_deleted == False
    ).all()

    deleted_count = 0
    deleted_size = 0

    for asset in assets:
        if asset.file_path and os.path.exists(asset.file_path):
            try:
                file_size = os.path.getsize(asset.file_path)
                os.remove(asset.file_path)
                deleted_count += 1
                deleted_size += file_size
            except Exception as e:
                print(f"Failed to delete file {asset.file_path}: {e}")

        # Mark asset as deleted
        asset.is_deleted = True
        asset.deleted_at = datetime.utcnow()

    self.db.commit()

    return {
        "deleted_count": deleted_count,
        "deleted_size": deleted_size
    }
```

#### 清理旧任务
```python
def cleanup_old_jobs(self, days: int = 30, keep_completed: bool = True):
    """Clean up files from old jobs"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = self.db.query(GenerationJob).filter(
        GenerationJob.created_at < cutoff_date
    )

    if keep_completed:
        # Only clean up failed/cancelled jobs
        query = query.filter(
            GenerationJob.status.in_(["failed", "cancelled"])
        )

    old_jobs = query.all()

    total_deleted = 0
    total_size = 0

    for job in old_jobs:
        result = self.cleanup_failed_job_files(job.id)
        total_deleted += result["deleted_count"]
        total_size += result["deleted_size"]

    return {
        "jobs_cleaned": len(old_jobs),
        "files_deleted": total_deleted,
        "bytes_freed": total_size
    }
```

#### 清理孤立文件
```python
def cleanup_orphaned_files(self, storage_dir: str) -> Dict[str, int]:
    """Clean up files that don't have corresponding asset records"""
    if not os.path.exists(storage_dir):
        return {"deleted_count": 0, "deleted_size": 0}

    deleted_count = 0
    deleted_size = 0

    # Get all file paths from assets
    asset_paths = set()
    assets = self.db.query(Asset).filter(Asset.is_deleted == False).all()
    for asset in assets:
        if asset.file_path:
            asset_paths.add(os.path.abspath(asset.file_path))

    # Walk through storage directory
    for root, dirs, files in os.walk(storage_dir):
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))

            # Skip if file is in asset records
            if file_path in asset_paths:
                continue

            # Delete orphaned file
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_count += 1
                deleted_size += file_size
            except Exception as e:
                print(f"Failed to delete orphaned file {file_path}: {e}")

    return {
        "deleted_count": deleted_count,
        "deleted_size": deleted_size
    }
```

### 4. app/api/assets.py
资产 API 端点：

#### 创建资产
```python
@router.post("/assets")
def create_asset(asset_data: AssetCreate, db: Session = Depends(get_db)):
    """Create a new asset record"""
```

#### 获取资产
```python
@router.get("/assets/{asset_id}")
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    """Get asset by ID"""
```

#### 获取项目资产
```python
@router.get("/projects/{project_id}/assets")
def get_project_assets(
    project_id: str,
    asset_type: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all assets for a project"""
```

#### 获取任务资产
```python
@router.get("/jobs/{job_id}/assets")
def get_job_assets(
    job_id: str,
    asset_type: Optional[str] = Query(None),
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all assets for a job"""
```

#### 更新资产
```python
@router.patch("/assets/{asset_id}")
def update_asset(
    asset_id: str,
    update_data: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update asset information"""
```

#### 删除资产
```python
@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: str,
    hard_delete: bool = Query(False),
    delete_file: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Delete an asset (soft delete by default)"""
```

#### 清理任务资产
```python
@router.delete("/jobs/{job_id}/assets")
def cleanup_job_assets(
    job_id: str,
    delete_files: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Clean up all assets for a job"""
```

#### 清理项目资产
```python
@router.delete("/projects/{project_id}/assets")
def cleanup_project_assets(
    project_id: str,
    delete_files: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Clean up all assets for a project"""
```

#### 存储统计
```python
@router.get("/assets/storage/stats")
def get_storage_stats(db: Session = Depends(get_db)):
    """Get storage statistics"""
```

### 5. alembic/versions/42e26d791376_add_assets_table.py
数据库迁移：

```python
def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('asset_type', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('meta_data', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text("(datetime('now'))"), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_project_id'), 'assets', ['project_id'])
    op.create_index(op.f('ix_assets_job_id'), 'assets', ['job_id'])
    op.create_index(op.f('ix_assets_asset_type'), 'assets', ['asset_type'])
```

## 架构设计

### 1. 资产类型

```
┌─────────────────────────────────────┐
│         Asset Types                 │
├─────────────────────────────────────┤
│  • audio      - TTS 生成的音频      │
│  • subtitle   - 字幕文件            │
│  • video      - 最终视频            │
│  • scene_json - 场景配置文件        │
│  • image      - 场景图片            │
└─────────────────────────────────────┘
```

### 2. 资产生命周期

```
创建任务
    ↓
生成文件 (audio, subtitle, etc.)
    ↓
创建资产记录 (AssetService.create_asset)
    ↓
文件使用中
    ↓
任务完成/失败
    ↓
软删除 (标记 is_deleted = True)
    ↓
定期清理 (FileCleanupService)
    ↓
硬删除 (删除数据库记录和文件)
```

### 3. 存储管理

```
┌─────────────────────────────────────┐
│      Storage Management             │
├─────────────────────────────────────┤
│  Asset Tracking                     │
│    ↓                                │
│  Storage Statistics                 │
│    ↓                                │
│  Cleanup Policies                   │
│    ↓                                │
│  Orphaned File Detection            │
│    ↓                                │
│  Automated Cleanup                  │
└─────────────────────────────────────┘
```

## API 文档

### POST /assets
创建资产记录

**请求体:**
```json
{
  "project_id": "proj_xxx",
  "job_id": "job_xxx",
  "asset_type": "audio",
  "file_path": "/path/to/file.mp3",
  "file_url": "https://cdn.example.com/file.mp3",
  "file_size": 1024000,
  "mime_type": "audio/mpeg",
  "metadata": {
    "duration": 10.5,
    "sample_rate": 44100
  }
}
```

**响应:**
```json
{
  "asset_id": "asset_xxx",
  "asset_type": "audio",
  "file_path": "/path/to/file.mp3",
  "file_url": "https://cdn.example.com/file.mp3",
  "file_size": 1024000
}
```

### GET /assets/{asset_id}
获取资产详情

**响应:**
```json
{
  "asset_id": "asset_xxx",
  "project_id": "proj_xxx",
  "job_id": "job_xxx",
  "asset_type": "audio",
  "file_path": "/path/to/file.mp3",
  "file_url": "https://cdn.example.com/file.mp3",
  "file_size": 1024000,
  "mime_type": "audio/mpeg",
  "metadata": "{\"duration\": 10.5}",
  "is_deleted": false,
  "created_at": "2026-04-17T05:50:00Z"
}
```

### GET /projects/{project_id}/assets
获取项目的所有资产

**查询参数:**
- `asset_type` (可选): 按类型过滤
- `include_deleted` (可选): 是否包含已删除的资产

**响应:**
```json
{
  "project_id": "proj_xxx",
  "total": 5,
  "assets": [
    {
      "asset_id": "asset_xxx",
      "job_id": "job_xxx",
      "asset_type": "audio",
      "file_path": "/path/to/file.mp3",
      "file_size": 1024000,
      "is_deleted": false,
      "created_at": "2026-04-17T05:50:00Z"
    }
  ]
}
```

### GET /jobs/{job_id}/assets
获取任务的所有资产

**查询参数:**
- `asset_type` (可选): 按类型过滤
- `include_deleted` (可选): 是否包含已删除的资产

**响应:**
```json
{
  "job_id": "job_xxx",
  "total": 3,
  "assets": [...]
}
```

### DELETE /assets/{asset_id}
删除资产

**查询参数:**
- `hard_delete` (可选): 是否硬删除（默认软删除）
- `delete_file` (可选): 是否删除物理文件

**响应 (软删除):**
```json
{
  "asset_id": "asset_xxx",
  "is_deleted": true,
  "message": "Asset soft deleted successfully"
}
```

**响应 (硬删除):**
```json
{
  "message": "Asset deleted permanently"
}
```

### DELETE /jobs/{job_id}/assets
清理任务的所有资产

**查询参数:**
- `delete_files` (可选): 是否删除物理文件

**响应:**
```json
{
  "job_id": "job_xxx",
  "deleted_count": 5,
  "message": "Cleaned up 5 assets"
}
```

### GET /assets/storage/stats
获取存储统计

**响应:**
```json
{
  "total_assets": 100,
  "total_size": 1024000000,
  "by_type": {
    "audio": {
      "count": 50,
      "size": 512000000
    },
    "video": {
      "count": 30,
      "size": 409600000
    },
    "subtitle": {
      "count": 20,
      "size": 102400000
    }
  }
}
```

## 使用场景

### 场景 1: 追踪生成的文件
```python
# 在 worker 中生成文件后创建资产记录
asset_service = AssetService(db)
asset = asset_service.create_asset(
    project_id=project_id,
    job_id=job_id,
    asset_type="audio",
    file_path="/storage/audio/scene_1.mp3",
    file_size=1024000,
    mime_type="audio/mpeg",
    metadata={"duration": 10.5, "scene_id": "scene_1"}
)
```

### 场景 2: 查询项目的所有视频
```bash
curl "http://localhost:8000/projects/proj_xxx/assets?asset_type=video"
```

### 场景 3: 清理失败任务的文件
```python
cleanup_service = FileCleanupService(db)
result = cleanup_service.cleanup_failed_job_files(job_id)
print(f"Deleted {result['deleted_count']} files, freed {result['deleted_size']} bytes")
```

### 场景 4: 定期清理旧文件
```python
# 清理 30 天前失败的任务
cleanup_service = FileCleanupService(db)
result = cleanup_service.cleanup_old_jobs(days=30, keep_completed=True)
print(f"Cleaned {result['jobs_cleaned']} jobs")
```

### 场景 5: 监控存储使用
```bash
curl http://localhost:8000/assets/storage/stats
```

## 技术要点

### 1. 避免 SQLAlchemy 保留字
- 问题: `metadata` 是 SQLAlchemy 的保留字
- 解决: 使用 `meta_data` 作为列名
- 影响: 需要在 API 响应中映射回 `metadata`

### 2. Python 3.9 兼容性
- 问题: `Dict[str, Any] | None` 语法需要 Python 3.10+
- 解决: 使用 `Optional[Dict[str, Any]]`
- 位置: task_queue.py

### 3. 路由冲突
- 问题: `/storage` 被 StaticFiles 占用
- 解决: 使用 `/assets/storage/stats` 作为 API 路径
- 原因: StaticFiles mount 优先级高于 API 路由

### 4. 软删除 vs 硬删除
- 软删除: 标记 `is_deleted = True`，保留文件和记录
- 硬删除: 删除数据库记录，可选删除物理文件
- 用途: 软删除用于审计，硬删除用于释放空间

## 性能考虑

### 数据库索引
- `project_id`: 快速查询项目资产
- `job_id`: 快速查询任务资产
- `asset_type`: 快速按类型过滤

### 查询优化
- 默认不包含已删除资产
- 支持按类型过滤减少数据量
- 按创建时间倒序排列

### 存储统计
- 使用 SQL 聚合函数计算
- 按类型分组统计
- 缓存考虑: 可添加 Redis 缓存

## 已知限制

1. **文件路径**: 当前存储本地路径，未来可扩展支持云存储 URL
2. **元数据格式**: 存储为 JSON 字符串，查询不便
3. **清理策略**: 需要手动触发，未实现自动定期清理
4. **存储配额**: 未实现存储配额限制

## 未来改进

### 1. 云存储集成
```python
def upload_to_cloud(self, asset_id: str, storage_provider: str):
    """Upload asset to cloud storage (S3, OSS, etc.)"""
    asset = self.get_asset(asset_id)
    # Upload file
    cloud_url = upload_file(asset.file_path, storage_provider)
    # Update asset URL
    self.update_asset_url(asset_id, cloud_url)
```

### 2. 自动清理任务
```python
# 使用 Celery 或 APScheduler
@scheduler.scheduled_job('cron', hour=2)
def auto_cleanup():
    """Run daily cleanup at 2 AM"""
    cleanup_service = FileCleanupService(db)
    cleanup_service.cleanup_old_jobs(days=30)
```

### 3. 存储配额
```python
def check_storage_quota(self, project_id: str, max_size: int) -> bool:
    """Check if project exceeds storage quota"""
    total_size = self.db.query(func.sum(Asset.file_size)).filter(
        Asset.project_id == project_id,
        Asset.is_deleted == False
    ).scalar() or 0
    return total_size < max_size
```

### 4. 资产版本控制
```python
class Asset(Base):
    version = Column(Integer, default=1)
    parent_asset_id = Column(String, nullable=True)  # For versioning
```

## 测试验证

### 自动化测试 ✓
- 资产创建: ✓
- 资产检索: ✓
- 项目资产查询: ✓
- 任务资产查询: ✓
- 类型过滤: ✓
- 软删除: ✓
- 存储统计: ✓

### 手动测试步骤
1. 创建项目和任务
2. 生成文件并创建资产记录
3. 查询资产列表
4. 按类型过滤资产
5. 软删除资产
6. 查看存储统计
7. 清理任务资产

## 结论

✅ **第28步完成**

资产管理和存储系统已成功实现：
- 完整的资产追踪机制
- 灵活的查询和过滤 API
- 软删除和硬删除支持
- 文件清理服务
- 存储统计功能

系统文件管理能力大幅提升：
- 文件可追溯性
- 存储空间监控
- 自动化清理能力
- 审计追踪
- 资源优化

下一步可以进入第29步：性能优化和缓存。
