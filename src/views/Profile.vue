<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="userInfo"
        :rules="rules"
        label-width="100px"
        class="profile-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userInfo.username" readonly />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userInfo.email" />
        </el-form-item>
        
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="userInfo.phone" />
        </el-form-item>
        
        <el-form-item label="注册时间">
          <el-input v-model="userInfo.created_at" readonly />
        </el-form-item>
        
        <el-form-item label="上次登录">
          <el-input v-model="userInfo.last_login" readonly />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存修改</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>

      <div class="password-section">
        <h3>修改密码</h3>
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          class="password-form"
        >
          <el-form-item label="当前密码" prop="currentPassword">
            <el-input v-model="passwordForm.currentPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handlePasswordChange">修改密码</el-button>
            <el-button @click="resetPasswordForm">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      userInfo: {
        username: '',
        email: '',
        phone: '',
        created_at: '',
        last_login: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号码', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码格式', trigger: 'blur' }
        ]
      },
      passwordRules: {
        currentPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (value !== this.passwordForm.newPassword) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ]
      }
    }
  },
  mounted() {
    this.fetchUserInfo()
  },
  methods: {
    fetchUserInfo() {
      const token = localStorage.getItem('token')
      
      fetch('http://127.0.0.1:5000/api/user/profile', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('获取用户信息失败')
          }
          return response.json()
        })
        .then(data => {
          this.userInfo = data
        })
        .catch(error => {
          console.error('获取用户信息失败:', error)
          this.$message.error('获取用户信息失败，请重试')
        })
    },
    
    handleSubmit() {
      this.$refs.formRef.validate((valid) => {
        if (valid) {
          const token = localStorage.getItem('token')
          
          fetch('http://127.0.0.1:5000/api/user/profile', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              email: this.userInfo.email,
              phone: this.userInfo.phone
            })
          })
            .then(response => {
              if (!response.ok) {
                throw new Error('更新用户信息失败')
              }
              return response.json()
            })
            .then(data => {
              this.$message.success('用户信息更新成功')
              this.userInfo = data
            })
            .catch(error => {
              console.error('更新用户信息失败:', error)
              this.$message.error('更新用户信息失败，请重试')
            })
        }
      })
    },
    
    handleCancel() {
      this.fetchUserInfo()
      this.$refs.formRef.resetFields()
    },
    
    handlePasswordChange() {
      this.$refs.passwordFormRef.validate((valid) => {
        if (valid) {
          const token = localStorage.getItem('token')
          
          fetch('http://127.0.0.1:5000/api/user/change-password', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              current_password: this.passwordForm.currentPassword,
              new_password: this.passwordForm.newPassword
            })
          })
            .then(response => {
              if (!response.ok) {
                throw new Error('修改密码失败')
              }
              return response.json()
            })
            .then(() => {
              this.$message.success('密码修改成功，请重新登录')
              this.resetPasswordForm()
              // 可以选择让用户重新登录
              // localStorage.removeItem('token')
              // this.$router.push('/login')
            })
            .catch(error => {
              console.error('修改密码失败:', error)
              this.$message.error('修改密码失败，请检查当前密码是否正确')
            })
        }
      })
    },
    
    resetPasswordForm() {
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      this.$refs.passwordFormRef.resetFields()
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.profile-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-form {
  margin-bottom: 30px;
}

.password-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.password-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.password-form {
  width: 100%;
}
</style>