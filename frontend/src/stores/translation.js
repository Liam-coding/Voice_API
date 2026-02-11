// frontend/src/stores/translation.js
import { defineStore } from 'pinia'

export const useTranslationStore = defineStore('translation', {
  state: () => ({
    results: [], // 存储当前的实时翻译片段
    history: []  // 存储点击停止后的历史记录
  }),
  actions: {
    addResult(data) {
      console.log('📥 添加翻译结果到store:', data)
      if (data.translation || data.original) {
        // 确保数据格式一致
        const resultItem = {
          id: Date.now() + Math.random(),
          translation: data.translation || '',
          original: data.original || '',
          timestamp: new Date().toISOString()
        }
        this.results.push(resultItem)
        console.log('✅ 结果已添加，当前结果数量:', this.results.length)
      } else {
        console.log('⚠️ 跳过空结果')
      }
    },
    saveToHistory() {
      if (this.results.length > 0) {
        const fullText = this.results.map(r => r.translation).join('')
        this.history.unshift({
          id: Date.now(),
          time: new Date().toLocaleTimeString(),
          content: fullText
        })
        this.results = [] // 保存后清空当前显示
      }
    }
  }
})