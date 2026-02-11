import websockets
import json
import asyncio
import traceback
import time


class MakawaiClient:
    def __init__(self):
        self.ws = None
        self.last_activity_time = 0
        self.is_processing = False

    async def connect(self, source_lang="zh", target_lang="en"):
        from config.api_config import MAKAWAI_WS_URL, MAKAWAI_API_KEY
        
        # 确保 URL 是字符串
        base_url = str(MAKAWAI_WS_URL).strip()
        url = f"{base_url}?source_lang={source_lang}&target_lang={target_lang}"

        headers = {
            "Authorization": f"Bearer {MAKAWAI_API_KEY}"
        }

        print(f"DEBUG: 正在连接到 Makawai WebSocket: {url}")
        try:
            if self.ws:
                await self.ws.close()
            self.ws = await websockets.connect(url, additional_headers=headers)
            print("DEBUG: Makawai WebSocket 连接成功")
        except Exception as e:
            print(f"DEBUG: Makawai WebSocket 连接失败: {str(e)}")
            print(f"DEBUG: 详细错误信息: {traceback.format_exc()}")
            raise e

    async def send_audio(self, pcm_bytes):
        """发送音频二进制数据"""
        # 防止并发访问
        if self.is_processing:
            raise Exception("当前正在处理其他请求，请稍后再试")
            
        # 正确检查WebSocket连接状态
        if self.ws and hasattr(self.ws, 'open') and self.ws.open:
            try:
                self.is_processing = True
                self.last_activity_time = time.time()
                
                # 记录更多调试信息
                print(f"DEBUG: 准备发送音频数据...")
                print(f"DEBUG: PCM数据前10字节: {pcm_bytes[:10].hex() if len(pcm_bytes) > 0 else '无数据'}")
                print(f"DEBUG: PCM数据总长度: {len(pcm_bytes)} 字节")
                
                # Makawai 接收二进制 PCM 数据流
                await self.ws.send(pcm_bytes)
                print(f"DEBUG: 已发送音频数据，大小: {len(pcm_bytes)} 字节")
            except Exception as e:
                print(f"DEBUG: 发送音频失败: {str(e)}")
                self.is_processing = False
                raise Exception(f"发送音频失败: {str(e)}")
        elif self.ws:  # 连接对象存在但状态不确定
            try:
                self.is_processing = True
                self.last_activity_time = time.time()
                # 尝试发送，让异常自然抛出
                await self.ws.send(pcm_bytes)
                print(f"DEBUG: 已发送音频数据，大小: {len(pcm_bytes)} 字节")
            except Exception as e:
                print(f"DEBUG: 发送音频失败: {str(e)}")
                self.is_processing = False
                raise Exception(f"发送音频失败: {str(e)}")
        else:
            raise Exception("WebSocket 未连接，无法发送音频")

    async def receive_result(self):
        """接收并解析翻译结果 - 符合API规范"""
        try:
            print("DEBUG: 等待Makawai响应...")
            message = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
            print(f"DEBUG: 收到响应: {message[:100]}...")
            
            # 解析JSON响应
            result = json.loads(message)
            print(f"DEBUG: 解析结果: {result}")
            
            # 检查业务错误
            if result.get('result') == 'failed':
                error_msg = result.get('err_msg', '未知错误')
                print(f"DEBUG: 业务错误: {error_msg}")
                return {
                    "translation": "",
                    "original": "",
                    "status": "error",
                    "error_message": error_msg
                }
            
            # 提取翻译文本
            translation = result.get('translated_text', '').strip()
            status = result.get('status', 'active')
            
            # 解码音频数据（如果存在）
            audio_bytes = None
            if 'audio_data' in result:
                try:
                    audio_bytes = base64.b64decode(result['audio_data'])
                except Exception as e:
                    print(f"DEBUG: 音频解码失败: {e}")
            
            return {
                "translation": translation,
                "original": "",
                "status": status,
                "audio_bytes": audio_bytes,
                "raw_response": result
            }
            
        except asyncio.TimeoutError:
            print("DEBUG: 接收超时")
            return {"translation": "", "original": "", "status": "timeout"}
        except websockets.exceptions.ConnectionClosedOK:
            print("DEBUG: 连接正常关闭")
            return {"translation": "", "original": "", "status": "closed"}
        except Exception as e:
            print(f"DEBUG: 接收错误: {e}")
            return {"translation": "", "original": "", "status": "error"}
        finally:
            self.is_processing = False

    async def close(self):
        if self.ws:
            try:
                # 如果还在处理中，等待一小段时间
                if self.is_processing:
                    print("DEBUG: 等待当前处理完成...")
                    await asyncio.sleep(0.1)
                await self.ws.close()
                print("DEBUG: Makawai WebSocket 连接已关闭")
            except Exception as e:
                print(f"DEBUG: 关闭连接时出错: {str(e)}")
            finally:
                self.ws = None
                self.is_processing = False