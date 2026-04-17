#!/bin/bash
# 日志查看脚本

echo "=========================================="
echo "博文视频生成系统 - 日志查看工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_menu() {
    echo "请选择要查看的日志："
    echo ""
    echo "  1) 后端API日志 (uvicorn)"
    echo "  2) Pipeline Worker日志"
    echo "  3) Redis日志"
    echo "  4) 最近的错误日志"
    echo "  5) 实时监控后端日志"
    echo "  6) 实时监控Worker日志"
    echo "  7) 查看所有运行中的进程"
    echo "  8) 查看存储目录状态"
    echo "  9) 退出"
    echo ""
    read -p "请输入选项 (1-9): " choice
}

view_backend_logs() {
    echo -e "${BLUE}=== 后端API日志 ===${NC}"
    if [ -f /tmp/pipeline-worker.log ]; then
        echo "找到 pipeline worker 日志文件"
    fi

    # 查找后台运行的uvicorn进程日志
    BACKEND_LOG=$(find /tmp/claude -name "*.output" -type f 2>/dev/null | grep -v pipeline | head -1)
    if [ -n "$BACKEND_LOG" ]; then
        echo "日志文件: $BACKEND_LOG"
        echo ""
        tail -n 50 "$BACKEND_LOG"
    else
        echo -e "${RED}未找到后端日志文件${NC}"
    fi
}

view_worker_logs() {
    echo -e "${BLUE}=== Pipeline Worker日志 ===${NC}"
    if [ -f /tmp/pipeline-worker.log ]; then
        echo "日志文件: /tmp/pipeline-worker.log"
        echo ""
        tail -n 50 /tmp/pipeline-worker.log
    else
        echo -e "${RED}未找到Worker日志文件${NC}"
        echo "Worker可能未启动或日志文件位置不同"
    fi
}

view_redis_logs() {
    echo -e "${BLUE}=== Redis日志 ===${NC}"
    echo "Redis通常不输出到文件，使用 redis-cli 查看状态："
    echo ""
    redis-cli INFO | grep -E "redis_version|uptime_in_seconds|connected_clients|used_memory_human"
}

view_error_logs() {
    echo -e "${BLUE}=== 最近的错误日志 ===${NC}"

    # 从后端日志中提取错误
    BACKEND_LOG=$(find /tmp/claude -name "*.output" -type f 2>/dev/null | grep -v pipeline | head -1)
    if [ -n "$BACKEND_LOG" ]; then
        echo "后端错误:"
        grep -i "error\|exception\|traceback" "$BACKEND_LOG" | tail -n 20
    fi

    echo ""

    # 从worker日志中提取错误
    if [ -f /tmp/pipeline-worker.log ]; then
        echo "Worker错误:"
        grep -i "error\|exception\|traceback" /tmp/pipeline-worker.log | tail -n 20
    fi
}

tail_backend_logs() {
    echo -e "${BLUE}=== 实时监控后端日志 (Ctrl+C 退出) ===${NC}"
    BACKEND_LOG=$(find /tmp/claude -name "*.output" -type f 2>/dev/null | grep -v pipeline | head -1)
    if [ -n "$BACKEND_LOG" ]; then
        tail -f "$BACKEND_LOG"
    else
        echo -e "${RED}未找到后端日志文件${NC}"
    fi
}

tail_worker_logs() {
    echo -e "${BLUE}=== 实时监控Worker日志 (Ctrl+C 退出) ===${NC}"
    if [ -f /tmp/pipeline-worker.log ]; then
        tail -f /tmp/pipeline-worker.log
    else
        echo -e "${RED}未找到Worker日志文件${NC}"
    fi
}

view_processes() {
    echo -e "${BLUE}=== 运行中的进程 ===${NC}"
    echo ""

    echo -e "${GREEN}后端API (uvicorn):${NC}"
    ps aux | grep "uvicorn" | grep -v grep || echo "未运行"

    echo ""
    echo -e "${GREEN}Pipeline Worker:${NC}"
    ps aux | grep "pipeline_worker" | grep -v grep || echo "未运行"

    echo ""
    echo -e "${GREEN}Redis:${NC}"
    ps aux | grep "redis-server" | grep -v grep || echo "未运行"

    echo ""
    echo -e "${GREEN}前端 (vite):${NC}"
    ps aux | grep "vite" | grep -v grep || echo "未运行"
}

view_storage() {
    echo -e "${BLUE}=== 存储目录状态 ===${NC}"
    echo ""

    STORAGE_DIR="/home/edy/Music/下载/博文生成视频项目/backend/storage"

    if [ -d "$STORAGE_DIR" ]; then
        echo "存储目录: $STORAGE_DIR"
        echo ""

        echo -e "${GREEN}视频文件:${NC}"
        find "$STORAGE_DIR/videos" -name "*.mp4" -type f -exec ls -lh {} \; 2>/dev/null | tail -n 10
        echo "总计: $(find "$STORAGE_DIR/videos" -name "*.mp4" -type f 2>/dev/null | wc -l) 个视频文件"

        echo ""
        echo -e "${GREEN}音频文件:${NC}"
        find "$STORAGE_DIR/audio" -name "*.mp3" -type f 2>/dev/null | wc -l
        echo "总计: $(find "$STORAGE_DIR/audio" -name "*.mp3" -type f 2>/dev/null | wc -l) 个音频文件"

        echo ""
        echo -e "${GREEN}字幕文件:${NC}"
        echo "总计: $(find "$STORAGE_DIR/subtitles" -name "*.srt" -type f 2>/dev/null | wc -l) 个字幕文件"

        echo ""
        echo -e "${GREEN}存储空间使用:${NC}"
        du -sh "$STORAGE_DIR"
    else
        echo -e "${RED}存储目录不存在${NC}"
    fi
}

# 主循环
while true; do
    show_menu

    case $choice in
        1)
            view_backend_logs
            ;;
        2)
            view_worker_logs
            ;;
        3)
            view_redis_logs
            ;;
        4)
            view_error_logs
            ;;
        5)
            tail_backend_logs
            ;;
        6)
            tail_worker_logs
            ;;
        7)
            view_processes
            ;;
        8)
            view_storage
            ;;
        9)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            ;;
    esac

    echo ""
    echo "按回车键继续..."
    read
    clear
done
