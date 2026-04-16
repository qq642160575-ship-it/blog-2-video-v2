#!/bin/bash

echo "=========================================="
echo "博文生成视频系统 - 环境配置"
echo "=========================================="
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 1. 配置后端
echo "📦 步骤 1/4: 配置后端环境..."
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "  创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "  安装 Python 依赖..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "  创建 .env 配置文件..."
    cat > .env << 'EOF'
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/blog_video_db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (暂时可以留空，Mock 阶段不需要)
OPENAI_API_KEY=sk-mock-key-for-testing

# Azure Speech (暂时可以留空，Mock 阶段不需要)
AZURE_SPEECH_KEY=mock-key
AZURE_SPEECH_REGION=eastus

# Storage
STORAGE_PATH=./storage
EOF
fi

# 创建存储目录
mkdir -p storage/audio storage/video storage/subtitles

echo "  ✅ 后端环境配置完成"
cd ..

# 2. 配置前端
echo ""
echo "📦 步骤 2/4: 配置前端环境..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  安装 Node.js 依赖..."
    npm install
else
    echo "  ✅ Node.js 依赖已安装"
fi

echo "  ✅ 前端环境配置完成"
cd ..

# 3. 检查 PostgreSQL 和 Redis
echo ""
echo "🔍 步骤 3/4: 检查服务..."

# 检查 PostgreSQL
if command -v psql &> /dev/null; then
    if pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "  ✅ PostgreSQL 正在运行"
    else
        echo "  ⚠️  PostgreSQL 未运行，请启动 PostgreSQL"
        echo "     或运行: docker-compose up -d postgres"
    fi
else
    echo "  ⚠️  PostgreSQL 未安装"
    echo "     请运行: docker-compose up -d postgres"
fi

# 检查 Redis
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "  ✅ Redis 正在运行"
    else
        echo "  ⚠️  Redis 未运行，请启动 Redis"
        echo "     或运行: docker-compose up -d redis"
    fi
else
    echo "  ⚠️  Redis 未安装"
    echo "     请运行: docker-compose up -d redis"
fi

# 4. 初始化数据库
echo ""
echo "🗄️  步骤 4/4: 初始化数据库..."
cd backend
source venv/bin/activate

# 检查数据库连接
if python -c "from app.core.db import engine; engine.connect()" 2>/dev/null; then
    echo "  ✅ 数据库连接成功"

    # 初始化表
    echo "  创建数据库表..."
    python scripts/init_db.py

    echo "  ✅ 数据库初始化完成"
else
    echo "  ⚠️  无法连接数据库"
    echo "     请检查 PostgreSQL 是否运行，或修改 .env 中的 DATABASE_URL"
fi

cd ..

echo ""
echo "=========================================="
echo "✅ 环境配置完成！"
echo "=========================================="
echo ""
echo "📝 下一步："
echo ""
echo "1. 启动后端服务："
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "2. 启动前端服务（新终端）："
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. 测试 API（新终端）："
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python scripts/test_flow.py"
echo ""
echo "4. 访问："
echo "   - API 文档: http://localhost:8000/docs"
echo "   - 前端页面: http://localhost:3000"
echo ""
