<template>
  <div class="debug-container">
    <h1>🎤 录音功能调试模式</h1>
    
    <!-- 调试信息面板 -->
    <div class="debug-panel">
      <h2>🔧 调试信息</h2>
      <div class="status-item">
        <strong>录音状态:</strong> 
        <span :class="recordingStatusClass">{{ recordingStatusText }}</span>
      </div>
      <div class="status-item">
        <strong>麦克风权限:</strong> 
        <span :class="permissionStatusClass">{{ permissionStatusText }}</span>
      </div>
      <div class="status-item">
        <strong>MediaRecorder:</strong> 
        <span :class="mediaRecorderStatusClass">{{ mediaRecorderStatusText }}</span>
      </div>
      <div class="status-item">
        <strong>后端连接:</strong> 
        <span :class="backendStatusClass">{{ backendStatusText }}</span>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="control-panel">
      <button @click="checkAllStatus" class="btn-primary">
        🔄 检查所有状态
      </button>
      <button @click="testMicrophone" class="btn-secondary">
        🎤 测试麦克风
      </button>
      <button @click="startDebugRecording" :disabled="isRecording" class="btn-record">
        {{ isRecording ? '⏹️ 停止录音' : '▶️ 开始录音测试' }}
      </button>
    </div>

    <!-- 详细日志 -->
    <div class="log-panel">
      <h2>📝 详细日志</h2>
      <div class="log-container" ref="logContainer">
        <div 
          v-for="(log, index) in logs" 
          :key="index" 
          :class="['log-entry', log.type]"
        >
          [{{ log.timestamp }}] {{ log.message }}
        </div>
      </div>
      <button @click="clearLogs" class="btn-clear">🗑️ 清空日志</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const isRecording = ref(false)
const hasMicrophonePermission = ref(false)
const mediaRecorderSupported = ref(false)
const backendConnected = ref(false)
const logs = ref([])
const logContainer = ref(null)

// 计算属性 - 状态文本
const recordingStatusText = computed(() => 
  isRecording.value ? '录音中' : '未录音'
)

const permissionStatusText = computed(() => 
  hasMicrophonePermission.value ? '已授权' : '未授权'
)

const mediaRecorderStatusText = computed(() => 
  mediaRecorderSupported.value ? '支持' : '不支持'
)

const backendStatusText = computed(() => 
  backendConnected.value ? '已连接' : '未连接'
)

// 计算属性 - 状态样式类
const recordingStatusClass = computed(() => 
  isRecording.value ? 'status-active' : 'status-inactive'
)

const permissionStatusClass = computed(() => 
  hasMicrophonePermission.value ? 'status-success' : 'status-error'
)

const mediaRecorderStatusClass = computed(() => 
  mediaRecorderSupported.value ? 'status-success' : 'status-error'
)

const backendStatusClass = computed(() => 
  backendConnected.value ? 'status-success' : 'status-error'
)

// 添加日志
const addLog = (message, type = 'info') => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({ timestamp, message, type })
  
  // 保持最新的100条日志
  if (logs.value.length > 100) {
    logs.value.shift()
  }
  
  // 滚动到底部
  setTimeout(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  }, 10)
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 检查所有状态
const checkAllStatus = async () => {
  addLog('🔍 开始检查所有系统状态...', 'info')
  
  // 检查MediaRecorder支持
  mediaRecorderSupported.value = typeof MediaRecorder !== 'undefined'
  addLog(
    mediaRecorderSupported.value ? 
    '✅ MediaRecorder API 可用' : 
    '❌ MediaRecorder API 不可用', 
    mediaRecorderSupported.value ? 'success' : 'error'
  )
  
  // 检查麦克风权限
  await checkMicrophonePermission()
  
  // 检查后端连接
  await checkBackendConnection()
  
  addLog('🏁 状态检查完成', 'info')
}

// 检查麦克风权限
const checkMicrophonePermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    hasMicrophonePermission.value = true
    addLog('✅ 麦克风权限已获取', 'success')
    
    // 立即关闭流
    stream.getTracks().forEach(track => track.stop())
  } catch (error) {
    hasMicrophonePermission.value = false
    addLog(`❌ 麦克风权限获取失败: ${error.message}`, 'error')
  }
}

// 检查后端连接
const checkBackendConnection = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/health')
    backendConnected.value = response.ok
    if (response.ok) {
      const data = await response.json()
      addLog(`✅ 后端连接成功: ${JSON.stringify(data)}`, 'success')
    } else {
      addLog(`❌ 后端返回错误: ${response.status}`, 'error')
    }
  } catch (error) {
    backendConnected.value = false
    addLog(`❌ 后端连接失败: ${error.message}`, 'error')
  }
}

