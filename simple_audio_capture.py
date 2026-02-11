#!/usr/bin/env python3
"""
简化版音频数据捕获工具
使用内置HTTP服务器捕获前端音频数据
"""

import http.server
import socketserver
import json
import cgi
import os
import binascii
from urllib.parse import urlparse, parse_qs

class AudioCaptureHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/capture/audio':
            self.handle_audio_capture()
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/capture/results':
            self.handle_get_results()
        elif self.path == '/capture/clear':
            self.handle_clear_results()
        elif self.path == '/':
            self.handle_root()
        else:
            self.send_error(404)
    
    def handle_audio_capture(self):
        """处理音频捕获请求"""
        try:
            # 解析multipart数据
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # 获取音频数据
            if 'audio_chunk' in form:
                audio_file = form['audio_chunk']
                audio_data = audio_file.file.read()
                
                # 获取其他参数
                source_lang = form.getvalue('source_lang', 'zh')
                target_lang = form.getvalue('target_lang', 'en')
                
                print(f"\n{'='*60}")
                print(f"📡 接收到音频数据")
                print(f"源语言: {source_lang}, 目标语言: {target_lang}")
                print(f"文件名: {audio_file.filename}")
                print(f"数据大小: {len(audio_data)} 字节")
                
                # 保存原始数据
                filename = f"captured_audio_{int(os.time()) if hasattr(os, 'time') else 0}.bin"
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                print(f"数据已保存到: {filename}")
                
                # 分析格式
                analysis = self.analyze_audio_format(audio_data)
                
                # 准备响应
                response_data = {
                    "status": "captured",
                    "filename": filename,
                    "size": len(audio_data),
                    "analysis": analysis
                }
                
                # 发送响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, indent=2).encode())
                
                # 打印详细分析
                print("格式分析结果:")
                for key, value in analysis.items():
                    print(f"  {key}: {value}")
                    
            else:
                self.send_error(400, "Missing audio_chunk parameter")
                
        except Exception as e:
            print(f"处理错误: {e}")
            self.send_error(500, str(e))
    
    def analyze_audio_format(self, audio_bytes):
        """分析音频格式"""
        result = {
            'file_header': '',
            'hex_header': '',
            'detected_format': 'unknown',
            'possible_formats': [],
            'size_info': {}
        }
        
        # 文件头分析
        if len(audio_bytes) >= 16:
            header = audio_bytes[:16]
            result['file_header'] = str(header)
            result['hex_header'] = binascii.hexlify(header).decode()
            
            # 格式识别
            if header.startswith(b'\x1a\x45\xdf\xa3'):
                result['detected_format'] = 'webm'
                result['possible_formats'].append('WebM')
            elif header.startswith(b'OggS'):
                result['detected_format'] = 'ogg'
                result['possible_formats'].append('Ogg')
            elif header.startswith(b'RIFF'):
                result['detected_format'] = 'wav'
                result['possible_formats'].append('WAV')
            elif header.startswith(b'fLaC'):
                result['detected_format'] = 'flac'
                result['possible_formats'].append('FLAC')
            else:
                result['detected_format'] = 'unknown'
                result['possible_formats'].append('可能是原始数据')
        
        # 大小信息
        result['size_info'] = {
            'total_bytes': len(audio_bytes),
            'can_be_16bit': len(audio_bytes) % 2 == 0,
            'can_be_32bit': len(audio_bytes) % 4 == 0,
            'estimated_16bit_samples': len(audio_bytes) // 2,
            'estimated_32bit_samples': len(audio_bytes) // 4
        }
        
        return result
    
    def handle_get_results(self):
        """返回捕获结果"""
        response = {"message": "音频捕获服务运行中", "endpoint": "/capture/audio"}
        self.send_json_response(response)
    
    def handle_clear_results(self):
        """清空结果"""
        response = {"status": "cleared"}
        self.send_json_response(response)
    
    def handle_root(self):
        """根路径响应"""
        response = {
            "message": "音频数据捕获服务",
            "endpoints": {
                "capture": "/capture/audio (POST)",
                "results": "/capture/results (GET)",
                "clear": "/capture/clear (GET)"
            }
        }
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())

def run_server(port=8001):
    """运行服务器"""
    with socketserver.TCPServer(("", port), AudioCaptureHandler) as httpd:
        print(f"音频数据捕获服务启动在端口 {port}")
        print(f"访问地址: http://localhost:{port}")
        print("请在前端进行录音测试...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")

if __name__ == "__main__":
    run_server()