#!/usr/bin/env python3
"""
音频格式测试脚本
用于验证音频转换和Makawai API的兼容性
"""

import asyncio
import aiohttp
import numpy as np
import wave
import io

def create_wav_file(sample_rate=44100, duration=2.0, frequency=440):
    """创建一个WAV文件用于测试"""
    print(f"🎵 创建测试WAV文件 - 采样率: {sample_rate}Hz, 持续时间: {duration}秒, 频率: {frequency}Hz")
    
    # 生成音频数据
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # 生成复合音（基频 + 泛音）
    audio_data = (
        np.sin(2 * np.pi * frequency * t) +  # 基频
        0.3 * np.sin(2 * np.pi * 2 * frequency * t) +  # 二次谐波
        0.1 * np.sin(2 * np.pi * 3 * frequency * t)    # 三次谐波
    )
    
    # 转换为16-bit PCM
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # 创建WAV文件
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    wav_buffer.seek(0)
    wav_bytes = wav_buffer.read()
    print(f"✅ WAV文件创建完成，大小: {len(wav_bytes)} 字节")
    return wav_bytes

async def test_with_generated_audio():
    """使用生成的音频进行测试"""
    print("\n🧪 使用生成的音频进行测试")
    
    # 创建不同采样率的测试音频
    test_cases = [
        (44100, 1.0, 440, "44.1kHz测试音频"),
        (22050, 1.0, 880, "22.05kHz测试音频"), 
        (16000, 1.5, 330, "16kHz测试音频"),
        (8000, 1.0, 220, "8kHz测试音频")
    ]
    
    async with aiohttp.ClientSession() as session:
        for sample_rate, duration, freq, description in test_cases:
            print(f"\n--- 测试 {description} ---")
            
            # 生成音频
            audio_data = create_wav_file(sample_rate, duration, freq)
            
            # 发送到后端
            try:
                form_data = aiohttp.FormData()
                form_data.add_field('audio_chunk', audio_data, filename='test.wav', content_type='audio/wav')
                form_data.add_field('source_lang', 'zh')
                form_data.add_field('target_lang', 'en')
                
                print(f"📤 发送音频数据 ({len(audio_data)} 字节)...")
                async with session.post('http://localhost:8000/api/translate', data=form_data) as response:
                    print(f"📥 收到响应，状态码: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ 翻译成功:")
                        print(f"   状态: {result.get('status')}")
                        print(f"   翻译: '{result.get('translation')}'")
                        print(f"   原文: '{result.get('original')}'")
                    else:
                        error_text = await response.text()
                        print(f"❌ 翻译失败:")
                        print(f"   状态码: {response.status}")
                        print(f"   错误信息: {error_text}")
                        
            except Exception as e:
                print(f"💥 请求异常: {str(e)}")

async def test_health_endpoint():
    """测试健康检查端点"""
    print("\n🏥 测试健康检查端点")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 健康检查成功:")
                    print(f"   系统状态: {result.get('status')}")
                    print(f"   Makawai连接: {result.get('makawai_connected')}")
                    return True
                else:
                    print(f"❌ 健康检查失败 (状态码: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🎼 开始音频格式兼容性测试")
    print("=" * 50)
    
    # 首先测试健康检查
    if not await test_health_endpoint():
        print("❌ 后端服务不可用，请先启动后端服务")
        return
    
    # 测试各种音频格式
    await test_with_generated_audio()
    
    print("\n" + "=" * 50)
    print("🏁 音频格式测试完成")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")