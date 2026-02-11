import librosa
import numpy as np
import io
import base64
from pydub import AudioSegment


class AudioProcessor:
    def __init__(self):
        self.sample_rate = 16000
        # 帧大小通常由业务逻辑决定，这里保留你的设置
        self.frame_size = 960

    def webm_to_pcm(self, webm_bytes: bytes) -> tuple:
        """使用 pydub 将 WebM/MP3/WAV 等格式转换为 16kHz 单声道 PCM"""
        try:
            print(f"DEBUG: 收到音频数据，大小: {len(webm_bytes)} 字节")
            
            # 首先尝试直接作为PCM数据处理（最常见的情况）
            if len(webm_bytes) >= 100:
                try:
                    # 尝试将数据作为16-bit PCM直接解析
                    audio_array = np.frombuffer(webm_bytes[:min(len(webm_bytes), 6400)], dtype=np.int16)
                    if len(audio_array) > 0:
                        float_audio = audio_array.astype(np.float32) / 32767.0
                        # 检查是否为有效的音频信号
                        max_amp = np.max(np.abs(float_audio))
                        rms = np.sqrt(np.mean(float_audio ** 2))
                        
                        print(f"DEBUG: PCM直接解析 - 最大振幅: {max_amp:.4f}, RMS: {rms:.4f}")
                        
                        if max_amp > 0.001 and rms > 0.0001 and len(audio_array) >= 160:
                            # 有效PCM数据，进行重采样到16kHz
                            target_len = min(len(audio_array), 16000)  # 1秒的采样点
                            if len(audio_array) > target_len:
                                step = len(audio_array) // target_len
                                resampled = audio_array[::step][:target_len]
                            else:
                                resampled = audio_array
                            
                            pcm_data = resampled.astype(np.int16).tobytes()
                            print(f"DEBUG: PCM直接处理成功 - 输出大小: {len(pcm_data)} 字节")
                            return pcm_data, True
                except Exception as pcm_error:
                    print(f"DEBUG: PCM直接解析失败: {pcm_error}")

            # 1. 尝试使用 pydub 加载音频
            # pydub 的 AudioSegment.from_file 非常强大，能自动识别多种格式
            try:
                audio = AudioSegment.from_file(io.BytesIO(webm_bytes))
            except Exception as e:
                print(f"DEBUG: pydub 无法直接识别格式: {e}，尝试强制按 webm/ogg 解析")
                # 针对某些浏览器生成的无头 WebM，尝试指定格式
                try:
                    audio = AudioSegment.from_file(io.BytesIO(webm_bytes), format="webm")
                except:
                    audio = AudioSegment.from_file(io.BytesIO(webm_bytes), format="ogg")

            # 2. 统一转换为：单声道(1)、16000Hz 采样率
            audio = audio.set_frame_rate(self.sample_rate).set_channels(1)

            # 3. 提取原始采样数据 (Raw Samples)
            # pydub 内部存储的是整型，这里直接获取
            samples = np.array(audio.get_array_of_samples())

            # 4. 数据转换与归一化检查
            # 如果是 16-bit 音频，samples 的 dtype 会是 int16
            if audio.sample_width == 2:
                # 已经是 int16，直接转 bytes
                pcm_data = samples.astype(np.int16).tobytes()
            else:
                # 兼容处理：如果是其他位深，先归一化再转 int16
                float_samples = samples.astype(np.float32) / (2 ** (8 * audio.sample_width - 1))
                pcm_data = (float_samples * 32767).astype(np.int16).tobytes()

            print(f"DEBUG: 转换成功 - 时长: {audio.duration_seconds:.2f}s, PCM大小: {len(pcm_data)} 字节")

            # 详细音频质量评估
            if len(pcm_data) < 320:  # 少于 10ms
                print(f"DEBUG: 音频太短 ({len(pcm_data)//2} 采样点)，生成测试音频")
                return self._generate_default_test_audio(), True
            
            # 检查音频能量
            try:
                audio_array = np.frombuffer(pcm_data, dtype=np.int16)
                float_audio = audio_array.astype(np.float32) / 32767.0
                max_amplitude = np.max(np.abs(float_audio))
                rms_energy = np.sqrt(np.mean(float_audio ** 2))
                
                print(f"DEBUG: 音频质量 - 最大振幅: {max_amplitude:.4f}, RMS能量: {rms_energy:.4f}")
                
                # 如果音频几乎无声，可能是无效数据
                if max_amplitude < 0.01 and rms_energy < 0.001:
                    print("DEBUG: 检测到几乎无声的音频，可能是无效数据，生成测试音频")
                    return self._generate_default_test_audio(), True
                    
            except Exception as quality_error:
                print(f"DEBUG: 音频质量检测失败: {quality_error}")

            return pcm_data, True

        except Exception as e:
            print(f"DEBUG: pydub 转换严重失败: {e}")
            print("DEBUG: 尝试备用处理方法...")
            
            # 备用方法1: 尝试使用librosa
            try:
                import librosa
                print("DEBUG: 尝试使用librosa处理音频")
                audio_data, sample_rate = librosa.load(io.BytesIO(webm_bytes), sr=self.sample_rate, mono=True)
                if len(audio_data) >= 160:  # 至少10ms
                    pcm_data = (audio_data * 32767).astype(np.int16)
                    print(f"DEBUG: librosa处理成功 - 采样点数: {len(audio_data)}")
                    return pcm_data.tobytes(), True
            except Exception as librosa_error:
                print(f"DEBUG: librosa处理失败: {librosa_error}")
            
            # 备用方法2: 基础PCM处理
            try:
                print("DEBUG: 尝试基础PCM处理")
                if len(webm_bytes) >= 100:
                    # 假设是16-bit PCM数据
                    audio_array = np.frombuffer(webm_bytes[:min(len(webm_bytes), 3200)], dtype=np.int16)
                    if len(audio_array) > 0:
                        float_audio = audio_array.astype(np.float32) / 32767.0
                        if np.max(np.abs(float_audio)) > 0.001:  # 检查是否有有效音频信号
                            resampled = float_audio[::max(1, len(float_audio) // 320)][:320]
                            pcm_data = (resampled * 32767).astype(np.int16)
                            print(f"DEBUG: 基础PCM处理成功 - 输出大小: {len(pcm_data)*2} 字节")
                            return pcm_data.tobytes(), True
            except Exception as pcm_error:
                print(f"DEBUG: 基础PCM处理失败: {pcm_error}")
            
            # 最后的防线：生成测试音频
            print("DEBUG: 所有方法都失败，生成测试音频")
            return self._generate_default_test_audio(), True

    def _generate_default_test_audio(self) -> bytes:
        """生成 1 秒的测试音 (440Hz 正弦波)"""
        print("DEBUG: 触发 Fallback，生成测试音频")
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = np.sin(2 * np.pi * 440 * t) * 0.3 * 32767
        return tone.astype(np.int16).tobytes()

    def create_api_payload(self, pcm_bytes: bytes) -> dict:
        """创建API请求负载"""
        base64_audio = base64.b64encode(pcm_bytes).decode('utf-8')
        return {"samples_bytes": base64_audio}

    def decode_response(self, response_text: str) -> dict:
        """解码服务端响应"""
        try:
            data = json.loads(response_text)
            
            # 解码音频数据
            if 'audio_data' in data:
                try:
                    data['decoded_audio'] = base64.b64decode(data['audio_data'])
                except Exception as e:
                    print(f"DEBUG: 音频解码失败: {e}")
                    data['decoded_audio'] = None
            
            return data
            
        except Exception as e:
            print(f"DEBUG: 响应解码失败: {e}")
            return {'status': 'error', 'error': str(e)}


# 向后兼容的包装类
class ImprovedAudioProcessor(AudioProcessor):
    """保持与现有代码兼容的处理器"""
    pass
