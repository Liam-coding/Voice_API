#!/bin/bash
# 重启后端服务

echo "正在重启后端服务..."

# 杀死现有进程
pkill -f "python.*index.py" 2>/dev/null
sleep 2

# 启动新服务
cd /Users/jialei/code/voice-translation-web/backend/src
python3 index.py

echo "后端服务已重启"
echo "访问地址: http://127.0.0.1:8000"
echo "健康检查: http://127.0.0.1:8000/health"

# 等待服务启动
sleep 3

# 测试服务是否正常运行
echo "测试服务连接..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "后端服务启动成功！"
    echo ""
    echo "下一步:"
    echo "1. 打开前端页面: http://localhost:5173"
    echo "2. 点击录音按钮测试功能"
    echo "3. 如仍有问题，在浏览器控制台运行 cors_test.js"
else
    echo "后端服务启动失败"
    echo "查看详细错误信息:"
    echo "tail -f backend.log"
fi

# 保持脚本运行以便查看日志
echo ""
echo "按 Ctrl+C 停止服务"
wait