<template>
  <div style="padding: 20px; text-align: center;">
    <h2>🎙️ 按钮绑定测试</h2>
    
    <!-- 状态显示 -->
    <div style="margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 10px;">
      <div><strong>录音状态:</strong> {{ isRecording ? '🔴 录音中' : '⚪ 未录音' }}</div>
      <div><strong>点击次数:</strong> {{ clickCount }}</div>
      <div><strong>最后点击时间:</strong> {{ lastClickTime || '从未点击' }}</div>
    </div>
    
    <!-- 测试按钮 -->
    <div style="margin: 20px 0;">
      <button 
        @click="handleButtonClick" 
        :style="buttonStyle"
        id="test-button"
      >
        {{ isRecording ? '⏹️ 停止录音' : '▶️ 开始录音' }}
      </button>
    </div>
    
    <!-- 日志显示 -->
    <div style="margin: 20px 0;">
      <h3>📝 点击日志</h3>
      <div 
        id="log-container"
        style="height: 300px; overflow-y: auto; background: #000; color: #0f0; padding: 15px; border-radius: 5px; font-family: monospace; text-align: left;"
      >
        <div v-for="(log, index) in logs" :key="index" style="margin: 5px 0;">
          [{{ log.time }}] {{ log.message }}
        </div>
      </div>
      <button @click="clearLogs" style="margin-top: 10px; padding: 8px 15px;">🗑️ 清空日志</button>
    </div>
    
    <!-- 网络测试 -->
    <div style="margin: 20px 0;">
      <h3>🌐 网络连接测试</h3>
      <button @click="testBackendConnection" style="padding: 10px 20px; margin: 5px;">
        🔗 测试后端连接
      </button>
      <button @click="testDirectAPI" style="padding: 10px 20px; margin: 5px;">
        🎵 测试直接API调用
      </button>
      <div style="margin-top: 10px; padding: 10px; background: #e9ecef; border-radius: 5px;">
        <div><strong>后端状态:</strong> {{ backendStatus }}</div>
        <div><strong>API测试结果:</strong> {{ apiTestResult }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 响应式数据
const isRecording = ref(false)
const clickCount = ref(0)
const lastClickTime = ref('')
const logs = ref([])
const backendStatus = ref('未知')
const apiTestResult = ref('未测试')

// 计算属性 - 按钮样式
const buttonStyle = computed(() => ({
  padding: '15px 30px',
  fontSize: '18px',
  borderRadius: '30px',
  border: 'none',
  cursor: 'pointer',
  backgroundColor: isRecording.value ? '#dc3545' : '#42b983',
  color: 'white',
  transition: 'all 0.3s',
  boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
}))

// 添加日志
const addLog = (message) => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({
    time: timestamp,
    message: message
  })
  
  // 保持最新的50条日志
  if (logs.value.length > 50) {
    logs.value.shift()
  }
  
  // 滚动到底部
  setTimeout(() => {
    const container = document.getElementById('log-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, 10)
  
  // 同时输出到浏览器控制台
  console.log(`[${timestamp}] ${message}`)
}

// 清空日志
const clearLogs = () => {
  logs.value = []
  addLog('日志已清空')
}

// 按钮点击处理
const handleButtonClick = () => {
  clickCount.value++
  lastClickTime.value = new Date().toLocaleTimeString()
  
  addLog(`🖱️ 按钮被点击! (第${clickCount.value}次)`)
  addLog(`当前状态: ${isRecording.value ? '录音中' : '未录音'}`)
  
  // 切换录音状态
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  addLog('🎙️ 开始录音流程...')
  
  try {
    addLog('🔍 请求麦克风权限...')
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    addLog('✅ 麦克风权限获取成功')
    
    addLog('🔧 初始化MediaRecorder...')
    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
    addLog('✅ MediaRecorder初始化成功')
    
    // 设置数据回调
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        addLog(`🔊 收到音频数据: ${event.data.size} 字节`)
        
        // 测试发送到后端
        if (event.data.size > 1000) {
          testSendAudio(event.data)
        }
      }
    }
    
    mediaRecorder.onstop = () => {
      addLog('⏹️ MediaRecorder已停止')
    }
    
    mediaRecorder.onerror = (event) => {
      addLog(`❌ MediaRecorder错误: ${event.error}`)
    }
    
    // 开始录音
    mediaRecorder.start(1000) // 每秒获取一次数据
    isRecording.value = true
    addLog('✅ 录音已开始')
    
    // 5秒后自动停止测试
    setTimeout(() => {
      if (isRecording.value) {
        stopRecording()
      }
    }, 5000)
    
  } catch (error) {
    addLog(`❌ 录音启动失败: ${error.message}`)
    alert(`录音启动失败:\n${error.message}`)
  }
}

// 停止录音
const stopRecording = () => {
  addLog('⏹️ 停止录音...')
  isRecording.value = false
  addLog('✅ 录音已停止')
}

// 测试发送音频数据
const testSendAudio = async (audioBlob) => {
  addLog(`📤 开始测试音频发送... (${audioBlob.size} 字节)`)
  
  const formData = new FormData()
  formData.append('audio_chunk', audioBlob, 'test.webm')
  formData.append('source_lang', 'zh')
  formData.append('target_lang', 'en')
  
  try {
    addLog('🌐 发送HTTP请求到后端...')
    const response = await fetch('http://127.0.0.1:8000/api/translate', {
      method: 'POST',
      body: formData
    })
    
    addLog(`📥 收到响应: ${response.status} ${response.statusText}`)
    
    if (response.ok) {
      const data = await response.json()
      addLog(`✅ API调用成功: ${JSON.stringify(data)}`)
    } else {
      const errorText = await response.text()
      addLog(`❌ API调用失败: ${response.status} - ${errorText}`)
    }
    
  } catch (error) {
    addLog(`💥 网络请求失败: ${error.message}`)
  }
}

// 测试后端连接
const testBackendConnection = async () => {
  addLog('🔗 开始测试后端连接...')
  
  try {
    const response = await fetch('http://127.0.0.1:8000/health')
    if (response.ok) {
      const data = await response.json()
      backendStatus.value = `✅ 连接成功 (${response.status})`
      addLog(`✅ 后端连接成功: ${JSON.stringify(data)}`)
    } else {
      backendStatus.value = `❌ 连接失败 (${response.status})`
      addLog(`❌ 后端连接失败: ${response.status}`)
    }
  } catch (error) {
    backendStatus.value = `💥 连接异常: ${error.message}`
    addLog(`💥 后端连接异常: ${error.message}`)
  }
}

// 测试直接API调用
const testDirectAPI = async () => {
  addLog('🎵 开始测试直接API调用...')
  
  // 创建简单的测试数据
  const testData = new Uint8Array(1000).fill(128)
  const blob = new Blob([testData], { type: 'audio/webm' })
  
  const formData = new FormData()
  formData.append('audio_chunk', blob, 'direct_test.webm')
  formData.append('source_lang', 'zh')
  formData.append('target_lang', 'en')
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/translate', {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const data = await response.json()
      apiTestResult.value = `✅ 成功: ${JSON.stringify(data)}`
      addLog(`✅ 直接API调用成功: ${JSON.stringify(data)}`)
    } else {
      const errorText = await response.text()
      apiTestResult.value = `❌ 失败: ${response.status} - ${errorText}`
      addLog(`❌ 直接API调用失败: ${response.status} - ${errorText}`)
    }
  } catch (error) {
    apiTestResult.value = `💥 异常: ${error.message}`
    addLog(`💥 直接API调用异常: ${error.message}`)
  }
}

// 组件挂载时的初始化
addLog('🚀 按钮测试组件已加载')
addLog('💡 请点击按钮开始测试')
</script>