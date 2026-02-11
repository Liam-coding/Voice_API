#!/usr/bin/env python3
"""
快速测试脚本 - 验证time模块导入问题是否已修复
"""

import asyncio
import aiohttp

async def quick_test():
    """快速测试单个请求"""
    print("🚀 开始快速测试...")
    
    # 创建简单的测试音频数据
    test_audio = b'\x00' * 1000  # 1000字节的静音PCM数据
    
    try:
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field('audio_chunk', test_audio, filename='test.wav', content_type='audio/wav')
            form_data.add_field('source_lang', 'zh')
            form_data.add_field('target_lang', 'en')
            
            print("📤 发送测试请求...")
            async with session.post('http://localhost:8000/api/translate', data=form_data) as response:
                print(f"📥 收到响应，状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 请求成功!")
                    print(f"   状态: {result.get('status')}")
                    print(f"   翻译: {result.get('translation')}")
                    print(f"   原文: {result.get('original')}")
                else:
                    error_text = await response.text()
                    print(f"❌ 请求失败:")
                    print(f"   状态码: {response.status}")
                    print(f"   错误信息: {error_text}")
                    
    except Exception as e:
        print(f"💥 测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    asyncio.run(quick_test())