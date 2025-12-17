<template>
  <div class="register-container">
    <!-- 增强背景效果 -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <div class="register-form-wrapper" @mouseenter="formHover = true" @mouseleave="formHover = false">
      <div class="register-title" :class="{ 'title-bounce': formHover }">智能停车管理系统</div>
      
      <el-form :model="registerForm" label-width="0" class="register-form" :rules="rules" ref="registerFormRef">
        <el-form-item prop="username">
          <div class="input-group" :class="{ 'input-focus': focusUsername, 'input-error': errors.username }">
            <el-icon class="input-icon"><User /></el-icon>
            <el-input 
              v-model="registerForm.username" 
              placeholder="用户名" 
              class="register-input"
              @focus="focusUsername = true"
              @blur="focusUsername = false; validateUsername"
              @input="errors.username = ''"
            ></el-input>
            <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-group" :class="{ 'input-focus': focusPassword, 'input-error': errors.password }">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="registerForm.password" 
              placeholder="密码" 
              class="register-input"
              @focus="focusPassword = true"
              @blur="focusPassword = false; validatePassword"
              @input="errors.password = ''"
            >
              <template #suffix>
                <el-icon 
                  :class="[showPassword ? 'el-icon-view' : 'el-icon-view-off', 'password-toggle']"
                  @click="togglePasswordVisibility"
                ></el-icon>
              </template>
            </el-input>
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
          </div>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <div class="input-group" :class="{ 'input-focus': focusConfirmPassword, 'input-error': errors.confirmPassword }">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input 
              :type="showConfirmPassword ? 'text' : 'password'" 
              v-model="registerForm.confirmPassword" 
              placeholder="确认密码" 
              class="register-input"
              @focus="focusConfirmPassword = true"
              @blur="focusConfirmPassword = false; validateConfirmPassword"
              @input="errors.confirmPassword = ''"
            >
              <template #suffix>
                <el-icon 
                  :class="[showConfirmPassword ? 'el-icon-view' : 'el-icon-view-off', 'password-toggle']"
                  @click="toggleConfirmPasswordVisibility"
                ></el-icon>
              </template>
            </el-input>
            <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            class="register-button"
            :loading="isLoading"
            :disabled="isLoading"
          >
            <template v-if="!isLoading">注册</template>
            <template v-else>
              <span class="loading-spinner"></span>
              注册中...
            </template>
          </el-button>
        </el-form-item>
        
        <el-form-item class="login-link">
          <span>已经有账号？</span>
          <el-button 
            type="text" 
            @click="navigateToLogin"
            class="login-button"
          >立即登录</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 注册成功/失败的反馈动画 -->
      <div v-if="showFeedback" :class="['feedback-overlay', feedbackType]">
        <div class="feedback-content">
          <div :class="['feedback-icon', feedbackType]">
            {{ feedbackType === 'success' ? '✓' : '✗' }}
          </div>
          <div class="feedback-text">{{ feedbackMessage }}</div>
        </div>
      </div>
    </div>
    
    <div class="register-animation" :class="['fade-in']">
      <div class="car-animation" :class="{ 'car-excited': formHover }"></div>
    </div>
  </div>
</template>

<script>
// 用 export default 声明多单词组件名，解决“component name 必须多单词”报错
export default {
  name: 'RegisterPage'
}
</script>

<script setup>
import { ref } from 'vue'
import { ElForm, ElFormItem, ElInput, ElButton } from 'element-plus'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'

const registerFormRef = ref()
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})
const router = useRouter()

// 表单交互状态
const formHover = ref(false)
const focusUsername = ref(false)
const focusPassword = ref(false)
const focusConfirmPassword = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)

// 验证错误信息
const errors = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

// 反馈信息
const showFeedback = ref(false)
const feedbackType = ref('')
const feedbackMessage = ref('')

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 用户名验证
const validateUsername = () => {
  if (!registerForm.value.username.trim()) {
    errors.value.username = '请输入用户名'
    return false
  }
  if (registerForm.value.username.length < 3 || registerForm.value.username.length > 20) {
    errors.value.username = '用户名长度在 3 到 20 个字符'
    return false
  }
  return true
}

