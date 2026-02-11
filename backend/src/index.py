import asyncio
import sys
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import traceback

# 1. 确保路径正确（防止 ModuleNotFoundError）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.converter import AudioProcessor
from adapter.makawaiAdapter import MakawaiClient

# 全局实例
makawai_client = None
audio_processor = AudioProcessor()
# 使用弱引用避免循环引用问题
import weakref
_request_lock = None

def get_request_lock():
    global _request_lock
    if _request_lock is None:
        _request_lock = asyncio.Lock()
    return _request_lock

# 2. 定义生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    global makawai_client
    # 启动时：连接 API
    print("DEBUG: 正在启动并连接 Makawai 服务...")
    try:
        makawai_client = MakawaiClient()
        await makawai_client.connect(source_lang="zh", target_lang="en")
        print("DEBUG: Makawai 连接成功")
    except Exception as e:
        print(f"DEBUG: Makawai 连接失败: {e}")
        print(f"DEBUG: 详细错误信息: {traceback.format_exc()}")
        # 即使连接失败也继续启动，后续请求会重新尝试连接
        makawai_client = None
    yield
    # 关闭时：断开连接
    if makawai_client and makawai_client.ws:
        try:
            await makawai_client.close()
        except Exception as e:
            print(f"DEBUG: 关闭 Makawai 连接时出错: {e}")
    print("DEBUG: 应用已关闭")

# 3. 初始化 App（只定义一次！）
app = FastAPI(lifespan=lifespan)

# 4. 配置跨域（必须在 app 定义之后）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/translate")
async def translate_audio(
        audio_chunk: UploadFile = File(...),
        source_lang: str = Form("zh"),
        target_lang: str = Form("en")
):
    global makawai_client
    
    # 记录请求信息
    print(f"🌐 收到翻译请求 - 源语言: {source_lang}, 目标语言: {target_lang}")
    print(f"📁 音频文件名: {audio_chunk.filename if audio_chunk else '未知'}")
    
    # 使用锁防止并发请求冲突
    async with get_request_lock():

        try:
            print(f"DEBUG: 收到翻译请求 - 源语言: {source_lang}, 目标语言: {target_lang}")

            # 检查文件
            if not audio_chunk or not audio_chunk.filename:
                raise HTTPException(status_code=400, detail="未提供音频文件")

            content = await audio_chunk.read()
            print(f"DEBUG: 接收到音频数据大小: {len(content)} 字节")

            if len(content) == 0:
                raise HTTPException(status_code=400, detail="音频文件为空")

            # 音频处理 - 符合API规范
            print("DEBUG: 开始音频处理...")
            pcm_bytes, success = audio_processor.webm_to_pcm(content)
            if not success:
                raise HTTPException(status_code=400, detail="音频质量不符合要求")
            print(f"DEBUG: 处理后PCM数据大小: {len(pcm_bytes)} 字节")

            # 检查连接状态，必要时重新连接
            connection_valid = False
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries and not connection_valid:
                if makawai_client and makawai_client.ws:
                    # 检查连接是否有效
                    try:
                        if hasattr(makawai_client.ws, 'open'):
                            connection_valid = makawai_client.ws.open
                        else:
                            # 如果没有open属性，尝试发送ping来测试连接
                            try:
                                await makawai_client.ws.ping()
                                connection_valid = True
                            except:
                                connection_valid = False
                    except Exception as e:
                        print(f"DEBUG: 连接状态检查失败: {e}")
                        connection_valid = False

                if not connection_valid:
                    retry_count += 1
                    print(f"DEBUG: Makawai 连接无效，尝试重新连接... (第{retry_count}次)")
                    try:
                        if makawai_client:
                            await makawai_client.close()
                        makawai_client = MakawaiClient()
                        await makawai_client.connect(source_lang=source_lang, target_lang=target_lang)
                        print("DEBUG: Makawai 重新连接成功")
                        connection_valid = True
                    except Exception as e:
                        print(f"DEBUG: Makawai 重新连接失败: {e}")
                        if retry_count >= max_retries:
                            raise HTTPException(status_code=500, detail=f"Makawai 连接失败: {str(e)}")
                        # 等待一段时间再重试
                        await asyncio.sleep(1)

            # 转发音频数据
            print("DEBUG: 发送音频到 Makawai...")
            try:
                await makawai_client.send_audio(pcm_bytes)
            except Exception as e:
                print(f"DEBUG: 发送音频到Makawai失败: {e}")
                # 如果发送失败，尝试重新连接后重试一次
                try:
                    if makawai_client:
                        await makawai_client.close()
                    makawai_client = MakawaiClient()
                    await makawai_client.connect(source_lang=source_lang, target_lang=target_lang)
                    print("DEBUG: 重新连接后再次尝试发送音频...")
                    await makawai_client.send_audio(pcm_bytes)
                except Exception as retry_e:
                    print(f"DEBUG: 重试发送也失败: {retry_e}")
                    raise HTTPException(status_code=500, detail=f"发送音频失败: {str(retry_e)}")

            # 获取翻译结果
            print("DEBUG: 等待 Makawai 响应...")
            result = await makawai_client.receive_result()
            print(f"DEBUG: Makawai 返回结果 -> {result}")

            # 检查结果状态
            result_status = result.get("status", "unknown")
            if result_status == "error":
                error_msg = result.get('error_message', result.get('translation', '未知错误'))
                raise HTTPException(status_code=500, detail=f"翻译服务错误: {error_msg}")
            elif result_status == "empty_result":
                error_msg = result.get('error_message', '未检测到可翻译内容')
                raise HTTPException(status_code=400, detail=f"音频处理失败: {error_msg}")
            elif result_status == "timeout":
                raise HTTPException(status_code=504, detail="翻译服务超时")

            return {
                "status": "success",
                "translation": result.get("translation", ""),
                "original": result.get("original", ""),
                "history_record": result
            }

        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            print(f"DEBUG: {error_msg}")
            print(f"DEBUG: 详细错误信息: {traceback.format_exc()}")
            # 确保释放锁
            raise HTTPException(status_code=500, detail=error_msg)
        # 锁会在async with块结束时自动释放

# 健康检查端点
@app.get("/health")
async def health_check():
    # 更准确的连接状态检测
    connected = False
    if makawai_client and makawai_client.ws:
        try:
            if hasattr(makawai_client.ws, 'open'):
                connected = makawai_client.ws.open
            else:
                # 尝试ping测试
                try:
                    await makawai_client.ws.ping()
                    connected = True
                except:
                    connected = False
        except Exception:
            connected = False
    
    return {
        "status": "healthy",
        "makawai_connected": connected
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)