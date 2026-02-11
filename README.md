# Voice Translation Web 应用

实时语音翻译应用，支持中英文互译。

## 项目结构

```
voice-translation-web/
├── backend/           # 后端服务
│   ├── src/          # 源代码
│   │   ├── adapter/  # 第三方API适配器
│   │   ├── audio/    # 音频处理模块
│   │   └── index.py  # 主应用入口
│   ├── config/       # 配置文件
│   ├── requirements.txt  # Python依赖
│   └── test_backend.py   # 后端测试脚本
└── frontend/         # 前端应用
    └── src/          # Vue源代码
```

## 环境要求

### 后端
- Python 3.8+
- FFmpeg (用于音频处理)

### 前端
- Node.js 16+
- npm 或 yarn

## 安装步骤

### 1. 安装FFmpeg (Mac)
```bash
brew install ffmpeg
```

### 2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd frontend
npm install
```

## 运行应用

### 启动后端服务
```bash
cd backend
python src/index.py
```

后端将在 `http://localhost:8000` 启动

### 启动前端应用
```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:5173` 启动

## 测试

### 后端组件测试
```bash
cd backend
python test_backend.py
```

### 健康检查
访问 `http://localhost:8000/health` 查看服务状态

## 常见问题排查

### 1. "received 1000 (OK); then sent 1000 (OK)" 错误
这通常表示WebSocket连接正常关闭，可能原因：
- Makawai API密钥无效
- 网络连接问题
- 音频数据格式不正确

### 2. 音频转换失败
确保已安装FFmpeg：
```bash
ffmpeg -version
```

### 3. 跨域问题
后端已配置CORS，允许所有来源访问。

## 调试模式

后端代码包含详细的DEBUG日志，可以在控制台查看详细的执行过程。

## API接口

### POST /api/translate
上传音频文件进行翻译

**参数:**
- `audio_chunk`: 音频文件 (multipart/form-data)
- `source_lang`: 源语言 (默认: zh)
- `target_lang`: 目标语言 (默认: en)

**响应:**
```json
{
  "status": "success",
  "translation": "翻译结果",
  "original": "原文",
  "history_record": {}
}
```

### GET /health
健康检查接口

**响应:**
```json
{
  "status": "healthy",
  "makawai_connected": true/false
}
```# Voice_API
