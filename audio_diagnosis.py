#!/usr/bin/env python3
"""
音频质量诊断工具
帮助分析为什么翻译结果为空
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.audio.converter import convert_to_makawai_format, generate_test_audio
import numpy as np
import json

def diagnose_empty_translation():
    """诊断空翻译问题"""
    print("🔍 音频质量诊断开始")
    print("=" * 50)
    
    # 1. 测试生成的标准音频
    print("\n1. 测试标准测试音频:")
    test_audio = generate_test_audio()
    print(f"   生成音频大小: {len(test_audio)} 字节")
    
    # 模拟后端处理
    processed_audio = convert_to_makawai_format(test_audio)
    print(f"   处理后音频大小: {len(processed_audio)} 字节")
    
    if len(processed_audio) > 0:
        print("   ✅ 标准音频处理正常")
    else:
        print("   ❌ 标准音频处理失败")
    
    # 2. 测试不同类型的音频数据
    print("\n2. 测试不同类型音频:")
    
    test_cases = [
        ("静音数据", np.zeros(1000, dtype=np.int16).tobytes()),
        ("低音量数据", (np.sin(np.linspace(0, 4*np.pi, 1000)) * 1000).astype(np.int16).tobytes()),
        ("正常音量数据", (np.sin(np.linspace(0, 4*np.pi, 1000)) * 16000).astype(np.int16).tobytes()),
        ("随机数据", np.random.randint(-1000, 1000, 1000, dtype=np.int16).tobytes())
    ]
    
    for name, audio_data in test_cases:
        print(f"\n   测试: {name}")
        print(f"   原始大小: {len(audio_data)} 字节")
        
        result = convert_to_makawai_format(audio_data)
        print(f"   处理后大小: {len(result)} 字节")
        print(f"   处理结果: {'成功' if len(result) > 0 else '失败'}")
    
    # 3. 分析可能的原因
    print("\n" + "=" * 50)
    print("📋 空翻译可能原因分析:")
    print("=" * 50)
    
    print("1. 🎤 录音质量问题:")
    print("   • 说话声音太小")
    print("   • 环境噪音过大")
    print("   • 麦克风距离太远")
    print("   • 发音不清晰")
    
    print("\n2. ⏱️ 时间因素:")
    print("   • 录音时间太短")
    print("   • 有效语音内容太少")
    print("   • 停顿时间过长")
    
    print("\n3. 🎵 音频特征:")
    print("   • 音调不在识别范围内")
    print("   • 语速过快或过慢")
    print("   • 方言或口音问题")
    
    print("\n4. 🤖 AI模型限制:")
    print("   • 语言模型训练数据限制")
    print("   • 特定词汇识别困难")
    print("   • 背景音乐干扰")

def create_troubleshooting_guide():
    """创建故障排除指南"""
    print("\n" + "=" * 50)
    print("🔧 故障排除步骤:")
    print("=" * 50)
    
    troubleshooting_steps = [
        "1. 🗣️ 改善录音条件:",
        "   • 对着麦克风清晰大声说话",
        "   • 选择安静的环境",
        "   • 靠近麦克风但不要贴太近",
        "   • 说普通话，语速适中",
        
        "\n2. ⏰ 调整录音时间:",
        "   • 每次录音至少2-3秒",
        "   • 连续说话不要停顿太久",
        "   • 说完一句话再停止",
        
        "\n3. 🎛️ 技术调整:",
        "   • 检查浏览器麦克风权限",
        "   • 尝试不同的浏览器",
        "   • 关闭其他音频应用",
        "   • 重启应用和浏览器",
        
        "\n4. 🧪 测试验证:",
        "   • 先测试简单词汇如'你好'",
        "   • 逐渐增加句子复杂度",
        "   • 观察哪些内容能被识别",
        "   • 记录成功和失败的模式"
    ]
    
    for step in troubleshooting_steps:
        print(step)

def generate_recommendation():
    """生成具体建议"""
    print("\n" + "=" * 50)
    print("💡 具体建议:")
    print("=" * 50)
    
    recommendations = [
        "✅ 立即尝试: 对着麦克风清晰地说'你好世界'",
        "✅ 录音技巧: 保持10-20厘米距离，语速稍慢",
        "✅ 环境要求: 选择相对安静的房间",
        "✅ 测试顺序: 从简单词汇开始，逐步增加复杂度",
        "✅ 耐心等待: 给AI一些时间处理和学习你的语音特征"
    ]
    
    for rec in recommendations:
        print(rec)
    
    print("\n🎯 如果仍然无法识别:")
    print("   • 可能是Makawai服务的语言模型限制")
    print("   • 建议联系服务提供商了解支持的语言和发音要求")
    print("   • 考虑使用其他语音识别服务作为备选方案")

if __name__ == "__main__":
    try:
        diagnose_empty_translation()
        create_troubleshooting_guide()
        generate_recommendation()
        
        print("\n" + "=" * 50)
        print("🚀 下一步行动:")
        print("=" * 50)
        print("1. 按照上述建议改善录音条件")
        print("2. 重新测试简单词汇的识别")
        print("3. 观察是否有改善")
        print("4. 如问题持续，考虑联系技术支持")
        
    except Exception as e:
        print(f"\n💥 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()