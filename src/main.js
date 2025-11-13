import { createApp } from 'vue' // 必须添加这一行，导入createApp函数
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 创建Vue应用实例
const app = createApp(App)

// 注入路由（核心步骤，使路由功能生效）
app.use(router)

// 注入Element Plus组件库（如果项目使用Element Plus）
app.use(ElementPlus)

// 将应用挂载到HTML中的#app元素
app.mount('#app')