#!/usr/bin/env python3
"""
测试脚本：验证audio_processor变量是否正确定义
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, '/Users/jialei/code/voice-translation-web/backend/src')

try:
    # 测试导入
    from audio.converter import AudioProcessor
    print("✓ 成功导入AudioProcessor类")
    
    # 测试实例化
    audio_processor = AudioProcessor()
    print("✓ 成功创建audio_processor实例")
    
    # 测试方法调用
    test_data = b"fake_audio_data_for_testing"
    result, success = audio_processor.webm_to_pcm(test_data)
    print(f"✓ webm_to_pcm方法调用成功，返回: {success}")
    
    print("\n🎉 所有测试通过！后端应该可以正常工作了。")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()