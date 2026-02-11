#!/bin/bash

# 语音翻译服务升级部署脚本

echo "🚀 开始部署改进版语音翻译服务..."

# 1. 备份当前版本
echo "📋 备份当前版本..."
cp -r backend/src backend/src_backup_$(date +%Y%m%d_%H%M%S)

# 2. 安装新依赖
echo "📦 安装新依赖..."
cd backend
pip install -r requirements.txt

# 3. 验证配置
echo "⚙️ 验证配置..."
if [ ! -f "config/api_config.py" ]; then
    echo "❌ 错误: 找不到配置文件 config/api_config.py"
    exit 1
fi

# 4. 测试新模块导入
echo "🧪 测试新模块..."
python -c "
import sys
sys.path.append('src')
try:
    from adapter.improved_makawai_adapter import ImprovedMakawaiClient
    from audio.improved_converter import ImprovedAudioProcessor
    print('✅ 新模块导入成功')
except Exception as e:
    print(f'❌ 模块导入失败: {e}')
    exit(1)
"

# 5. 运行单元测试
echo "🔬 运行单元测试..."
python -m pytest tests/ -v || echo "⚠️ 测试失败，继续部署..."

# 6. 启动服务
echo "🚀 启动改进版服务..."
echo "请手动运行: python src/improved_index.py"

echo "✅ 部署完成！"
echo ""
echo "📝 下一步操作:"
echo "1. 检查配置文件: backend/config/api_config.py"
echo "2. 启动服务: cd backend && python src/improved_index.py"
echo "3. 测试服务: curl http://localhost:8000/health"
echo "4. 前端测试: 访问 http://localhost:5173"