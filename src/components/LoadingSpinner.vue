<template>
  <div v-if="visible" :class="['loading-spinner-container', position, { 'full-screen': fullScreen }]">
    <div class="loading-spinner">
      <div class="spinner"></div>
      <div v-if="text" class="loading-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 组件属性
const props = defineProps({
  // 是否可见
  visible: {
    type: Boolean,
    default: false
  },
  // 加载文本
  text: {
    type: String,
    default: '加载中...'
  },
  // 位置：center, top, bottom, left, right
  position: {
    type: String,
    default: 'center',
    validator: (value) => {
      return ['center', 'top', 'bottom', 'left', 'right'].includes(value)
    }
  },
  // 是否全屏覆盖
  fullScreen: {
    type: Boolean,
    default: false
  },
  // 是否透明背景
  transparent: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* 加载容器 */
.loading-spinner-container {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: all 0.3s ease;
}

/* 全屏加载 */
.loading-spinner-container.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(2px);
}

/* 透明背景 */
.loading-spinner-container.transparent {
  background-color: transparent;
}

/* 位置样式 */
.loading-spinner-container.center {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-spinner-container.top {
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.loading-spinner-container.bottom {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.loading-spinner-container.left {
  top: 50%;
  left: 20px;
  transform: translateY(-50%);
}

.loading-spinner-container.right {
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
}

/* 加载动画 */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-xl);
  animation: fadeIn 0.3s ease-out;
}

/* 透明模式下的加载动画 */
.loading-spinner-container.transparent .loading-spinner {
  background-color: transparent;
  box-shadow: none;
}

/* 加载文本 */
.loading-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

/* 旋转动画 */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--light-gray);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
  position: relative;
}

/* 添加双层旋转效果 */
.spinner::before {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  width: 40px;
  height: 40px;
  border: 4px solid transparent;
  border-bottom-color: var(--secondary-color);
  border-radius: 50%;
  animation: spinReverse 1.5s ease-in-out infinite;
}

/* 旋转动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 反向旋转动画 */
@keyframes spinReverse {
  to {
    transform: rotate(-360deg);
  }
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>