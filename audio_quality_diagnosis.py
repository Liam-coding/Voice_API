#!/usr/bin/env python3
"""
音频质量诊断测试脚本
用于分析和调试音频质量问题
"""

import sys
import os
import numpy as np
import librosa
import io

# 添加src目录到路径
sys.path.insert(0, '/Users/jialei/code/voice-translation-web/backend/src')

from audio.converter import AudioProcessor

def analyze_audio_chunk(audio_bytes, description="未知音频"):
    """分析音频数据块"""
    print(f"\n=== {description} 分析 ===")
    print(f"数据大小: {len(audio_bytes)} 字节")
    
    try:
        # 使用AudioProcessor分析
        processor = AudioProcessor()
        audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        
        print(f"采样率: {sr}Hz")
        print(f"采样点数: {len(audio_data)}")
        print(f"时长: {len(audio_data)/16000:.3f} 秒")
        print(f"最大振幅: {np.max(np.abs(audio_data)):.4f}")
        print(f"RMS能量: {np.sqrt(np.mean(audio_data**2)):.4f}")
        print(f"平均振幅: {np.mean(np.abs(audio_data)):.4f}")
        
        # 质量评估
        quality_result = processor._assess_audio_quality(audio_data)
        print(f"质量评估: {'通过' if quality_result['acceptable'] else '不通过'}")
        if not quality_result['acceptable']:
            print(f"原因: {quality_result['reason']}")
        
        # 尝试转换
        pcm_result, success = processor.webm_to_pcm(audio_bytes)
        print(f"转换结果: {'成功' if success else '失败'}")
        if success:
            print(f"PCM大小: {len(pcm_result)} 字节")
        
    except Exception as e:
        print(f"分析失败: {e}")

def generate_test_samples():
    """生成不同质量的测试样本"""
    print("\n=== 生成测试样本 ===")
    
    processor = AudioProcessor()
    sample_rate = 16000
    
    # 1. 极短音频 (50采样点)
    t1 = np.linspace(0, 50/16000, 50, False)
    short_audio = np.sin(2 * np.pi * 440 * t1)
    short_pcm = (short_audio * 32767 * 0.3).astype(np.int16)
    
    # 2. 低音量音频
    t2 = np.linspace(0, 1, sample_rate, False)
    low_volume = np.sin(2 * np.pi * 440 * t2) * 0.001  # 极低音量
    low_pcm = (low_volume * 32767).astype(np.int16)
    
    # 3. 正常音频
    t3 = np.linspace(0, 1, sample_rate, False)
    normal_audio = np.sin(2 * np.pi * 440 * t3)
    normal_pcm = (normal_audio * 32767 * 0.3).astype(np.int16)
    
    # 分析各样本
    analyze_audio_chunk(short_pcm.tobytes(), "极短音频 (50采样点)")
    analyze_audio_chunk(low_pcm.tobytes(), "低音量音频")
    analyze_audio_chunk(normal_pcm.tobytes(), "正常音频")

def main():
    print("音频质量诊断工具")
    print("=" * 50)
    
    # 生成并分析测试样本
    generate_test_samples()
    
    print("\n=== 建议 ===")
    print("1. 确保录音时长大于10ms (160采样点)")
    print("2. 检查麦克风音量设置")
    print("3. 确保环境相对安静")
    print("4. 说话时保持适当距离麦克风")

if __name__ == "__main__":
    main()