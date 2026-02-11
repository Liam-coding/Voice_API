<template>
  <div class="app-wrapper">
    <header>
      <h1>Makawai 实时语音翻译</h1>
      <p class="subtitle">中 ⇄ 英 实时转译系统</p>
    </header>

    <main>
      <AudioRecorder />

      <TranslationDisplay />

      <section class="history-container">
        <h3>历史记录</h3>
        <div v-if="store.history.length === 0" class="empty">暂无历史记录</div>
        <div v-for="h in store.history" :key="h.id" class="history-card">
          <span class="time">{{ h.time }}</span>
          <p>{{ h.content }}</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import AudioRecorder from './components/AudioRecorder.vue'
import TranslationDisplay from './components/TranslationDisplay.vue'
import { useTranslationStore } from './stores/translation'

const store = useTranslationStore()
</script>

<style>
/* 极简 UI 风格 */
.app-wrapper {
  max-width: 600px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #2c3e50;
  text-align: center;
}

.subtitle { 
  color: #666; 
  margin-bottom: 40px; 
  font-size: 18px;
}

.history-container { 
  margin-top: 50px; 
  text-align: left; 
}

.history-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  border-left: 4px solid #42b983;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.time { 
  font-size: 12px; 
  color: #999; 
}

.empty { 
  color: #ccc; 
  text-align: center; 
  padding: 20px; 
  font-style: italic;
}

/* 录音状态指示器样式 */
.recorder-wrapper {
  margin: 30px 0;
}

.status-indicator {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  background: #e9ecef;
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: #d4edda;
  color: #155724;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.main-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 50px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(66, 185, 131, 0.3);
}

.main-btn:hover {
  background: #359c6d;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(66, 185, 131, 0.4);
}

.main-btn.btn-recording {
  background: #dc3545;
  animation: recording-pulse 1s infinite;
}

.main-btn.btn-recording:hover {
  background: #c82333;
}

@keyframes recording-pulse {
  0% { box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3); }
  50% { box-shadow: 0 4px 15px rgba(220, 53, 69, 0.6); }
  100% { box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3); }
}

.icon {
  font-size: 20px;
  margin-right: 8px;
  display: inline-block;
}
</style>