#!/usr/bin/env python3
"""
改进后的后端测试脚本
测试并发处理、错误恢复和连接管理功能
"""

import asyncio
import aiohttp
import time
import traceback

async def test_single_request(session, audio_data, request_id=1):
    """测试单个请求"""
    try:
        print(f"\n=== 测试请求 #{request_id} ===")
        start_time = time.time()
        
        form_data = aiohttp.FormData()
        form_data.add_field('audio_chunk', audio_data, filename='test.wav', content_type='audio/wav')
        form_data.add_field('source_lang', 'zh')
        form_data.add_field('target_lang', 'en')
        
        async with session.post('http://localhost:8000/api/translate', data=form_data) as response:
            response_time = time.time() - start_time
            print(f"请求 #{request_id} 响应时间: {response_time:.2f}秒")
            
            if response.status == 200:
                result = await response.json()
                print(f"✅ 请求 #{request_id} 成功:")
                print(f"   状态: {result.get('status')}")
                print(f"   翻译: {result.get('translation')}")
                print(f"   原文: {result.get('original')}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ 请求 #{request_id} 失败 (状态码: {response.status}):")
                print(f"   错误信息: {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ 请求 #{request_id} 异常: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

async def test_concurrent_requests(num_requests=3):
    """测试并发请求处理"""
    print(f"\n🚀 开始并发测试 ({num_requests}个并发请求)")
    
    # 创建测试音频数据（模拟不同的音频）
    test_audios = []
    for i in range(num_requests):
        # 创建不同长度的PCM数据来模拟不同音频
        audio_size = 1000 + (i * 200)  # 不同大小的音频数据
        audio_data = bytes([i % 256] * audio_size)  # 简单的测试数据
        test_audios.append(audio_data)
    
    async with aiohttp.ClientSession() as session:
        # 并发执行所有请求
        tasks = [
            test_single_request(session, audio_data, i+1) 
            for i, audio_data in enumerate(test_audios)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        print(f"\n📊 并发测试结果:")
        print(f"   总请求数: {num_requests}")
        print(f"   成功数: {successful}")
        print(f"   失败数: {failed}")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均响应时间: {total_time/num_requests:.2f}秒")
        
        return successful == num_requests

async def test_sequential_requests(num_requests=5):
    """测试顺序请求处理"""
    print(f"\n🔄 开始顺序测试 ({num_requests}个连续请求)")
    
    # 创建测试音频数据
    audio_data = b'\x00' * 1000  # 固定大小的测试数据
    
    async with aiohttp.ClientSession() as session:
        successful = 0
        start_time = time.time()
        
        for i in range(num_requests):
            if await test_single_request(session, audio_data, i+1):
                successful += 1
            # 短暂延迟避免过于频繁的请求
            await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        print(f"\n📊 顺序测试结果:")
        print(f"   总请求数: {num_requests}")
        print(f"   成功数: {successful}")
        print(f"   失败数: {num_requests - successful}")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均响应时间: {total_time/num_requests:.2f}秒")
        
        return successful == num_requests

async def test_health_check():
    """测试健康检查接口"""
    print("\n🏥 测试健康检查接口")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 健康检查成功:")
                    print(f"   系统状态: {result.get('status')}")
                    print(f"   Makawai连接: {result.get('makawai_connected')}")
                    return True
                else:
                    print(f"❌ 健康检查失败 (状态码: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🧪 开始改进后的后端测试")
    print("=" * 50)
    
    # 首先测试健康检查
    if not await test_health_check():
        print("❌ 健康检查失败，退出测试")
        return
    
    # 测试顺序请求
    sequential_success = await test_sequential_requests(3)
    
    # 测试并发请求
    concurrent_success = await test_concurrent_requests(3)
    
    # 最终结果
    print("\n" + "=" * 50)
    print("🏁 测试总结:")
    print(f"   顺序请求测试: {'✅ 通过' if sequential_success else '❌ 失败'}")
    print(f"   并发请求测试: {'✅ 通过' if concurrent_success else '❌ 失败'}")
    
    if sequential_success and concurrent_success:
        print("🎉 所有测试通过！后端改进成功！")
    else:
        print("⚠️  部分测试失败，请检查后端日志")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {str(e)}")
        print(traceback.format_exc())