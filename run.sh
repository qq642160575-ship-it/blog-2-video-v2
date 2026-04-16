#!/bin/bash

echo "=========================================="
echo "博文生成视频系统 - 快速启动"
echo "=========================================="
echo ""

# 检查环境是否已配置
if [ ! -d "backend/venv" ]; then
    echo "❌ 环境未配置，请先运行: ./setup.sh"
    exit 1
fi

# 启动后端
echo "🚀 启动后端服务..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "   后端 PID: $BACKEND_PID"
echo "   后端地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "   前端 PID: $FRONTEND_PID"
echo "   前端地址: http://localhost:3000"
echo ""

echo "=========================================="
echo "✅ 服务已启动！"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait
