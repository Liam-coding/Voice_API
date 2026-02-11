#!/usr/bin/env python3
"""
音频格式详细诊断工具
分析前端发送的音频数据格式
"""

import sys
import os
import numpy as np
import struct

def analyze_audio_data(audio_bytes):
    """详细分析音频数据"""
    print(f"=== 音频数据分析 ===")
    print(f"数据大小: {len(audio_bytes)} 字节")
    print(f"前32字节十六进制: {audio_bytes[:32].hex()}")
    
    # 检查文件头特征
    if len(audio_bytes) > 4:
        header = audio_bytes[:4]
        print(f"文件头: {header}")
        
        # 识别可能的格式
        if header.startswith(b'\x1a\x45\xdf\xa3'):  # WebM
            print("🔍 检测到: WebM格式")
        elif header.startswith(b'OggS'):  # Ogg
            print("🔍 检测到: Ogg格式")
        elif header.startswith(b'\x00\x00\x00\x18'):  # MP4
            print("🔍 检测到: MP4格式")
        elif header.startswith(b'RIFF'):  # WAV
            print("🔍 检测到: WAV格式")
        elif header.startswith(b'fLaC'):  # FLAC
            print("🔍 检测到: FLAC格式")
        else:
            print("🔍 未知格式，尝试PCM分析")
    
    # 尝试PCM分析
    print(f"\n=== PCM分析 ===")
    
    # 16-bit Little Endian PCM分析
    if len(audio_bytes) >= 2:
        try:
            samples_16bit = np.frombuffer(audio_bytes[:min(3200, len(audio_bytes))], dtype=np.int16)
            print(f"16-bit样本数: {len(samples_16bit)}")
            if len(samples_16bit) > 0:
                max_val = np.max(np.abs(samples_16bit))
                print(f"16-bit最大值: {max_val}")
                print(f"16-bit范围: [{np.min(samples_16bit)}, {np.max(samples_16bit)}]")
        except Exception as e:
            print(f"16-bit分析失败: {e}")
    
    # 32-bit Float PCM分析
    if len(audio_bytes) >= 4:
        try:
            samples_32bit = np.frombuffer(audio_bytes[:min(6400, len(audio_bytes))], dtype=np.float32)
            print(f"32-bit浮点样本数: {len(samples_32bit)}")
            if len(samples_32bit) > 0:
                max_val = np.max(np.abs(samples_32bit))
                print(f"32-bit浮点最大值: {max_val:.6f}")
                print(f"32-bit浮点范围: [{np.min(samples_32bit):.6f}, {np.max(samples_32bit):.6f}]")
        except Exception as e:
            print(f"32-bit分析失败: {e}")
    
    # 8-bit PCM分析
    try:
        samples_8bit = np.frombuffer(audio_bytes[:min(1600, len(audio_bytes))], dtype=np.uint8)
        print(f"8-bit样本数: {len(samples_8bit)}")
        if len(samples_8bit) > 0:
            print(f"8-bit范围: [{np.min(samples_8bit)}, {np.max(samples_8bit)}]")
    except Exception as e:
        print(f"8-bit分析失败: {e}")

def create_test_audio_files():
    """创建各种测试音频文件"""
    print(f"\n=== 创建测试音频 ===")
    
    sample_rate = 16000
    duration = 0.5  # 0.5秒
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 生成测试信号
    signal = np.sin(2 * np.pi * 440 * t) * 0.3
    
    # 1. 16-bit PCM
    pcm_16bit = (signal * 32767).astype(np.int16)
    with open('/tmp/test_16bit.pcm', 'wb') as f:
        f.write(pcm_16bit.tobytes())
    print(f"创建16-bit PCM文件: /tmp/test_16bit.pcm ({len(pcm_16bit)*2}字节)")
    
    # 2. 32-bit Float
    with open('/tmp/test_32bit.raw', 'wb') as f:
        f.write(signal.astype(np.float32).tobytes())
    print(f"创建32-bit Float文件: /tmp/test_32bit.raw ({len(signal)*4}字节)")
    
    # 3. 8-bit PCM
    pcm_8bit = ((signal * 127) + 128).astype(np.uint8)
    with open('/tmp/test_8bit.raw', 'wb') as f:
        f.write(pcm_8bit.tobytes())
    print(f"创建8-bit PCM文件: /tmp/test_8bit.raw ({len(pcm_8bit)}字节)")

def main():
    print("音频格式诊断工具")
    print("=" * 50)
    
    # 如果提供了文件参数，分析该文件
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            print(f"分析文件: {file_path}")
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            analyze_audio_data(audio_data)
        else:
            print(f"文件不存在: {file_path}")
    else:
        print("使用方法: python3 audio_format_diagnosis.py <音频文件路径>")
        print("或运行测试音频生成...")
        create_test_audio_files()
    
    print("\n=== 建议 ===")
    print("1. 检查前端实际发送的音频格式")
    print("2. 确认浏览器支持的MediaRecorder格式")
    print("3. 考虑使用WAV格式作为最兼容的选择")

if __name__ == "__main__":
    main()