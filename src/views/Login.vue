<template>
  <div class="login-container">
    <!-- 粒子效果背景 -->
    <ParticlesBackground v-if="showParticles" @particles-ended="handleParticlesEnded" />
    
    <!-- 增强背景效果 -->
    <div class="bg-shapes" :class="{ 'bg-fade-out': !showParticles }">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <div class="login-form-wrapper" @mouseenter="formHover = true" @mouseleave="formHover = false">
      <div class="login-title" :class="{ 'title-bounce': formHover }">sunshine的智能停车管理系统</div>
      
      <el-form :model="loginForm" label-width="0" class="login-form">
        <el-form-item prop="username">
          <div class="input-group" :class="{ 'input-focus': focusUsername, 'input-error': errors.username }">
            <i class="el-icon-user"></i>
            <el-input 
              v-model="loginForm.username" 
              placeholder="用户名" 
              class="login-input"
              @focus="focusUsername = true"
              @blur="focusUsername = false; validateUsername"
              @input="errors.username = ''"
            ></el-input>
            <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-group" :class="{ 'input-focus': focusPassword, 'input-error': errors.password }">
            <i class="el-icon-lock"></i>
            <el-input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="loginForm.password" 
              placeholder="密码" 
              class="login-input"
              @focus="focusPassword = true"
              @blur="focusPassword = false"
              @input="errors.password = ''"
            >
              <template #suffix>
                <i 
                  :class="[showPassword ? 'el-icon-view' : 'el-icon-view-off', 'password-toggle']"
                  @click="togglePasswordVisibility"
                ></i>
              </template>
            </el-input>
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin"
            :loading="isLoading"
            :disabled="isLoading"
            class="login-button"
          >
            <template v-if="!isLoading">登录</template>
            <template v-else>
              <span class="loading-spinner"></span>
              登录中...
            </template>
          </el-button>
        </el-form-item>
        
        <el-form-item class="register-link">
          <span>还没有账号？</span>
          <el-button 
            type="text" 
            @click="navigateToRegister"
            class="register-button"
          >立即注册</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 登录成功/失败的反馈动画 -->
      <div v-if="showFeedback" :class="['feedback-overlay', feedbackType]">
        <div class="feedback-content">
          <div :class="['feedback-icon', feedbackType]">
            {{ feedbackType === 'success' ? '✓' : '✗' }}
          </div>
          <div class="feedback-text">{{ feedbackMessage }}</div>
        </div>
      </div>
    </div>
    
    <div class="login-animation" :class="{ 'fade-in': !showParticles }">
      <div class="car-animation" :class="{ 'car-excited': formHover }"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage'
}
</script>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ParticlesBackground from '../components/ParticlesBackground.vue'

// 表单状态
const loginForm = ref({
  username: '',
  password: ''
})

// 交互状态
const focusUsername = ref(false)
const focusPassword = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const formHover = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('') // 'success' 或 'error'
const feedbackMessage = ref('')

// 验证错误
const errors = ref({
  username: '',
  password: ''
})

// 粒子效果控制
const showParticles = ref(true)

// 处理粒子效果结束事件
const handleParticlesEnded = () => {
  console.log('接收到particles-ended事件，设置showParticles为false');
  showParticles.value = false;
  console.log('showParticles值已更新:', showParticles.value);
}

const router = useRouter()

// 验证用户名
const validateUsername = () => {
  if (!loginForm.value.username.trim()) {
    errors.value.username = '请输入用户名'
    return false
  }
  return true
}

// 验证密码
const validatePassword = () => {
  if (!loginForm.value.password) {
    errors.value.password = '请输入密码'
    return false
  }
  return true
}

// 切换密码可见性
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
  // 添加密码切换的微动画效果
  const passwordInput = document.querySelector('.login-input[type="password"], .login-input[type="text"]')
  if (passwordInput) {
    passwordInput.classList.add('password-toggle-animation')
    setTimeout(() => {
      passwordInput.classList.remove('password-toggle-animation')
    }, 300)
  }
}

// 导航到注册页
const navigateToRegister = () => {
  // 添加页面切换动画
  router.push('/register')
}

// 显示反馈信息
const showFeedbackMessage = (type, message) => {
  feedbackType.value = type
  feedbackMessage.value = message
  showFeedback.value = true
  
  setTimeout(() => {
    showFeedback.value = false
  }, 3000)
}

// 生命周期钩子，初始化页面
onMounted(() => {
  console.log('登录页面已加载');
})

