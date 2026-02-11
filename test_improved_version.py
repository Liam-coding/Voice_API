#!/usr/bin/env python3
"""
改进版语音翻译服务测试脚本
"""

import asyncio
import sys
import os
import requests
import json

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_health_check():
    """测试健康检查接口"""
    print("🏥 测试健康检查接口...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 健康检查异常: {e}")
        return False

def test_service_status():
    """测试服务状态接口"""
    print("📊 测试服务状态接口...")
    
    try:
        response = requests.get('http://localhost:8000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态正常: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 服务状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 服务状态检查异常: {e}")
        return False

def test_audio_processing():
    """测试音频处理功能"""
    print("🎵 测试音频处理功能...")
    
    # 生成测试音频数据
    import numpy as np
    
    # 生成1秒的440Hz正弦波
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_signal = np.sin(2 * np.pi * 440 * t)
    pcm_data = (audio_signal * 32767 * 0.3).astype(np.int16)
    
    # 保存为临时文件
    temp_file = '/tmp/test_audio.pcm'
    with open(temp_file, 'wb') as f:
        f.write(pcm_data.tobytes())
    
    try:
        # 准备表单数据
        with open(temp_file, 'rb') as f:
            files = {'audio_chunk': ('test.pcm', f, 'audio/pcm')}
            data = {
                'source_lang': 'zh',
                'target_lang': 'en'
            }
            
            response = requests.post(
                'http://localhost:8000/api/translate',
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 音频处理成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"❌ 音频处理失败: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"💥 音频处理异常: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def test_websocket_connection():
    """测试WebSocket连接"""
    print("🔌 测试WebSocket连接...")
    
    try:
        from src.adapter.improved_makawai_adapter import ImprovedMakawaiClient
        
        client = ImprovedMakawaiClient()
        
        # 测试连接
        if await client.connect(source_lang="zh", target_lang="en"):
            print("✅ WebSocket连接成功")
            
            # 测试发送简单数据
            test_data = b'\x00' * 100
            await client.send_audio(test_data)
            print("✅ 音频数据发送成功")
            
            # 测试接收（可能会超时，这是正常的）
            try:
                result = await asyncio.wait_for(client.receive_result(), timeout=5.0)
                print(f"✅ 接收测试结果: {result}")
            except asyncio.TimeoutError:
                print("⚠️ 接收超时（正常现象）")
            
            await client.close()
            print("✅ WebSocket测试完成")
            return True
        else:
            print("❌ WebSocket连接失败")
            return False
            
    except Exception as e:
        print(f"💥 WebSocket测试异常: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def run_comprehensive_tests():
    """运行综合测试"""
    print("🎯 开始综合测试...\n")
    
    tests = [
        ("健康检查", test_health_check),
        ("服务状态", test_service_status),
        ("音频处理", test_audio_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"正在运行: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 异步测试
    print(f"\n{'='*50}")
    print("正在运行: WebSocket连接测试")
    print('='*50)
    
    try:
        result = asyncio.run(test_websocket_connection())
        results.append(("WebSocket连接", result))
    except Exception as e:
        print(f"❌ WebSocket测试异常: {e}")
        results.append(("WebSocket连接", False))
    
    # 输出测试总结
    print(f"\n{'='*50}")
    print("📊 测试结果总结")
    print('='*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)