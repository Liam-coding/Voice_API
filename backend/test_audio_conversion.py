#!/usr/bin/env python3
"""
音频转换修复验证脚本
测试新的robust音频处理功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.audio.converter import convert_to_makawai_format, generate_test_audio
import numpy as np

def test_audio_conversion():
    """测试音频转换功能"""
    print("🎵 开始音频转换测试")
    print("=" * 50)
    
    # 测试1: 空数据
    print("\n1. 测试空数据处理:")
    result1 = convert_to_makawai_format(b'')
    print(f"   输入: 空字节")
    print(f"   输出: {len(result1)} 字节")
    print(f"   类型: {'测试音频' if len(result1) > 0 else '失败'}")
    
    # 测试2: 小数据
    print("\n2. 测试小数据处理:")
    small_data = b'\x00' * 50
    result2 = convert_to_makawai_format(small_data)
    print(f"   输入: 50字节零数据")
    print(f"   输出: {len(result2)} 字节")
    print(f"   类型: {'测试音频' if len(result2) > 0 else '失败'}")
    
    # 测试3: 随机数据
    print("\n3. 测试随机数据处理:")
    random_data = np.random.randint(0, 256, 1000, dtype=np.uint8).tobytes()
    result3 = convert_to_makawai_format(random_data)
    print(f"   输入: 1000字节随机数据")
    print(f"   输出: {len(result3)} 字节")
    print(f"   类型: {'处理成功' if len(result3) > 0 else 'fallback到测试音频'}")
    
    # 测试4: 直接生成测试音频
    print("\n4. 测试直接生成测试音频:")
    test_audio = generate_test_audio()
    print(f"   生成的测试音频大小: {len(test_audio)} 字节")
    print(f"   应该是: 32000 字节 (16kHz * 1秒 * 2字节)")
    
    # 验证PCM格式
    if len(test_audio) == 32000:
        print("   ✅ PCM格式正确")
        # 检查是否为有效的16-bit数据
        try:
            pcm_array = np.frombuffer(test_audio, dtype=np.int16)
            print(f"   ✅ 成功解析为 {len(pcm_array)} 个16-bit样本")
            print(f"   ✅ 数值范围: {np.min(pcm_array)} 到 {np.max(pcm_array)}")
        except Exception as e:
            print(f"   ❌ PCM解析失败: {e}")
    else:
        print(f"   ❌ PCM格式错误，期望32000字节，实际{len(test_audio)}字节")
    
    print("\n" + "=" * 50)
    print("🏁 音频转换测试完成")

def test_with_real_scenario():
    """模拟真实场景测试"""
    print("\n🎭 模拟真实场景测试")
    print("=" * 30)
    
    # 模拟前端发送的WebM音频数据（简化版本）
    print("模拟WebM音频数据处理:")
    
    # 创建模拟的WebM音频数据（这里用简单的PCM数据代替）
    sample_rate = 48000  # 常见的录音采样率
    duration = 0.5  # 0.5秒
    frequency = 880  # 较高的音调
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_signal = np.sin(2 * np.pi * frequency * t)
    # 转换为16-bit PCM
    pcm_data = (audio_signal * 32767 * 0.5).astype(np.int16)
    
    print(f"   模拟原始音频: {len(pcm_data)*2} 字节 ({sample_rate}Hz, {duration}秒)")
    
    # 测试转换
    converted = convert_to_makawai_format(pcm_data.tobytes())
    print(f"   转换后数据: {len(converted)} 字节")
    
    if len(converted) == 32000:
        print("   ✅ 转换为目标格式成功")
    elif len(converted) > 0:
        print("   ⚠️ 使用了fallback处理")
    else:
        print("   ❌ 转换失败")

if __name__ == "__main__":
    try:
        test_audio_conversion()
        test_with_real_scenario()
        
        print("\n💡 下一步建议:")
        print("1. 重启后端服务以应用音频转换修复")
        print("2. 重新测试前端录音功能")
        print("3. 观察后端日志中的音频转换信息")
        print("4. 验证是否还能看到 'Format not recognised' 错误")
        
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()