// 处理登录
const handleLogin = async () => {
  // 验证表单
  const isUsernameValid = validateUsername()
  const isPasswordValid = validatePassword()
  
  if (!isUsernameValid || !isPasswordValid) {
    // 给错误的输入框添加抖动效果
    const errorInputs = document.querySelectorAll('.input-error')
    errorInputs.forEach(input => {
      input.classList.add('error-shake')
      setTimeout(() => {
        input.classList.remove('error-shake')
      }, 500)
    })
    return
  }
  
  // 设置加载状态
  isLoading.value = true
  
  try {
    const trimmedForm = {
      username: loginForm.value.username.trim(),
      password: loginForm.value.password.trim()
    }
    
    // 增加请求超时处理
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000) // 10秒超时
    
    const response = await fetch('http://127.0.0.1:5000/api/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trimmedForm),
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.code === 200) {
      // 保存token、用户ID和角色到localStorage
      localStorage.setItem('token', data.data.token)
      localStorage.setItem('user_id', data.data.user_id)
      localStorage.setItem('role', data.data.role || 'user')
      
      // 显示成功反馈
      showFeedbackMessage('success', '登录成功！')
      
      // 延迟跳转，让用户看到成功动画
      setTimeout(() => {
        // 添加页面切换的动画效果
        const formWrapper = document.querySelector('.login-form-wrapper')
        if (formWrapper) {
          formWrapper.classList.add('form-success-exit')
          setTimeout(() => {
            router.push('/')
          }, 500)
        } else {
          router.push('/')
        }
      }, 1000)
    } else {
      // 显示错误反馈
      showFeedbackMessage('error', data.message || '登录失败')
    }
  } catch (error) {
    // 详细的错误处理
    let errorMessage = '登录失败，请重试'
    
    if (error.name === 'AbortError') {
      errorMessage = '请求超时，请检查网络连接'
    } else if (error.message.includes('Failed to fetch')) {
      errorMessage = '无法连接到服务器，请检查后端服务是否正在运行'
    } else {
      errorMessage = error.message || '登录失败，请重试'
    }
    
    // 显示错误反馈
    showFeedbackMessage('error', errorMessage)
    
    // 添加重试按钮的逻辑
    setTimeout(() => {
      showFeedback.value = false
    }, 4000) // 延长显示时间
  } finally {
    // 重置加载状态
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  z-index: 1; /* 确保登录容器在最上层 */
  opacity: 1; /* 默认完全可见 */
  overflow: hidden;
  transition: background-position 0.5s ease;
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

/* 背景淡出动画 */
.bg-fade-out {
  animation: fadeOut 1s ease-out forwards;
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    z-index: -1;
  }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 确保登录表单在粒子效果后显示 */
.login-form-wrapper {
  opacity: 0;
  animation: fadeInForm 1s ease-out 5s forwards;
}

/* 增强的背景效果 */
.bg-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.4;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: rgba(102, 126, 234, 0.6);
  top: -250px;
  left: -250px;
  animation: floatLarge 20s ease-in-out infinite;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: rgba(118, 75, 162, 0.6);
  bottom: -200px;
  right: -200px;
  animation: floatLarge 25s ease-in-out infinite reverse;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: floatMedium 15s ease-in-out infinite;
}

/* 渐变背景动画 */
@keyframes gradientShift {
  0% { background-position: 0% 50% }
  50% { background-position: 100% 50% }
  100% { background-position: 0% 50% }
}

@keyframes floatLarge {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(50px, 50px) scale(1.1); }
}

@keyframes floatMedium {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(calc(-50% + 30px), calc(-50% + 30px)) scale(1.2); }
}

.login-form-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 420px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%); /* 向上偏移一些，让位置更居中 */
  z-index: 5; /* 确保登录表单在背景之上，但在粒子效果之下 */
  opacity: 0; /* 默认隐藏 */
  transition: opacity 0.8s ease-in, transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  backdrop-filter: blur(10px);
  pointer-events: none; /* 防止点击隐藏的表单 */
  animation: none; /* 移除原动画，由粒子效果触发显示 */
}

/* 当没有粒子效果时显示表单 */
.login-container:not(:has(.particles-container)) .login-form-wrapper {
  opacity: 1;
  pointer-events: auto;
  animation: slideUp 0.6s ease-out;
  transform: translate(-50%, -60%); /* 保持居中位置 */
}

/* 表单悬浮效果 */
.login-form-wrapper:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  background: rgba(255, 255, 255, 0.98);
}

/* 表单成功退出动画 */
.form-success-exit {
  animation: formExit 0.5s ease-out forwards;
}

@keyframes formExit {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: #333;
  transition: transform 0.3s ease;
}

/* 标题弹跳效果 */
.title-bounce {
  animation: titleBounce 0.6s ease-out;
}

@keyframes titleBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.login-form {
  width: 100%;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border-radius: 25px;
  overflow: hidden;
}

.input-group i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  z-index: 1;
  transition: color 0.3s ease, transform 0.3s ease;
}

