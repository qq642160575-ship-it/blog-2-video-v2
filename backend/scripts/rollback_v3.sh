#!/bin/bash
# =======================================================
# AI短视频生成系统 v3 回滚脚本
# 用法: bash scripts/rollback_v3.sh [backup_db_file]
# =======================================================
set -e

BACKUP_DB=${1:-""}

echo "==================================="
echo " AI短视频生成系统 v3 回滚脚本"
echo "==================================="

# 1. 回滚数据库迁移
echo ""
echo "[1/3] 回滚数据库迁移 (降到 v2 head)..."
alembic downgrade -1
echo "  ✓ 迁移已回滚"

# 2. 恢复数据库备份（如果提供）
echo ""
if [ -n "$BACKUP_DB" ] && [ -f "$BACKUP_DB" ]; then
    echo "[2/3] 恢复数据库备份: $BACKUP_DB..."
    cp "$BACKUP_DB" blog_video.db
    echo "  ✓ 数据库已恢复"
else
    echo "[2/3] 未提供备份文件，跳过数据库恢复"
    echo "  ℹ 如需恢复，请手动: cp <backup_file> blog_video.db"
fi

# 3. 重启服务
echo ""
echo "[3/3] 重启服务..."
if systemctl is-active --quiet video-generation-service 2>/dev/null; then
    systemctl restart video-generation-service
    echo "  ✓ 服务已重启"
else
    echo "  ℹ 请手动重启后端服务"
fi

echo ""
echo "==================================="
echo "✅ v3 回滚完成，已退回到 v2"
echo "==================================="
