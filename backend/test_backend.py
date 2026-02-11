#!/usr/bin/env python3
"""
后端测试脚本
用于验证各个组件是否正常工作
"""

import asyncio
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.adapter.makawaiAdapter import MakawaiClient
from src.audio.converter import convert_to_makawai_format

async def test_makawai_connection():
    """测试Makawai连接"""
    print("=== 测试Makawai连接 ===")
    client = MakawaiClient()
    try:
        await client.connect(source_lang="zh", target_lang="en")
        print("✓ Makawai连接成功")
        
        # 发送一些测试数据
        test_pcm = b'\x00' * 1024  # 空的PCM数据
        await client.send_audio(test_pcm)
        print("✓ 音频发送成功")
        
        # 尝试接收结果
        result = await client.receive_result()
        print(f"✓ 接收结果: {result}")
        
    except Exception as e:
        print(f"✗ Makawai连接失败: {e}")
    finally:
        await client.close()

def test_audio_converter():
    """测试音频转换"""
    print("\n=== 测试音频转换 ===")
    try:
        # 创建一个简单的测试音频数据（WAV格式）
        import struct
        import wave
        
        # 创建一个简单的WAV文件数据
        sample_rate = 16000
        duration = 1  # 1秒
        frequency = 440  # 440Hz音调
        
        # 生成正弦波
        import math
        samples = []
        for i in range(int(sample_rate * duration)):
            sample = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(sample)
        
        # 转换为bytes
        test_wav_data = struct.pack('<' + 'h' * len(samples), *samples)
        print(f"✓ 生成测试音频数据: {len(test_wav_data)} 字节")
        
        # 测试转换
        pcm_data = convert_to_makawai_format(test_wav_data)
        print(f"✓ 音频转换成功: {len(pcm_data)} 字节PCM数据")
        
    except Exception as e:
        print(f"✗ 音频转换失败: {e}")

async def main():
    print("开始后端组件测试...\n")
    
    # 测试音频转换
    test_audio_converter()
    
    # 测试Makawai连接
    await test_makawai_connection()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())