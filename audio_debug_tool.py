#!/usr/bin/env python3
"""
音频解析调试工具
帮助诊断WebM音频解析问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from audio.converter import AudioProcessor
import numpy as np

def create_test_webm_audio():
    """创建一个简单的测试WebM音频"""
    # 生成一个简单的音频信号
    sample_rate = 44100
    duration = 1.0  # 1秒
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 生成440Hz正弦波
    audio_signal = np.sin(2 * np.pi * 440 * t) * 0.3
    
    # 转换为16-bit PCM
    pcm_data = (audio_signal * 32767).astype(np.int16)
    
    return pcm_data.tobytes()

def test_audio_processing():
    """测试音频处理功能"""
    print("=== 音频处理调试测试 ===")
    
    processor = AudioProcessor()
    
    # 测试1: 正常PCM数据
    print("\n1. 测试正常PCM数据:")
    test_pcm = create_test_webm_audio()
    print(f"   测试数据大小: {len(test_pcm)} 字节")
    
    try:
        result, success = processor.webm_to_pcm(test_pcm)
        status = "✓" if success and result else "✗"
        print(f"   {status} 处理结果: 成功={success}, 输出大小={len(result) if result else 0}")
    except Exception as e:
        print(f"   ✗ 处理异常: {e}")
    
    # 测试2: 小数据
    print("\n2. 测试小数据:")
    small_data = b'a' * 50
    try:
        result, success = processor.webm_to_pcm(small_data)
        status = "✓" if success and result else "✗"
        print(f"   {status} 处理结果: 成功={success}, 输出大小={len(result) if result else 0}")
    except Exception as e:
        print(f"   ✗ 处理异常: {e}")
    
    # 测试3: 模拟WebM头部数据
    print("\n3. 测试模拟WebM数据:")
    # 创建包含WebM头部的模拟数据
    webm_header = b'\x1a\x45\xdf\xa3' + b'\x00' * 100  # EBML header + 数据
    webm_data = webm_header + test_pcm[:1000]
    print(f"   WebM模拟数据大小: {len(webm_data)} 字节")
    
    try:
        result, success = processor.webm_to_pcm(webm_data)
        status = "✓" if success and result else "✗"
        print(f"   {status} 处理结果: 成功={success}, 输出大小={len(result) if result else 0}")
    except Exception as e:
        print(f"   ✗ 处理异常: {e}")

def analyze_audio_characteristics(audio_bytes):
    """分析音频数据特征"""
    print(f"\n=== 音频数据特征分析 ===")
    print(f"数据大小: {len(audio_bytes)} 字节")
    print(f"前16字节十六进制: {audio_bytes[:16].hex()}")
    
    # 检查是否包含WebM特征
    if b'\x1a\x45\xdf\xa3' in audio_bytes[:100]:
        print("✓ 检测到WebM EBML头部")
    
    # 检查数据分布
    if len(audio_bytes) > 100:
        # 尝试作为16-bit PCM解析
        try:
            audio_array = np.frombuffer(audio_bytes[:min(1000, len(audio_bytes))], dtype=np.int16)
            if len(audio_array) > 0:
                max_val = np.max(np.abs(audio_array))
                avg_val = np.mean(np.abs(audio_array))
                print(f"作为16-bit PCM解析:")
                print(f"  最大值: {max_val}")
                print(f"  平均绝对值: {avg_val}")
                print(f"  有效采样点数: {len(audio_array)}")
        except:
            print("无法作为16-bit PCM解析")

def main():
    """主函数"""
    print("开始音频解析调试...\n")
    
    # 运行处理测试
    test_audio_processing()
    
    # 创建一些测试数据进行分析
    print("\n" + "="*50)
    test_data = create_test_webm_audio()
    analyze_audio_characteristics(test_data)
    
    print("\n建议:")
    print("1. 如果处理总是失败并生成测试音频，说明输入数据格式可能不兼容")
    print("2. 可以尝试在前端调整录音参数:")
    print("   - 改变音频MIME类型")
    print("   - 调整比特率")
    print("   - 修改采样率")
    print("3. 查看详细的调试日志了解具体失败原因")

if __name__ == "__main__":
    main()