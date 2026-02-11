# 安装和运行指南

## 快速开始

### 1. 安装Python依赖
```bash
cd backend
pip install websockets fastapi uvicorn python-multipart
```

注意：音频处理库(librosa, pydub)是可选的，简化版本可以不安装。

### 2. 验证基本连接
```bash
cd backend
python minimal_test.py
```

### 3. 启动后端服务
```bash
cd backend/src
python index.py
```

### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 故障排除

### 如果遇到"received 1000 (OK)"错误：

1. **检查API密钥**：确认`config/api_config.py`中的密钥正确
2. **网络连接**：确保能访问Makawai API服务器
3. **查看详细日志**：后端会输出DEBUG信息帮助定位问题

### 如果音频转换失败：

使用简化版本的转换器（已包含在代码中），或者：
```bash
pip install librosa numpy pydub
brew install ffmpeg  # Mac用户
```

### 常用调试命令：

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 测试WebSocket连接
python backend/minimal_test.py

# 查看后端日志
# 在启动后端服务的终端中查看DEBUG输出
```

## 项目特点

- **简化依赖**：核心功能不强依赖外部音频库
- **详细日志**：丰富的DEBUG信息便于问题定位
- **自动重连**：WebSocket连接断开时自动重新连接
- **错误处理**：完善的异常处理机制