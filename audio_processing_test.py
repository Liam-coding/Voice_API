#!/usr/bin/env python3
"""
音频处理诊断和测试脚本
验证修复后的音频处理功能
"""

import sys
import os
import numpy as np
import io

# 添加src目录到路径
sys.path.insert(0, '/Users/jialei/code/voice-translation-web/backend/src')

from audio.converter import AudioProcessor

def test_audio_formats():
    """测试不同格式的音频处理"""
    print("=== 音频格式处理测试 ===\n")
    
    processor = AudioProcessor()
    
    # 1. 测试PCM数据
    print("1. 测试PCM格式数据:")
    pcm_data = (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 32767 * 0.3).astype(np.int16)
    result, success = processor.webm_to_pcm(pcm_data.tobytes())
    print(f"   PCM处理结果: {'成功' if success else '失败'}, 大小: {len(result) if success else 0} 字节\n")
    
    # 2. 测试短数据
    print("2. 测试短音频数据:")
    short_data = (np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600)) * 32767 * 0.3).astype(np.int16)
    result, success = processor.webm_to_pcm(short_data.tobytes())
    print(f"   短数据处理结果: {'成功' if success else '失败'}, 大小: {len(result) if success else 0} 字节\n")
    
    # 3. 测试低音量数据
    print("3. 测试低音量数据:")
    low_volume = (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 32767 * 0.001).astype(np.int16)
    result, success = processor.webm_to_pcm(low_volume.tobytes())
    print(f"   低音量处理结果: {'成功' if success else '失败'}, 大小: {len(result) if success else 0} 字节\n")
    
    # 4. 测试无效数据
    print("4. 测试无效数据:")
    invalid_data = b"this is not audio data at all"
    result, success = processor.webm_to_pcm(invalid_data)
    print(f"   无效数据处理结果: {'成功' if success else '失败'}, 大小: {len(result) if success else 0} 字节\n")

def test_lock_mechanism():
    """测试锁机制"""
    print("=== 异步锁机制测试 ===\n")
    
    # 导入修复后的锁机制
    sys.path.insert(0, '/Users/jialei/code/voice-translation-web/backend/src')
    import index
    
    try:
        lock = index.get_request_lock()
        print("✓ 锁机制初始化成功")
        print("✓ 锁类型:", type(lock))
    except Exception as e:
        print(f"✗ 锁机制测试失败: {e}")

def main():
    print("音频处理系统诊断工具")
    print("=" * 50)
    
    test_audio_formats()
    test_lock_mechanism()
    
    print("\n=== 测试完成 ===")
    print("请检查以上结果确认系统是否正常工作")

if __name__ == "__main__":
    main()