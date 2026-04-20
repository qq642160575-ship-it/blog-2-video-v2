#!/bin/bash
# =======================================================
# AI短视频生成系统 v3 部署脚本
# 用法: bash scripts/deploy_v3.sh [prod_db_name]
# =======================================================
set -e

DB_NAME=${1:-"prod_db"}
BACKUP_FILE="backup_${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"

echo "==================================="
echo " AI短视频生成系统 v3 部署脚本"
echo " DB: ${DB_NAME}"
echo "==================================="

# 1. 运行单元测试
echo ""
echo "[1/5] 运行单元测试..."
python -m pytest tests/test_hook_service.py tests/test_e2e_mock.py -v --tb=short
echo "  ✓ 单元测试通过"

# 2. 备份数据库（SQLite 模式）
echo ""
echo "[2/5] 备份数据库..."
if [ -f "blog_video.db" ]; then
    cp blog_video.db "${BACKUP_FILE//.sql/.db}"
    echo "  ✓ SQLite 备份: ${BACKUP_FILE//.sql/.db}"
else
    echo "  ⚠ 未找到本地 SQLite 数据库，跳过备份"
fi

# 3. 执行数据库迁移
echo ""
echo "[3/5] 执行数据库迁移..."
alembic upgrade head
echo "  ✓ 迁移完成"

# 4. 验证迁移结果
echo ""
echo "[4/5] 验证迁移结果..."
python - << 'EOF'
import sqlite3
conn = sqlite3.connect('blog_video.db')
cursor = conn.execute('PRAGMA table_info(scenes)')
cols = {row[1] for row in cursor.fetchall()}
v3_fields = {'scene_role', 'narrative_stage', 'emotion_level', 'hook_type', 'quality_score'}
missing = v3_fields - cols
if missing:
    print(f"  ❌ 缺少字段: {missing}")
    exit(1)
print(f"  ✓ v3 字段全部存在: {v3_fields}")
conn.close()
EOF

# 5. 重启服务（如果有 systemd 服务）
echo ""
echo "[5/5] 重启服务..."
if systemctl is-active --quiet video-generation-service 2>/dev/null; then
    systemctl restart video-generation-service
    echo "  ✓ 服务已重启"
else
    echo "  ℹ 未检测到 systemd 服务，请手动重启后端"
    echo "    cd backend && uvicorn app.main:app --reload"
fi

echo ""
echo "==================================="
echo "✅ v3 部署完成"
echo "==================================="
