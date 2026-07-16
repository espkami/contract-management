import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElIcons from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)
Object.entries(ElIcons).forEach(([name, comp]) => app.component(name, comp))
app.use(createPinia()).use(router).use(ElementPlus, { locale: zhCn }).mount('#app')
