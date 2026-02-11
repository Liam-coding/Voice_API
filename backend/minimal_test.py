#!/usr/bin/env python3
"""
最小化测试脚本 - 不依赖外部库
用于快速验证基本功能
"""

import asyncio
import json
import base64
import websockets
import traceback
from config.api_config import MAKAWAI_WS_URL, MAKAWAI_API_KEY

async def test_minimal_connection():
    """最小化连接测试"""
    print("=== 最小化连接测试 ===")
    
    try:
        # 构建WebSocket URL
        url = f"{MAKAWAI_WS_URL}?source_lang=zh&target_lang=en"
        headers = {"Authorization": f"Bearer {MAKAWAI_API_KEY}"}
        
        print(f"连接URL: {url}")
        
        # 建立连接
        ws = await websockets.connect(url, additional_headers=headers)
        print("✓ WebSocket连接建立成功")
        
        # 发送测试音频数据（简单的PCM数据）
        test_pcm = b'\x00' * 1024  # 1024字节的静音PCM数据
        await ws.send(test_pcm)
        print("✓ 测试音频数据发送成功")
        
        # 等待响应
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            print(f"✓ 收到响应: {response}")
            
            # 尝试解析JSON
            try:
                result = json.loads(response)
                print(f"✓ JSON解析成功: {result}")
            except json.JSONDecodeError:
                print("⚠ 响应不是有效的JSON格式")
                
        except asyncio.TimeoutError:
            print("⚠ 等待响应超时")
            
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
    finally:
        if 'ws' in locals():
            await ws.close()
            print("✓ WebSocket连接已关闭")

async def main():
    print("开始最小化测试...\n")
    await test_minimal_connection()
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())