/* 输入框聚焦效果 */
.input-group.input-focus {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.input-group.input-focus i {
  color: #667eea;
  transform: translateY(-50%) scale(1.1);
}

/* 输入框错误效果 */
.input-group.input-error {
  box-shadow: 0 0 0 3px rgba(235, 87, 87, 0.2);
}

.input-group.input-error i {
  color: #eb5757;
}

/* 错误抖动动画 */
.input-group.error-shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.login-input {
  width: 100%;
  padding-left: 45px;
  padding-right: 45px;
  height: 45px;
  border: 2px solid #ddd;
  border-radius: 25px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
}

.login-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: inset 0 0 0 2px rgba(102, 126, 234, 0.2);
  transform: scale(1.02);
}

/* 密码切换动画 */
.login-input.password-toggle-animation {
  animation: passwordToggle 0.3s ease-in-out;
}

@keyframes passwordToggle {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

/* 密码可见性切换按钮 */
.password-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
  transition: color 0.3s ease, transform 0.3s ease;
}

.password-toggle:hover {
  color: #667eea;
  transform: translateY(-50%) scale(1.1);
}

/* 错误消息样式 */
.error-message {
  position: absolute;
  top: 100%;
  left: 15px;
  font-size: 12px;
  color: #eb5757;
  margin-top: 4px;
  opacity: 0;
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-button {
  width: 100%;
  height: 45px;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  background-size: 200% auto;
  animation: buttonGradient 3s ease infinite;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* 按钮渐变动画 */
@keyframes buttonGradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(102, 126, 234, 0.5);
  background-position: right center;
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 8px 15px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.8;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载动画 */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.register-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.register-link span {
  margin-right: 5px;
}

.register-button {
  color: #667eea;
  padding: 0;
  position: relative;
  transition: color 0.3s ease;
}

.register-button:hover {
  color: #764ba2;
}

.register-button::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #667eea;
  transition: width 0.3s ease;
}

.register-button:hover::after {
  width: 100%;
}

/* 登录动画区域 */
.login-animation {
  position: absolute;
  top: 50%; /* 与登录表单垂直居中对齐 */
  left: calc(50% + 300px); /* 位于登录表单右侧，进一步右移 */
  transform: translateY(-50%);
  width: 150px;
  height: 100px;
  opacity: 0;
  transition: opacity 0.8s ease-in;
  pointer-events: none;
  z-index: 4; /* 确保在登录表单后面 */
}

/* 确保小车在fade-in后保持可见 */
.login-animation.fade-in {
  opacity: 1 !important;
}

.car-animation {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  position: relative;
  transition: transform 0.3s ease;
}

/* 车辆兴奋动画 */
.car-animation.car-excited {
  animation: carExcited 1s ease-in-out;
}

@keyframes carExcited {
  0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
  25% { transform: translateY(-15px) rotate(3deg) scale(1.05); }
  50% { transform: translateY(5px) rotate(-2deg) scale(1.03); }
  75% { transform: translateY(-10px) rotate(2deg) scale(1.05); }
}

.car-animation::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 10px;
  width: 60px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.car-animation::after {
  content: '';
  position: absolute;
  bottom: -15px;
  left: 20px;
  width: 40px;
  height: 30px;
  background: #333;
  border-radius: 5px;
  box-shadow: 100px 0 0 #333;
  animation: wheelsRotate 1s linear infinite;
}

/* 车轮旋转动画 */
@keyframes wheelsRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes carMove {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-10px) rotate(2deg);
  }
  75% {
    transform: translateY(10px) rotate(-2deg);
  }
}

/* 反馈覆盖层 */
.feedback-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  z-index: 10;
  animation: feedbackAppear 0.3s ease-out;
}

@keyframes feedbackAppear {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.feedback-content {
  text-align: center;
  padding: 20px;
}

.feedback-icon {
  font-size: 40px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-weight: bold;
}

/* 成功反馈样式 */
.feedback-overlay.success {
  background: rgba(255, 255, 255, 0.98);
}

.feedback-icon.success {
  background: rgba(72, 187, 120, 0.2);
  color: #48bb78;
  animation: successPulse 0.6s ease-out;
}

@keyframes successPulse {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* 错误反馈样式 */
.feedback-overlay.error {
  background: rgba(255, 255, 255, 0.98);
}

.feedback-icon.error {
  background: rgba(235, 87, 87, 0.2);
  color: #eb5757;
  animation: errorShake 0.3s ease-in-out;
}

@keyframes errorShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.feedback-text {
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    padding: 10px;
  }
  
  .login-animation {
    margin-left: 0;
    margin-top: 30px;
    width: 100%;
    height: auto;
  }
  
  .car-animation {
    width: 150px;
    height: 90px;
  }
  
  .login-form-wrapper {
    padding: 30px 20px;
  }
}
</style>