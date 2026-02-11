<template>
  <div class="recorder-wrapper">
    <div class="status-indicator" :class="{ active: isRecording }">
      <span class="dot"></span>
      {{ isRecording ? '正在实时转译...' : '准备就绪' }}
    </div>
    <button 
      @click="handleButtonClick" 
      :class="{ 'btn-recording': isRecording }" 
      class="main-btn"
      id="record-button"
    >
      <div class="icon">{{ isRecording ? '⏹' : '🎤' }}</div>
      {{ isRecording ? '停止录音' : '开始实时语音翻译' }}
    </button>
    
    <!-- 调试信息 -->
    <div v-if="debugMode" class="debug-info">
      <p>点击次数: {{ clickCount }}</p>
      <p>录音状态: {{ isRecording ? '录音中' : '未录音' }}</p>
      <p>最后点击: {{ lastClickTime }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { useTranslationStore } from '../stores/translation'

// 配置axios基础URL
const API_BASE_URL = 'http://127.0.0.1:8000'  // 正常服务
// const API_BASE_URL = 'http://127.0.0.1:8001'  // 调试捕获服务

const store = useTranslationStore()
const isRecording = ref(false)
const clickCount = ref(0)
const lastClickTime = ref('')
const debugMode = ref(true) // 开启调试模式
let mediaRecorder = null
let chunkTimer = null

// 新的按钮处理函数
const handleButtonClick = () => {
  console.log('🖱️ 按钮被点击了!')
  console.trace('按钮点击调用栈')
  
  clickCount.value++
  lastClickTime.value = new Date().toLocaleTimeString()
  
  // 强制触发状态更新
  nextTick(() => {
    if (isRecording.value) {
      stop()
    } else {
      start()
    }
  })
}

const toggleRecording = () => {
  console.log('🔄 toggleRecording被调用')
  isRecording.value ? stop() : start()
}

const start = async () => {
  console.log('🎙️ 开始录音...')
  console.log('📢 录音函数被调用，准备获取麦克风权限')
  
  try {
    console.log('🔍 请求麦克风访问权限...')
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
        channelCount: 1
      } 
    })
    console.log('✅ 麦克风权限获取成功')
    console.log('🔧 初始化MediaRecorder...')
    
    // 尝试多种音频格式以提高兼容性
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg',
      'audio/mp4'
    ]
    
    let selectedMimeType = ''
    for (const mimeType of mimeTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        selectedMimeType = mimeType
        break
      }
    }
    
    if (!selectedMimeType) {
      console.warn('⚠️ 没有找到支持的音频格式，使用默认配置')
      selectedMimeType = 'audio/webm'
    }
    
    const constraints = {
      mimeType: selectedMimeType,
      audioBitsPerSecond: 128000
    }
    
    mediaRecorder = new MediaRecorder(stream, constraints)
    console.log('✅ MediaRecorder初始化成功')
    console.log('   格式:', selectedMimeType)
    console.log('   比特率:', constraints.audioBitsPerSecond)

    mediaRecorder.ondataavailable = async (event) => {
      console.log('🔊 MediaRecorder收到音频数据:', event.data.size, '字节')
      
      // 优化数据块大小阈值，确保足够的音频数据
      if (event.data.size > 100) {  // 降低阈值但保持合理性
        const formData = new FormData()
        formData.append('audio_chunk', new Blob([event.data], { type: 'audio/webm' }))
        
        console.log('📤 发送音频数据到后端:', {
          size: event.data.size,
          type: 'audio/webm',
          url: `${API_BASE_URL}/api/translate`
        })
        
        try {
          // 改用fetch API，与调试页面保持一致
          const response = await fetch(`${API_BASE_URL}/api/translate`, {
            method: 'POST',
            body: formData,
            timeout: 10000
          })
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }
          
          const res = {
            status: response.status,
            data: await response.json()
          }
          
          console.log('📥 收到后端响应:', {
            status: res.status,
            data: res.data
          })
          
          if (res.data.translation) {
            store.addResult(res.data)
            console.log('✅ 翻译结果已添加到显示')
          }
        } catch (err) {
          console.error('❌ 翻译请求失败:', {
            message: err.message,
            status: err.status
          })
          
          // 显示用户友好的错误信息
          let errorMsg = '翻译服务暂时不可用'
          if (err.name === 'AbortError' || err.message.includes('timeout')) {
            errorMsg = '请求超时，请检查网络连接'
          } else if (err.message.includes('400')) {
            errorMsg = '音频数据格式不正确'
          } else if (err.message.includes('500')) {
            errorMsg = '服务器内部错误'
          }
          
          console.warn("分片翻译跳过:", errorMsg)
        }
      } else {
        console.log('⏭️ 跳过小数据块:', event.data.size, '字节')
      }
    }

    // 优化录制间隔以平衡延迟和数据质量
    mediaRecorder.start(1500)  // 1.5秒间隔，提供更好的数据块大小
    isRecording.value = true
    console.log('✅ 录音已开始，状态已更新')
  } catch (err) {
    console.error('❌ 录音启动失败:', err)
    alert('请允许麦克风权限\n错误信息: ' + err.message)
  }
}

const stop = () => {
  console.log('⏹️ 停止录音...')
  if (chunkTimer) {
    clearInterval(chunkTimer)
  }
  if (mediaRecorder) {
    mediaRecorder.stop()
    if (mediaRecorder.stream) {
      mediaRecorder.stream.getTracks().forEach(track => track.stop())
    }
  }
  isRecording.value = false
  store.saveToHistory()
  console.log('✅ 录音已停止')
}
onUnmounted(stop)
</script>