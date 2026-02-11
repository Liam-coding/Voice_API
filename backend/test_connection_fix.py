#!/usr/bin/env python3
"""
测试WebSocket连接修复
"""

import asyncio
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.adapter.makawaiAdapter import MakawaiClient

async def test_basic_connection():
    """测试基本连接功能"""
    print("🔌 测试WebSocket连接...")
    
    client = MakawaiClient()
    
    try:
        # 测试连接
        print("1. 测试初始连接...")
        await client.connect()
        print("✅ 连接成功")
        
        # 测试发送简单数据
        print("2. 测试发送音频数据...")
        test_data = b'\x00' * 100  # 100字节的测试数据
        await client.send_audio(test_data)
        print("✅ 音频发送成功")
        
        # 测试接收响应
        print("3. 测试接收响应...")
        result = await client.receive_result()
        print(f"✅ 接收结果: {result}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
    finally:
        # 清理连接
        await client.close()
        print("🧹 连接已关闭")

async def test_reconnection():
    """测试重连功能"""
    print("\n🔄 测试重连功能...")
    
    client = MakawaiClient()
    
    try:
        # 初始连接
        await client.connect()
        print("✅ 初始连接成功")
        
        # 主动关闭连接
        await client.close()
        print("🔌 主动关闭连接")
        
        # 再次发送数据（应该触发重连）
        test_data = b'\x00' * 50
        await client.send_audio(test_data)
        print("✅ 重连后发送成功")
        
    except Exception as e:
        print(f"❌ 重连测试失败: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    print("🧪 开始WebSocket适配器测试")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_basic_connection())
    asyncio.run(test_reconnection())
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")