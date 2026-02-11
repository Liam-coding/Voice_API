# Makawai 实时语音翻译 API 规范

## 版本信息
- 版本: v2.1.3
- 更新日期: 2026-1-3
- 更新内容: 更新音频规格

## 核心特性
- 实时流式翻译，低延迟响应
- 支持10+语种互译
- 输出翻译后的语音 + 文本
- 支持原声克隆输出

## 连接信息
```
协议: WebSocket Secure (wss://)
域名: api.makaw.cn
路径: /partner_translate
端口: 443
完整URL: wss://api.makaw.cn/partner_translate
```

## 鉴权认证
推荐使用HTTP Header方式：
```
Authorization: Bearer sk-xxxxxxxxxxxxxxxx
```

## 支持语种
- zh: 中文 (Chinese)
- en: 英语 (English)
- ja: 日语 (Japanese)
- ko: 韩语 (Korean)
- ru: 俄语 (Russian)
- fr: 法语 (French)
- de: 德语 (German)
- es: 西班牙语 (Spanish)
- pt: 葡萄牙语 (Portuguese)
- it: 意大利语 (Italian)

## 音频规格要求

### 输入音频规格 (Client → Server)
- 编码格式: Opus（推荐）或 PCM
- 采样率: 16000 Hz (16kHz)
- 声道数: 1 (单声道 Mono)
- 位深度: 16-bit (PCM时)
- 帧时长: 20ms / 40ms / 60ms（推荐60ms）
- 每帧采样数: 320 / 640 / 960

### 输出音频规格 (Server → Client)
- 编码格式: Opus
- 采样率: 24000 Hz (24kHz)
- 声道数: 1 (单声道 Mono)

## 数据协议

### 客户端请求格式
```json
{
  "samples_bytes": "<Base64编码的音频数据>"
}
```

### 服务端响应格式
```json
{
  "format": "opus",
  "audio_data": "<Base64编码的翻译后音频>",
  "translated_text": "Hello, how are you?",
  "frame_size": 960,
  "status": "active"
}
```

## WebSocket错误码

### 连接关闭码
- 1000: Normal Closure (正常关闭)
- 4001: Auth Required (未提供鉴权信息)
- 4003: Auth Failed (鉴权失败)

### 业务错误
```json
{
  "result": "failed",
  "err_msg": "错误描述信息",
  "status": "stopped"
}
```

## 关键技术要点

1. **音频编码**: 必须使用Opus编码，不能直接发送PCM数据
2. **数据传输**: 所有音频数据都需要Base64编码后通过JSON传输
3. **帧同步**: 推荐使用60ms帧（960个采样点）以平衡延迟和识别效果
4. **采样率转换**: 输入16kHz，输出24kHz，需要适当的重采样处理