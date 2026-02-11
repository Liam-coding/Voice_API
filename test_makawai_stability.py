#!/usr/bin/env python3
"""
Makawai连接稳定性测试脚本
专门测试长时间等待响应的情况
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.adapter.makawaiAdapter import MakawaiClient
import numpy as np

async def test_long_wait_scenario():
    """测试长时间等待场景"""
    print("⏱️ 开始Makawai长时间等待测试")
    print("=" * 50)
    
    client = MakawaiClient()
    
    try:
        # 1. 建立连接
        print("1. 建立WebSocket连接...")
        await client.connect(source_lang="zh", target_lang="en")
        print("✅ 连接建立成功")
        
        # 2. 生成测试音频数据
        print("\n2. 生成测试音频数据...")
        # 生成1秒的标准测试音频
        sample_rate = 16000
        duration = 1.0
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_signal = np.sin(2 * np.pi * frequency * t)
        pcm_data = (audio_signal * 32767 * 0.3).astype(np.int16)
        audio_bytes = pcm_data.tobytes()
        
        print(f"   音频数据大小: {len(audio_bytes)} 字节")
        
        # 3. 发送音频数据
        print("\n3. 发送音频到Makawai...")
        await client.send_audio(audio_bytes)
        print("✅ 音频发送成功")
        
        # 4. 等待响应（测试长时间等待）
        print("\n4. 等待Makawai响应...")
        print("   观察连接是否会提前关闭")
        print("   超时设置: 30秒")
        
        result = await client.receive_result()
        print(f"\n📥 收到结果: {result}")
        
        # 5. 分析结果
        status = result.get("status", "unknown")
        if status == "closed":
            print("⚠️  连接在等待期间被关闭")
            print("   可能原因:")
            print("   - Makawai服务处理完成后主动关闭连接")
            print("   - 服务端超时设置较短")
            print("   - 音频内容无法识别导致提前终止")
        elif status == "timeout":
            print("⏰ 等待超时")
            print("   建议进一步增加超时时间")
        elif status == "success":
            print("🎉 成功收到响应")
            if result.get("translation"):
                print(f"   翻译结果: {result['translation']}")
            else:
                print("   但翻译结果为空")
        else:
            print(f"❓ 其他状态: {status}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
    
    finally:
        # 6. 清理连接
        print("\n6. 清理连接...")
        await client.close()
        print("✅ 测试完成")

async def test_multiple_scenarios():
    """测试多种场景"""
    print("\n" + "=" * 50)
    print("🔄 测试多种等待场景")
    
    scenarios = [
        ("短音频", 0.5),
        ("标准音频", 1.0), 
        ("长音频", 2.0)
    ]
    
    for name, duration in scenarios:
        print(f"\n--- 测试场景: {name} ({duration}秒) ---")
        
        client = MakawaiClient()
        try:
            await client.connect(source_lang="zh", target_lang="en")
            
            # 生成对应时长的音频
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_signal = np.sin(2 * np.pi * 440 * t)  # 440Hz音调
            pcm_data = (audio_signal * 32767 * 0.3).astype(np.int16)
            audio_bytes = pcm_data.tobytes()
            
            print(f"发送 {len(audio_bytes)} 字节音频数据...")
            await client.send_audio(audio_bytes)
            
            print("等待响应...")
            result = await client.receive_result()
            print(f"结果状态: {result.get('status', 'unknown')}")
            
            if result.get("translation"):
                print(f"✅ 翻译成功: {result['translation']}")
            else:
                print("❌ 无翻译结果")
                
        except Exception as e:
            print(f"❌ 场景失败: {e}")
        finally:
            await client.close()

if __name__ == "__main__":
    print("🎙️ Makawai连接稳定性专项测试")
    print("专注于诊断连接提前关闭问题")
    
    try:
        # 运行主要测试
        asyncio.run(test_long_wait_scenario())
        
        # 运行多场景测试
        asyncio.run(test_multiple_scenarios())
        
        print("\n" + "=" * 50)
        print("📋 测试结论:")
        print("=" * 50)
        print("如果连接总是提前关闭:")
        print("1. 可能是Makawai服务端的超时设置问题")
        print("2. 可能是音频内容不符合服务要求")
        print("3. 建议联系Makawai技术支持确认服务配置")
        print("4. 可以尝试调整发送的音频特征")
        
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试框架错误: {e}")