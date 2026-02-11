#!/bin/bash

echo "🚀 启动语音翻译开发环境"

# 检查后端依赖
echo "📋 检查后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "📦 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 启动后端（后台运行）
echo "サービ 启动后端服务..."
python src/index.py &
BACKEND_PID=$!
echo "sPid: $BACKEND_PID"

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 后端服务启动成功 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 启动前端
echo "サービ 启动前端开发服务器..."
cd ../frontend
npm install
npm run dev &

echo ""
echo "🎉 开发环境启动完成!"
echo "🌐 前端地址: http://localhost:5173"
echo "サービ 后端地址: http://localhost:8000"
echo "🐛 调试页面: http://localhost:5173/debug.html"
echo ""
echo "💡 使用 Ctrl+C 停止所有服务"

# 等待用户中断
wait