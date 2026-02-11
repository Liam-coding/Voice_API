import asyncio
import sys
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import traceback
from typing import Optional

# 确保路径正确
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入改进的模块
from audio.improved_converter import AudioProcessor
from adapter.improved_makawai_adapter import MakawaiClient

# 全局实例
makawai_client: Optional[MakawaiClient] = None
audio_processor = AudioProcessor()
_request_lock: Optional[asyncio.Lock] = None

def get_request_lock():
    """获取请求锁"""
    global _request_lock
    if _request_lock is None:
        _request_lock = asyncio.Lock()
    return _request_lock

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global makawai_client
    
    print("🚀 启动语音翻译服务...")
    
    # 初始化连接
    max_init_retries = 3
    for attempt in range(max_init_retries):
        try:
            print(f"📡 尝试连接Makawai服务 (第{attempt + 1}次)...")
            makawai_client = MakawaiClient()
            
            if await makawai_client.connect(source_lang="zh", target_lang="en"):
                print("✅ Makawai服务连接成功")
                break
            else:
                print(f"❌ Makawai服务连接失败 (第{attempt + 1}次)")
                if attempt < max_init_retries - 1:
                    await asyncio.sleep(2)  # 等待后重试
                    
        except Exception as e:
            print(f"💥 连接异常: {e}")
            if attempt < max_init_retries - 1:
                await asyncio.sleep(2)
    
    if not makawai_client or not makawai_client.is_connected():
        print("⚠️ 警告: Makawai服务连接失败，将在收到请求时尝试重新连接")
        makawai_client = None
    
    yield
    
    # 关闭连接
    print("🧹 正在关闭服务...")
    if makawai_client:
        try:
            await makawai_client.close()
        except Exception as e:
            print(f"⚠️ 关闭连接时出错: {e}")
    print("👋 服务已关闭")

# 初始化应用
app = FastAPI(
    title="语音翻译API",
    description="实时语音翻译服务",
    version="2.0.0",
    lifespan=lifespan
)

# CORS配置
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
    """音频翻译接口"""
    global makawai_client
    
    print(f"🌐 收到翻译请求 - {source_lang} → {target_lang}")
    print(f"📁 音频文件: {audio_chunk.filename}")
    
    async with get_request_lock():
        try:
            # 验证输入
            if not audio_chunk or not audio_chunk.filename:
                raise HTTPException(status_code=400, detail="未提供音频文件")
            
            # 读取音频数据
            content = await audio_chunk.read()
            print(f"📊 接收音频数据: {len(content)} 字节")
            
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="音频文件为空")
            
            # 音频处理
            print("🔄 处理音频数据...")
            pcm_bytes, success = audio_processor.webm_to_pcm(content)
            
            if not success:
                raise HTTPException(status_code=400, detail="音频处理失败")
            
            print(f"✅ 音频处理完成: {len(pcm_bytes)} 字节PCM数据")
            
            # 确保连接有效
            await _ensure_connection(source_lang, target_lang)
            
            # 发送音频数据
            print("📤 发送音频到翻译服务...")
            await makawai_client.send_audio(pcm_bytes)
            
            # 接收翻译结果
            print("📥 等待翻译结果...")
            result = await makawai_client.receive_result()
            
            # 处理结果
            return _process_translation_result(result)
            
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"翻译处理失败: {str(e)}"
            print(f"💥 {error_msg}")
            print(f"📋 详细错误: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)

async def _ensure_connection(source_lang: str, target_lang: str):
    """确保WebSocket连接有效"""
    global makawai_client
    
    max_retries = 3
    
    for attempt in range(max_retries):
        # 检查现有连接
        if makawai_client and makawai_client.is_connected():
            # 尝试ping测试
            if await makawai_client.ping_server():
                print("✅ 连接状态良好")
                return
            else:
                print("⚠️ 连接可能已断开")
        
        # 重新连接
        print(f"🔄 尝试重新连接 (第{attempt + 1}次)...")
        try:
            if makawai_client:
                await makawai_client.close()
            
            makawai_client = MakawaiClient()
            if await makawai_client.connect(source_lang, target_lang):
                print("✅ 重新连接成功")
                return
            else:
                print(f"❌ 重新连接失败 (第{attempt + 1}次)")
                
        except Exception as e:
            print(f"💥 重新连接异常: {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(1)
    
    raise HTTPException(status_code=503, detail="无法连接到翻译服务")

def _process_translation_result(result: dict):
    """处理翻译结果"""
    status = result.get("status", "unknown")
    
    print(f"📊 翻译结果状态: {status}")
    
    if status == "success":
        translation = result.get("translation", "").strip()
        original = result.get("original", "").strip()
        
        response = {
            "status": "success",
            "translation": translation,
            "original": original
        }
        
        # 如果有音频数据，也返回
        if result.get("audio_bytes"):
            response["audio_available"] = True
        
        print(f"✅ 翻译成功: '{translation}'")
        return response
        
    elif status == "error":
        error_msg = result.get("error_message", "未知错误")
        print(f"❌ 翻译错误: {error_msg}")
        raise HTTPException(status_code=500, detail=f"翻译服务错误: {error_msg}")
        
    elif status == "timeout":
        print("⏰ 翻译超时")
        raise HTTPException(status_code=504, detail="翻译服务超时")
        
    elif status == "closed":
        print("🔌 连接已关闭")
        raise HTTPException(status_code=503, detail="翻译服务连接中断")
        
    else:
        print(f"❓ 未知状态: {status}")
        raise HTTPException(status_code=500, detail=f"未知错误状态: {status}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    connected = False
    status_details = {}
    
    if makawai_client:
        connected = makawai_client.is_connected()
        status_details = {
            "connection_attempts": getattr(makawai_client, 'connection_attempts', 0),
            "is_processing": getattr(makawai_client, 'is_processing', False),
            "last_activity": getattr(makawai_client, 'last_activity_time', 0)
        }
    
    return {
        "status": "healthy" if connected else "degraded",
        "makawai_connected": connected,
        "details": status_details
    }

@app.get("/api/status")
async def service_status():
    """详细服务状态"""
    return {
        "service": "Voice Translation API",
        "version": "2.0.0",
        "audio_processor": {
            "sample_rate": audio_processor.sample_rate,
            "supported_formats": ["webm", "wav", "pcm"]
        },
        "supported_languages": ["zh", "en", "ja", "ko", "ru", "fr", "de", "es", "pt", "it"],
        "health": await health_check()
    }

if __name__ == "__main__":
    print("🚀 启动语音翻译服务...")
    uvicorn.run(
        "improved_index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )