import websockets
import json
import asyncio
import traceback
import time
import ssl
import base64
from typing import Optional, Dict, Any


class ImprovedMakawaiClient:
    """
    改进版Makawai客户端
    - 更稳定的连接管理
    - 更好的错误处理
    - 支持实时音频流传输
    """
    
    def __init__(self):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.last_activity_time = 0
        self.is_processing = False
        self.connection_attempts = 0
        self.max_retries = 3
        self.ssl_context = ssl.create_default_context()
        
    async def connect(self, source_lang: str = "zh", target_lang: str = "en") -> bool:
        """建立WebSocket连接"""
        from config.api_config import MAKAWAI_WS_URL, MAKAWAI_API_KEY
        
        # 防止无限重连
        if self.connection_attempts >= self.max_retries:
            print(f"DEBUG: 达到最大重连次数 {self.max_retries}")
            return False
            
        try:
            # 清理旧连接
            if self.ws:
                await self.close()
            
            # 构建连接URL
            base_url = str(MAKAWAI_WS_URL).strip()
            url = f"{base_url}?source_lang={source_lang}&target_lang={target_lang}"
            
            headers = {
                "Authorization": f"Bearer {MAKAWAI_API_KEY}",
                "User-Agent": "VoiceTranslationClient/1.0"
            }
            
            print(f"DEBUG: 连接到 {url}")
            
            # 建立连接
            self.ws = await websockets.connect(
                url, 
                additional_headers=headers,
                ssl=self.ssl_context,
                timeout=10.0
            )
            
            print("DEBUG: WebSocket连接建立成功")
            self.connection_attempts = 0  # 重置重连计数
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            self.connection_attempts += 1
            print(f"DEBUG: 连接失败 (尝试 {self.connection_attempts}/{self.max_retries}): {e}")
            print(f"DEBUG: 详细错误: {traceback.format_exc()}")
            return False
    
    async def send_audio_stream(self, audio_generator):
        """发送音频流数据"""
        if not self.ws:
            raise Exception("WebSocket未连接")
            
        if self.is_processing:
            raise Exception("当前正在处理其他请求")
            
        try:
            self.is_processing = True
            self.last_activity_time = time.time()
            
            print("DEBUG: 开始发送音频流...")
            
            async for audio_chunk in audio_generator:
                if not self.ws or not hasattr(self.ws, 'open') or not self.ws.open:
                    raise Exception("WebSocket连接已断开")
                
                # 发送音频数据
                await self.ws.send(audio_chunk)
                print(f"DEBUG: 发送音频块: {len(audio_chunk)} 字节")
                
                # 保持活跃状态
                self.last_activity_time = time.time()
                
            # 发送结束标记
            await self.ws.send(b"")
            print("DEBUG: 音频流发送完成")
            
        except Exception as e:
            print(f"DEBUG: 音频流发送失败: {e}")
            raise
        finally:
            self.is_processing = False
    
    async def send_audio(self, pcm_bytes: bytes):
        """发送单次音频数据"""
        if not self.ws:
            raise Exception("WebSocket未连接")
            
        if self.is_processing:
            raise Exception("当前正在处理其他请求")
            
        try:
            self.is_processing = True
            self.last_activity_time = time.time()
            
            print(f"DEBUG: 发送音频数据: {len(pcm_bytes)} 字节")
            print(f"DEBUG: 数据前16字节: {pcm_bytes[:16].hex()}")
            
            await self.ws.send(pcm_bytes)
            print("DEBUG: 音频数据发送成功")
            
        except Exception as e:
            print(f"DEBUG: 音频发送失败: {e}")
            raise
        finally:
            self.is_processing = False
    
    async def receive_result(self) -> Dict[str, Any]:
        """接收翻译结果"""
        if not self.ws:
            return {"status": "error", "error_message": "WebSocket未连接"}
            
        try:
            print("DEBUG: 等待翻译结果...")
            
            # 设置超时
            message = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
            print(f"DEBUG: 收到响应: {message[:100]}...")
            
            # 解析响应
            try:
                result = json.loads(message)
                print(f"DEBUG: 解析结果: {result}")
                
                # 处理业务错误
                if result.get('result') == 'failed':
                    return {
                        "status": "error",
                        "error_message": result.get('err_msg', '未知错误'),
                        "translation": "",
                        "original": ""
                    }
                
                # 提取翻译文本
                translation = result.get('translated_text', '').strip()
                original = result.get('original_text', '').strip()
                
                # 解码音频数据（如果存在）
                audio_bytes = None
                if 'audio_data' in result:
                    try:
                        audio_bytes = base64.b64decode(result['audio_data'])
                        print(f"DEBUG: 解码音频数据: {len(audio_bytes)} 字节")
                    except Exception as e:
                        print(f"DEBUG: 音频解码失败: {e}")
                
                return {
                    "status": "success",
                    "translation": translation,
                    "original": original,
                    "audio_bytes": audio_bytes,
                    "raw_response": result
                }
                
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON解析失败: {e}")
                return {
                    "status": "error", 
                    "error_message": f"响应格式错误: {str(e)}",
                    "translation": "",
                    "original": ""
                }
                
        except asyncio.TimeoutError:
            print("DEBUG: 接收超时")
            return {
                "status": "timeout",
                "error_message": "翻译服务超时",
                "translation": "",
                "original": ""
            }
        except websockets.exceptions.ConnectionClosed:
            print("DEBUG: 连接已关闭")
            return {
                "status": "closed",
                "error_message": "连接已关闭",
                "translation": "",
                "original": ""
            }
        except Exception as e:
            print(f"DEBUG: 接收错误: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "translation": "",
                "original": ""
            }
        finally:
            self.is_processing = False
    
    async def ping_server(self) -> bool:
        """Ping服务器检查连接状态"""
        if not self.ws:
            return False
            
        try:
            await self.ws.ping()
            self.last_activity_time = time.time()
            return True
        except Exception as e:
            print(f"DEBUG: Ping失败: {e}")
            return False
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self.ws:
            return False
            
        try:
            return hasattr(self.ws, 'open') and self.ws.open
        except Exception:
            return False
    
    async def close(self):
        """关闭连接"""
        if self.ws:
            try:
                if self.is_processing:
                    print("DEBUG: 等待当前处理完成...")
                    await asyncio.sleep(0.1)
                
                await self.ws.close()
                print("DEBUG: WebSocket连接已关闭")
            except Exception as e:
                print(f"DEBUG: 关闭连接时出错: {e}")
            finally:
                self.ws = None
                self.is_processing = False
                self.connection_attempts = 0


# 向后兼容的包装类
class MakawaiClient(ImprovedMakawaiClient):
    """保持与现有代码兼容的客户端"""
    pass