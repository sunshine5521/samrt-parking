<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-title">智能停车管理系统</div>
      <el-form :model="loginForm" label-width="0" class="login-form">
        <el-form-item prop="username">
          <div class="input-group">
            <i class="el-icon-user"></i>
            <el-input v-model="loginForm.username" placeholder="用户名" class="login-input"></el-input>
          </div>
        </el-form-item>
        <el-form-item prop="password">
          <div class="input-group">
            <i class="el-icon-lock"></i>
            <el-input type="password" v-model="loginForm.password" placeholder="密码" class="login-input"></el-input>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" class="login-button">登录</el-button>
        </el-form-item>
        <el-form-item class="register-link">
          <span>还没有账号？</span>
          <el-button type="text" @click="$router.push('/register')">立即注册</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="login-animation">
      <div class="car-animation"></div>
    </div>
  </div>
</template>

<script>
// 补充组件名称（多单词命名，符合ESLint规则）
export default {
  name: 'LoginForm'
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
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  top: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite;
}

.login-container::after {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  bottom: -50px;
  right: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(50px, 50px) scale(1.1);
  }
}

.login-form-wrapper {
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

.login-title {
  text-align: center;
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #667eea;
}

.login-form {
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

.login-input {
  border: none;
  background: transparent;
  padding: 15px 20px 15px 55px;
  border-radius: 30px;
  font-size: 16px;
  width: 100%;
  color: #333;
}

.login-input:focus {
  outline: none;
  box-shadow: none;
}

.login-button {
  width: 100%;
  height: 50px;
  border-radius: 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.login-button:active {
  transform: translateY(0);
}

.register-link {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-link span {
  margin-right: 10px;
}

.register-link .el-button {
  color: #667eea;
  font-weight: bold;
  padding: 0;
}

.register-link .el-button:hover {
  color: #764ba2;
  text-decoration: underline;
}
</style>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const loginForm = ref({
  username: '',
  password: ''
})
const router = useRouter()

const login = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm.value)
    })
    const data = await response.json()
    if (data.code === 200) {
      localStorage.setItem('token', data.data.token)
      localStorage.setItem('user_id', data.data.user_id)
      localStorage.setItem('role', data.data.role || 'user')
      ElMessage.success('登录成功')
      router.push('/parking-lots')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('网络错误，请重试')
  }
}
</script>
