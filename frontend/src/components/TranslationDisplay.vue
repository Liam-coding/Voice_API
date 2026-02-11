<template>
  <div class="display-container">
    <div v-if="store.results.length === 0" class="no-results">
      等待翻译结果...
    </div>
    <div v-for="(item, index) in store.results" :key="index" class="message-row">
      <div class="source">原文: {{ item.original || '...' }}</div>
      <div class="target">译文: {{ item.translation || '翻译中...' }}</div>
    </div>
  </div>
</template>

<script setup>
import { useTranslationStore } from '../stores/translation'

const store = useTranslationStore()
</script>

<style scoped>
.display-container {
  min-height: 100px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  text-align: left;
}

.no-results {
  color: #666;
  text-align: center;
  padding: 20px;
  font-style: italic;
}

.message-row {
  margin-bottom: 15px;
  padding: 10px;
  background: white;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.source {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.target {
  color: #2c3e50;
  font-weight: 500;
  font-size: 16px;
}
</style>