// 密码验证
const validatePassword = () => {
  if (!registerForm.value.password) {
    errors.value.password = '请输入密码'
    return false
  }
  if (registerForm.value.password.length < 6 || registerForm.value.password.length > 20) {
    errors.value.password = '密码长度在 6 到 20 个字符'
    return false
  }
  return true
}

// 确认密码验证
const validateConfirmPassword = () => {
  if (!registerForm.value.confirmPassword) {
    errors.value.confirmPassword = '请确认密码'
    return false
  }
  if (registerForm.value.confirmPassword !== registerForm.value.password) {
    errors.value.confirmPassword = '两次输入的密码不一致'
    return false
  }
  return true
}

// 切换密码可见性
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
  // 添加密码切换的微动画效果
  const passwordInput = document.querySelector('.register-input[type="password"], .register-input[type="text"]')
  if (passwordInput) {
    passwordInput.classList.add('password-toggle-animation')
    setTimeout(() => {
      passwordInput.classList.remove('password-toggle-animation')
    }, 300)
  }
}

// 切换确认密码可见性
const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value
  // 添加密码切换的微动画效果
  const confirmPasswordInput = document.querySelectorAll('.register-input[type="password"], .register-input[type="text"]')[1]
  if (confirmPasswordInput) {
    confirmPasswordInput.classList.add('password-toggle-animation')
    setTimeout(() => {
      confirmPasswordInput.classList.remove('password-toggle-animation')
    }, 300)
  }
}

// 导航到登录页
const navigateToLogin = () => {
  router.push('/login')
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

// 处理注册
const handleRegister = async () => {
  // 验证表单
  const isUsernameValid = validateUsername()
  const isPasswordValid = validatePassword()
  const isConfirmPasswordValid = validateConfirmPassword()
  
  if (!isUsernameValid || !isPasswordValid || !isConfirmPasswordValid) {
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
    // 修剪密码后再发送到后端
    const trimmedForm = {
      ...registerForm.value,
      username: registerForm.value.username.trim(),
      password: registerForm.value.password.trim()
    }
    const response = await fetch('http://127.0.0.1:5000/api/user/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trimmedForm)
    })
    const data = await response.json()
    if (data.code === 200) {
      // 显示成功反馈
      showFeedbackMessage('success', '注册成功，请登录')
      
      // 延迟跳转，让用户看到成功动画
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      // 显示错误反馈
      showFeedbackMessage('error', data.message || '注册失败')
    }
  } catch (error) {
    // 详细的错误处理
    let errorMessage = '注册失败，请重试'
    
    if (error.name === 'AbortError') {
      errorMessage = '请求超时，请检查网络连接'
    } else if (error.message.includes('Failed to fetch')) {
      errorMessage = '无法连接到服务器，请检查后端服务是否正在运行'
    } else {
      errorMessage = error.message || '注册失败，请重试'
    }
    
    // 显示错误反馈
    showFeedbackMessage('error', errorMessage)
  } finally {
    // 重置加载状态
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 全局样式变量 */
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #48bb78;
  --warning-color: #ed8936;
  --danger-color: #f56565;
  --light-gray: #f7fafc;
  --medium-gray: #e2e8f0;
  --dark-gray: #4a5568;
  --border-radius: 12px;
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  z-index: 1;
  opacity: 1;
  overflow: hidden;
  transition: background-position 0.5s ease;
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

/* 背景形状效果 */
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
  animation: float 15s ease-in-out infinite;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: rgba(240, 147, 251, 0.6);
  top: -250px;
  left: -250px;
  animation-delay: 0s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: rgba(245, 87, 108, 0.6);
  bottom: -200px;
  right: -200px;
  animation-delay: -5s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -2.5s;
}

/* 渐变背景动画 */
@keyframes gradientShift {
  0% { background-position: 0% 50% }
  50% { background-position: 100% 50% }
  100% { background-position: 0% 50% }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(50px, 50px) scale(1.1); }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 注册表单容器 */
.register-form-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 5;
  transition: opacity 0.8s ease-in, transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  backdrop-filter: blur(10px);
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(50px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 表单悬浮效果 */
.register-form-wrapper:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
  background: rgba(255, 255, 255, 0.98);
}

/* 注册标题 */
.register-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

/* 注册表单 */
.register-form {
  width: 100%;
}

/* 输入组 */
.input-group {
  position: relative;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border-radius: 25px;
  overflow: hidden;
  background: #f8f9fa;
  border: 2px solid transparent;
}

.input-group:hover {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* 输入框聚焦效果 */
.input-group.input-focus {
  border-color: #f5576c;
  box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.2);
  background: white;
}

/* 输入框错误效果 */
.input-group.input-error {
  border-color: #f56565;
  box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.2);
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

/* 输入图标 */
.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  z-index: 1;
  transition: color 0.3s ease, transform 0.3s ease;
}

