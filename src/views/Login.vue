<template>
  <el-form :model="loginForm" label-width="80px" style="max-width: 400px; margin: 100px auto;">
    <el-form-item label="用户名">
      <el-input v-model="loginForm.username"></el-input>
    </el-form-item>
    <el-form-item label="密码">
      <el-input type="password" v-model="loginForm.password"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="login">登录</el-button>
      <el-button @click="$router.push('/register')">注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
// 补充组件名称（多单词命名，符合ESLint规则）
export default {
  name: 'LoginForm'
}
</script>

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
