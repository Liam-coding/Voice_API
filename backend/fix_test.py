#!/usr/bin/env python3
"""
修复验证测试脚本
专门测试 'ClientConnection' object has no attribute 'open' 问题
"""

import asyncio
import websockets
import traceback
from config.api_config import MAKAWAI_WS_URL, MAKAWAI_API_KEY

async def test_websocket_attributes():
    """测试WebSocket对象的属性"""
    print("=== WebSocket属性测试 ===")
    
    try:
        # 构建WebSocket URL
        url = f"{MAKAWAI_WS_URL}?source_lang=zh&target_lang=en"
        headers = {"Authorization": f"Bearer {MAKAWAI_API_KEY}"}
        
        print(f"连接URL: {url}")
        
        # 建立连接
        ws = await websockets.connect(url, additional_headers=headers)
        print("✓ WebSocket连接建立成功")
        
        # 检查对象类型和属性
        print(f"WebSocket对象类型: {type(ws)}")
        print(f"WebSocket对象属性: {dir(ws)}")
        
        # 测试各种属性检查方法
        print(f"hasattr(ws, 'open'): {hasattr(ws, 'open')}")
        if hasattr(ws, 'open'):
            print(f"ws.open 值: {ws.open}")
        
        print(f"hasattr(ws, 'closed'): {hasattr(ws, 'closed')}")
        if hasattr(ws, 'closed'):
            print(f"ws.closed 值: {ws.closed}")
            
        # 尝试发送测试数据
        test_data = b'\x00' * 1024
        try:
            await ws.send(test_data)
            print("✓ 测试数据发送成功")
        except Exception as e:
            print(f"✗ 数据发送失败: {e}")
            
        # 尝试接收响应
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"✓ 收到响应: {response[:100]}...")  # 只显示前100个字符
        except asyncio.TimeoutError:
            print("⚠ 等待响应超时")
        except Exception as e:
            print(f"✗ 接收响应失败: {e}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
    finally:
        if 'ws' in locals():
            await ws.close()
            print("✓ WebSocket连接已关闭")

async def test_connection_state_detection():
    """测试连接状态检测方法"""
    print("\n=== 连接状态检测测试 ===")
    
    # 模拟不同的连接状态
    class MockWebSocket:
        def __init__(self, is_open=True):
            self.open = is_open
            self.closed = not is_open
            
        async def send(self, data):
            if self.open:
                print("Mock: 数据发送成功")
            else:
                raise Exception("连接已关闭")
                
        async def recv(self):
            if self.open:
                return '{"translated_text": "测试", "status": "success"}'
            else:
                raise Exception("连接已关闭")
                
        async def close(self):
            self.open = False
            self.closed = True
            
        async def ping(self):
            if self.open:
                return True
            else:
                raise Exception("连接已关闭")
    
    # 测试开放连接
    print("测试开放连接:")
    open_ws = MockWebSocket(is_open=True)
    print(f"  hasattr(open_ws, 'open'): {hasattr(open_ws, 'open')}")
    print(f"  open_ws.open: {open_ws.open}")
    
    # 测试关闭连接
    print("测试关闭连接:")
    closed_ws = MockWebSocket(is_open=False)
    print(f"  hasattr(closed_ws, 'open'): {hasattr(closed_ws, 'open')}")
    print(f"  closed_ws.open: {closed_ws.open}")
    
    # 测试无open属性的对象
    print("测试无open属性对象:")
    class NoOpenAttr:
        async def send(self, data):
            pass
        async def recv(self):
            pass
        async def close(self):
            pass
        async def ping(self):
            pass
    
    no_attr_obj = NoOpenAttr()
    print(f"  hasattr(no_attr_obj, 'open'): {hasattr(no_attr_obj, 'open')}")
    print(f"  hasattr(no_attr_obj, 'ping'): {hasattr(no_attr_obj, 'ping')}")

async def main():
    print("开始修复验证测试...\n")
    
    # 测试连接状态检测
    await test_connection_state_detection()
    
    # 测试实际WebSocket连接
    await test_websocket_attributes()
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())