.input-group.input-focus .input-icon {
  color: #f5576c;
  transform: translateY(-50%) scale(1.1);
}

/* 注册输入框 */
.register-input {
  border: none;
  background: transparent;
  padding: 15px 15px 15px 55px;
  border-radius: 25px;
  font-size: 14px;
  width: 100%;
  color: #333;
  transition: all 0.3s ease;
}

.register-input:focus {
  outline: none;
  box-shadow: none;
  background: transparent;
}

/* 密码切换动画 */
.register-input.password-toggle-animation {
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
  font-size: 18px;
  transition: color 0.3s ease, transform 0.3s ease;
  z-index: 1;
}

.password-toggle:hover {
  color: #f5576c;
  transform: translateY(-50%) scale(1.1);
}

/* 错误消息样式 */
.error-message {
  position: absolute;
  top: 100%;
  left: 15px;
  font-size: 12px;
  color: #f56565;
  margin-top: 4px;
  opacity: 0;
  animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 注册按钮 */
.register-button {
  width: 100%;
  height: 45px;
  border-radius: 25px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

.register-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(245, 87, 108, 0.5);
  background-position: right center;
}

.register-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 8px 15px rgba(245, 87, 108, 0.4);
}

.register-button:disabled {
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

/* 登录链接 */
.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}

.login-link span {
  margin-right: 5px;
}

.login-button {
  color: #f5576c;
  padding: 0;
  position: relative;
  transition: color 0.3s ease;
}

.login-button:hover {
  color: #f093fb;
}

.login-button::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #f5576c;
  transition: width 0.3s ease;
}

.login-button:hover::after {
  width: 100%;
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
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  z-index: 10;
  animation: feedbackAppear 0.3s ease-out;
}

@keyframes feedbackAppear {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
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
  background: rgba(245, 101, 101, 0.2);
  color: #f56565;
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

/* 注册动画区域 */
.register-animation {
  position: absolute;
  top: 50%;
  left: calc(50% + 300px);
  transform: translateY(-50%);
  width: 150px;
  height: 100px;
  opacity: 0;
  transition: opacity 0.8s ease-in;
  pointer-events: none;
  z-index: 4;
}

/* 确保小车在fade-in后保持可见 */
.register-animation.fade-in {
  opacity: 1 !important;
}

.car-animation {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .register-container {
    flex-direction: column;
    padding: 10px;
  }
  
  .register-animation {
    position: relative;
    left: auto;
    top: auto;
    transform: none;
    margin: 30px 0;
    width: 100%;
    height: auto;
  }
  
  .car-animation {
    width: 150px;
    height: 90px;
    margin: 0 auto;
  }
  
  .register-form-wrapper {
    padding: 30px 20px;
  }
  
  .register-title {
    font-size: 20px;
  }
}
</style>