// 测试麦克风
const testMicrophone = async () => {
  addLog('🎤 开始测试麦克风功能...', 'info')
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true
      }
    })
    
    addLog('✅ 麦克风流获取成功', 'success')
    
    // 获取设备信息
    const devices = await navigator.mediaDevices.enumerateDevices()
    const audioInputs = devices.filter(d => d.kind === 'audioinput')
    addLog(`🎧 检测到 ${audioInputs.length} 个音频输入设备`, 'info')
    
    // 显示第一个设备信息
    if (audioInputs.length > 0) {
      addLog(`📱 主要设备: ${audioInputs[0].label || '默认设备'}`, 'info')
    }
    
    // 关闭流
    stream.getTracks().forEach(track => {
      track.stop()
      addLog('🔇 麦克风流已关闭', 'info')
    })
    
  } catch (error) {
    addLog(`❌ 麦克风测试失败: ${error.message}`, 'error')
  }
}

// 调试录音功能
let debugMediaRecorder = null
let debugStream = null

const startDebugRecording = async () => {
  if (isRecording.value) {
    // 停止录音
    if (debugMediaRecorder) {
      debugMediaRecorder.stop()
    }
    if (debugStream) {
      debugStream.getTracks().forEach(track => track.stop())
    }
    isRecording.value = false
    addLog('⏹️ 调试录音已停止', 'info')
    return
  }
  
  // 开始录音
  addLog('🎙️ 开始调试录音...', 'info')
  
  try {
    debugStream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000
      }
    })
    
    addLog('✅ 麦克风流获取成功', 'success')
    
    // 检查支持的MIME类型
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg'
    ]
    
    let selectedMimeType = ''
    for (let mimeType of mimeTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        selectedMimeType = mimeType
        break
      }
    }
    
    if (!selectedMimeType) {
      throw new Error('没有找到支持的音频格式')
    }
    
    addLog(`_CODEC_ 选择的音频格式: ${selectedMimeType}`, 'info')
    
    debugMediaRecorder = new MediaRecorder(debugStream, { 
      mimeType: selectedMimeType 
    })
    
    addLog('✅ MediaRecorder初始化成功', 'success')
    
    // 设置事件监听器
    debugMediaRecorder.ondataavailable = async (event) => {
      if (event.data.size > 0) {
        addLog(`🔊 收到音频数据: ${event.data.size} 字节`, 'info')
        
        // 立即测试发送
        if (event.data.size > 1000) {
          await testSendAudioData(event.data)
        }
      }
    }
    
    debugMediaRecorder.onstop = () => {
      addLog('⏹️ MediaRecorder已停止', 'info')
    }
    
    debugMediaRecorder.onerror = (event) => {
      addLog(`❌ MediaRecorder错误: ${event.error}`, 'error')
    }
    
    // 开始录音，每500ms获取一次数据
    debugMediaRecorder.start(500)
    isRecording.value = true
    addLog('✅ 调试录音已开始，可以说话测试...', 'success')
    
  } catch (error) {
    addLog(`❌ 调试录音启动失败: ${error.message}`, 'error')
  }
}

// 测试发送音频数据
const testSendAudioData = async (audioBlob) => {
  addLog(`📤 开始测试音频数据发送... (${audioBlob.size} 字节)`, 'info')
  
  const formData = new FormData()
  formData.append('audio_chunk', audioBlob, 'debug_recording.webm')
  formData.append('source_lang', 'zh')
  formData.append('target_lang', 'en')
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/translate', {
      method: 'POST',
      body: formData,
      timeout: 10000
    })
    
    addLog(`📥 收到响应: ${response.status} ${response.statusText}`, 'info')
    
    if (response.ok) {
      const data = await response.json()
      addLog(`✅ 翻译成功: ${JSON.stringify(data)}`, 'success')
    } else {
      const errorText = await response.text()
      addLog(`❌ 翻译失败: ${response.status} - ${errorText}`, 'error')
    }
    
  } catch (error) {
    addLog(`💥 网络请求失败: ${error.message}`, 'error')
  }
}

// 组件挂载时自动检查
onMounted(() => {
  addLog('🚀 调试组件已加载', 'info')
  checkAllStatus()
})
</script>

<style scoped>
.debug-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.debug-panel {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin: 20px 0;
  border-left: 5px solid #42b983;
}

.status-item {
  margin: 10px 0;
  padding: 8px;
  background: white;
  border-radius: 5px;
}

.status-active { color: #dc3545; font-weight: bold; }
.status-inactive { color: #6c757d; }
.status-success { color: #28a745; }
.status-error { color: #dc3545; }

.control-panel {
  text-align: center;
  margin: 30px 0;
}

.btn-primary, .btn-secondary, .btn-record, .btn-clear {
  padding: 12px 25px;
  margin: 5px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-record {
  background: #007bff;
  color: white;
}

.btn-clear {
  background: #ffc107;
  color: #212529;
}

.btn-primary:hover, .btn-secondary:hover, .btn-record:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.log-panel {
  background: #2d2d2d;
  border-radius: 10px;
  padding: 20px;
  margin: 20px 0;
}

.log-container {
  height: 300px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #fff;
  padding: 15px;
  border-radius: 5px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  margin: 15px 0;
}

.log-entry {
  margin: 5px 0;
  padding: 3px 0;
}

.log-entry.success { color: #4caf50; }
.log-entry.error { color: #f44336; }
.log-entry.info { color: #2196f3; }
.log-entry.warning { color: #ff9800; }
</style>