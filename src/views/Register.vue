<template>
  <div style="max-width: 400px; margin: 100px auto;">
    <el-form :model="registerForm" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="registerForm.username"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input type="password" v-model="registerForm.password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input type="password" v-model="registerForm.confirmPassword"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="register">注册</el-button>
      </el-form-item>
    </el-form>
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
/* 可选：添加组件样式 */
</style>