import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 导入 Pinia
import App from './App.vue'

// 导入全局样式（如果 Vite 自带了样式文件）
import './style.css'

const app = createApp(App)

// 2. 创建 Pinia 实例
const pinia = createPinia()

// 3. 将 Pinia 插件安装到 Vue 实例中
app.use(pinia)

// 4. 最后挂载应用
app.mount('#app')