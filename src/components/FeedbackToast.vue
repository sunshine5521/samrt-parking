<template>
  <div class="feedback-container">
    <!-- 反馈消息列表 -->
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="[
        'feedback-toast',
        toast.type,
        { 'feedback-toast-top': position === 'top' },
        { 'feedback-toast-bottom': position === 'bottom' }
      ]"
      :style="{
        zIndex: 9999,
        animationDelay: `${toast.delay}s`
      }"
    >
      <!-- 图标 -->
      <div class="feedback-icon">
        <el-icon v-if="toast.type === 'success'">
          <CircleCheckFilled />
        </el-icon>
        <el-icon v-else-if="toast.type === 'error'">
          <CircleCloseFilled />
        </el-icon>
        <el-icon v-else-if="toast.type === 'warning'">
          <CircleWarningFilled />
        </el-icon>
        <el-icon v-else-if="toast.type === 'info'">
          <CircleInfoFilled />
        </el-icon>
      </div>
      
      <!-- 内容 -->
      <div class="feedback-content">
        <div class="feedback-title">{{ toast.title || getDefaultTitle(toast.type) }}</div>
        <div class="feedback-message">{{ toast.message }}</div>
      </div>
      
      <!-- 关闭按钮 -->
      <div class="feedback-close" @click="removeToast(toast.id)">
        <el-icon><CircleClose /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { CircleCheckFilled, CircleCloseFilled, CircleWarningFilled, CircleInfoFilled, CircleClose } from '@element-plus/icons-vue'

// 组件属性
const props = defineProps({
  // 位置：top, bottom
  position: {
    type: String,
    default: 'top',
    validator: (value) => {
      return ['top', 'bottom'].includes(value)
    }
  },
  // 自动关闭时间（毫秒）
  duration: {
    type: Number,
    default: 3000
  }
})

// 反馈消息列表
const toasts = ref([])

// 生成唯一ID
const generateId = () => {
  return Date.now() + Math.random().toString(36).substr(2, 9)
}

// 获取默认标题
const getDefaultTitle = (type) => {
  const titles = {
    success: '成功',
    error: '错误',
    warning: '警告',
    info: '提示'
  }
  return titles[type] || '提示'
}

// 添加反馈消息
const addToast = (options) => {
  const toast = {
    id: generateId(),
    type: 'info',
    title: '',
    message: '',
    duration: props.duration,
    delay: 0,
    ...options
  }
  
  toasts.value.push(toast)
  
  // 自动移除
  if (toast.duration > 0) {
    setTimeout(() => {
      removeToast(toast.id)
    }, toast.duration + toast.delay * 1000)
  }
  
  return toast.id
}

// 移除反馈消息
const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

// 清空所有反馈消息
const clearToasts = () => {
  toasts.value = []
}

// 暴露方法给父组件
const methods = {
  success: (message, title, options = {}) => {
    return addToast({ type: 'success', message, title, ...options })
  },
  error: (message, title, options = {}) => {
    return addToast({ type: 'error', message, title, ...options })
  },
  warning: (message, title, options = {}) => {
    return addToast({ type: 'warning', message, title, ...options })
  },
  info: (message, title, options = {}) => {
    return addToast({ type: 'info', message, title, ...options })
  },
  clear: clearToasts,
  remove: removeToast
}

defineExpose(methods)
</script>

<style scoped>
/* 容器 */
.feedback-container {
  position: fixed;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 9999;
}

/* 顶部位置 */
.feedback-toast-top {
  top: 20px;
}

/* 底部位置 */
.feedback-toast-bottom {
  bottom: 20px;
}

/* 反馈消息 */
.feedback-toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  margin: 10px auto;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  background-color: white;
  max-width: 400px;
  width: 90%;
  animation: slideIn 0.3s ease-out forwards, slideOut 0.3s ease-in forwards 2.7s;
  pointer-events: auto;
  border-left: 4px solid transparent;
  position: relative;
  overflow: hidden;
}

/* 添加背景渐变效果 */
.feedback-toast::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  animation: progress 3s ease-out forwards;
}

/* 进度条动画 */
@keyframes progress {
  from { width: 100%; }
  to { width: 0; }
}

/* 滑入动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 滑出动画 */
@keyframes slideOut {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-50px);
  }
}

/* 底部滑入动画 */
.feedback-toast-bottom {
  animation: slideInBottom 0.3s ease-out forwards, slideOutBottom 0.3s ease-in forwards 2.7s;
}

@keyframes slideInBottom {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideOutBottom {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(50px);
  }
}

/* 图标样式 */
.feedback-icon {
  font-size: 24px;
  margin-top: 2px;
  flex-shrink: 0;
}

/* 内容区域 */
.feedback-content {
  flex: 1;
  min-width: 0;
}

/* 标题样式 */
.feedback-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

/* 消息样式 */
.feedback-message {
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-secondary);
}

/* 关闭按钮 */
.feedback-close {
  font-size: 16px;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.feedback-close:hover {
  opacity: 1;
  transform: scale(1.1);
}

/* 类型样式 - 成功 */
.feedback-toast.success {
  border-left-color: var(--success-color);
  box-shadow: 0 4px 12px rgba(72, 187, 120, 0.15);
}

.feedback-toast.success .feedback-icon {
  color: var(--success-color);
}

.feedback-toast.success .feedback-title {
  color: var(--success-color);
}

.feedback-toast.success::before {
  background: linear-gradient(90deg, var(--success-color), #38a169);
}

/* 类型样式 - 错误 */
.feedback-toast.error {
  border-left-color: var(--danger-color);
  box-shadow: 0 4px 12px rgba(245, 101, 101, 0.15);
}

.feedback-toast.error .feedback-icon {
  color: var(--danger-color);
}

.feedback-toast.error .feedback-title {
  color: var(--danger-color);
}

.feedback-toast.error::before {
  background: linear-gradient(90deg, var(--danger-color), #e53e3e);
}

/* 类型样式 - 警告 */
.feedback-toast.warning {
  border-left-color: var(--warning-color);
  box-shadow: 0 4px 12px rgba(237, 137, 54, 0.15);
}

.feedback-toast.warning .feedback-icon {
  color: var(--warning-color);
}

.feedback-toast.warning .feedback-title {
  color: var(--warning-color);
}

.feedback-toast.warning::before {
  background: linear-gradient(90deg, var(--warning-color), #dd6b20);
}

/* 类型样式 - 信息 */
.feedback-toast.info {
  border-left-color: var(--info-color);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
}

.feedback-toast.info .feedback-icon {
  color: var(--info-color);
}

.feedback-toast.info .feedback-title {
  color: var(--info-color);
}

.feedback-toast.info::before {
  background: linear-gradient(90deg, var(--info-color), #3182ce);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feedback-toast {
    margin: 8px;
    padding: 14px 18px;
    max-width: calc(100% - 16px);
  }
  
  .feedback-toast-top {
    top: 10px;
  }
  
  .feedback-toast-bottom {
    bottom: 10px;
  }
}
</style>