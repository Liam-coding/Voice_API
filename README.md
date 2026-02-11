# 🎙️ Makawai 实时语音翻译系统

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

**中英实时语音互译 | WebSocket连接 | 现代Web技术栈**

</div>

## 🌟 项目特色

- 🎯 **实时翻译** - 支持中英双向实时语音翻译
- 🔄 **WebSocket通信** - 高效稳定的双向通信协议
- 🎤 **智能录音** - 自适应音频质量检测与处理
- 🌐 **现代化前端** - Vue 3 + Vite 构建的响应式界面
- 🔧 **完善调试** - 丰富的调试工具和详细日志
- 🛡️ **健壮架构** - 自动重连、异常处理、并发控制

## 🏗️ 技术架构

```
voice-translation-web/
├── backend/                    # Python后端服务
│   ├── src/                   
│   │   ├── adapter/           # Makawai API适配器
│   │   ├── audio/             # 音频处理模块
│   │   └── index.py           # FastAPI主应用
│   ├── requirements.txt       # Python依赖
│   └── config/                # 配置文件
└── frontend/                  # Vue.js前端应用
    ├── src/                   
    │   ├── components/        # Vue组件
    │   ├── stores/            # Pinia状态管理
    │   └── App.vue            # 主应用组件
    └── package.json           # Node.js依赖
```

## 🚀 快速开始

### 系统要求

**后端环境:**
- Python 3.8+
- FFmpeg (音频处理)

**前端环境:**
- Node.js 16+
- npm 或 yarn

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd voice-translation-web

# 使用启动脚本（推荐）
chmod +x start_dev.sh
./start_dev.sh
```

### 手动安装

```bash
# 1. 安装FFmpeg (Mac)
brew install ffmpeg

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 启动后端服务
python src/index.py
# 服务将运行在 http://localhost:8000

cd ..

# 4. 安装前端依赖
cd frontend
npm install

# 5. 启动前端开发服务器
npm run dev
# 应用将运行在 http://localhost:5173
```

## 🎯 核心功能

### 🎤 实时语音录制
- 基于Web Audio API的高质量录音
- 智能音频质量检测
- 自适应降噪处理

### 🌐 WebSocket实时通信
- 稳定的双向通信连接
- 自动重连机制
- 连接状态监控

### 🔄 智能翻译处理
- 支持中英双向翻译
- 音频格式自适应转换
- 翻译结果缓存管理

### 📊 用户界面
- 响应式设计适配多设备
- 实时录音状态指示
- 翻译历史记录展示
- 直观的操作反馈

## 🔧 API接口文档

### POST `/api/translate`
**语音翻译接口**

```bash
# 示例请求
curl -X POST http://localhost:8000/api/translate \
  -F "audio_chunk=@recording.webm" \
  -F "source_lang=zh" \
  -F "target_lang=en"
```

**请求参数:**
- `audio_chunk` *(required)*: 音频文件 (multipart/form-data)
- `source_lang` *(optional)*: 源语言，默认 `zh`
- `target_lang` *(optional)*: 目标语言，默认 `en`

**响应示例:**
```json
{
  "status": "success",
  "translation": "Hello world",
  "original": "你好世界",
  "history_record": {
    "timestamp": "2024-01-01T10:30:00Z",
    "duration": 2.5
  }
}
```

### GET `/health`
**服务健康检查**

```bash
curl http://localhost:8000/health
```

**响应示例:**
```json
{
  "status": "healthy",
  "makawai_connected": true,
  "uptime": 3600
}
```

## 🛠️ 调试与测试

### 内置调试工具

项目提供多个调试页面帮助快速定位问题：

- `http://localhost:5173/debug.html` - 基础连接调试
- `http://localhost:5173/button_test.html` - 按钮功能测试
- `http://localhost:5173/detailed_debug.html` - 详细诊断面板

### 后端测试脚本

```bash
# 运行后端测试
cd backend
python test_backend.py

# 测试连接稳定性
python test_connection_fix.py

# 音频处理测试
python test_audio_conversion.py
```

### 常见问题排查

**1. WebSocket连接失败**
```bash
# 检查后端连接状态
curl http://localhost:8000/health

# 查看详细日志
# 在后端终端查看DEBUG输出
```

**2. 音频录制问题**
- 确认浏览器麦克风权限已授权
- 检查HTTPS环境（生产环境）
- 验证MediaRecorder API支持

**3. 翻译结果为空**
- 检查音频质量是否达标
- 确认Makawai API密钥配置正确
- 验证网络连接稳定性

## 📈 性能优化

### 后端优化
- 异步处理提升并发能力
- 连接池管理减少重复连接
- 智能重试机制提高稳定性

### 前端优化
- 组件懒加载减少初始包大小
- 音频数据流式处理
- 状态管理优化渲染性能

## 🔒 安全考虑

- CORS策略配置
- 请求频率限制
- 输入数据验证
- 敏感信息配置分离

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

### 开发规范
1. 遵循现有代码风格
2. 添加必要的测试用例
3. 更新相关文档
4. 确保CI/CD通过

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Makawai](https://makawai.com) - 语音翻译API服务
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) - 浏览器音频处理

## 📧 联系方式

如有任何问题或建议，请联系：**jialei.liu.sh@gmail.com**

---

<div align="center">

**✨ 让沟通无障碍，让世界更紧密 ✨**

[问题反馈](https://github.com/your-repo/issues) · [功能建议](https://github.com/your-repo/discussions)

</div>