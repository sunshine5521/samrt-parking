<template>
  <div class="register-container">
    <div class="register-form-wrapper">
      <div class="register-title">智能停车管理系统</div>
      <el-form :model="registerForm" label-width="0" class="register-form">
        <el-form-item prop="username">
          <div class="input-group">
            <i class="el-icon-user"></i>
            <el-input v-model="registerForm.username" placeholder="用户名" class="register-input"></el-input>
          </div>
        </el-form-item>
        <el-form-item prop="password">
          <div class="input-group">
            <i class="el-icon-lock"></i>
            <el-input type="password" v-model="registerForm.password" placeholder="密码" class="register-input"></el-input>
          </div>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <div class="input-group">
            <i class="el-icon-lock"></i>
            <el-input type="password" v-model="registerForm.confirmPassword" placeholder="确认密码" class="register-input"></el-input>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register" class="register-button">注册</el-button>
        </el-form-item>
        <el-form-item class="login-link">
          <span>已经有账号？</span>
          <el-button type="text" @click="$router.push('/login')">立即登录</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="register-animation">
      <div class="car-animation"></div>
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
import { ElMessage, ElForm, ElFormItem, ElInput, ElButton } from 'element-plus'
import { useRouter } from 'vue-router'

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})
const router = useRouter()

const register = async () => {
  // 去掉前后空格再比较
  if (registerForm.value.password.trim() !== registerForm.value.confirmPassword.trim()) {
    ElMessage.error('两次密码不一致')
    return
  }
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
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('网络错误，请重试')
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-container::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  top: -100px;
  right: -100px;
  animation: float 9s ease-in-out infinite;
}

.register-container::after {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  bottom: -50px;
  left: -50px;
  animation: float 7s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(40px, 40px) scale(1.05);
  }
}

.register-form-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
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

.register-title {
  text-align: center;
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f5576c;
}

.register-form {
  width: 100%;
}

.input-group {
  position: relative;
  margin-bottom: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 30px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.input-group:hover, .input-group:focus-within {
  border-color: #f5576c;
  box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.1);
  background: #fff;
}

.input-group i {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 18px;
}

.register-input {
  border: none;
  background: transparent;
  padding: 15px 20px 15px 55px;
  border-radius: 30px;
  font-size: 16px;
  width: 100%;
  color: #333;
}

.register-input:focus {
  outline: none;
  box-shadow: none;
}

.register-button {
  width: 100%;
  height: 50px;
  border-radius: 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(245, 87, 108, 0.4);
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
}

.register-button:active {
  transform: translateY(0);
}

.login-link {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-link span {
  margin-right: 10px;
}

.login-link .el-button {
  color: #f5576c;
  font-weight: bold;
  padding: 0;
}

.login-link .el-button:hover {
  color: #f093fb;
  text-decoration: underline;
}
</style>