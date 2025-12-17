<template>
  <div class="user-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddUserDialog = true">添加用户</el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="users"
        style="width: 100%"
        :row-key="row => row.id"
      >
        <el-table-column prop="id" label="用户ID" width="80" align="center" />
        <el-table-column prop="username" label="用户名" width="120" align="center" />
        <el-table-column prop="role" label="用户角色" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'warning' : 'success'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editUser(scope.row)">
              编辑
            </el-button>
            <el-button 
              :type="scope.row.role === 'admin' ? 'danger' : 'warning'" 
              size="small" 
              @click="toggleRole(scope.row)"
              :disabled="scope.row.id === 1"
            >
              {{ scope.row.role === 'admin' ? '降级为用户' : '升级为管理员' }}
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteUser(scope.row.id)"
              :disabled="scope.row.id === 1"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="users.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 添加/编辑用户对话框 -->
      <el-dialog v-model="showAddUserDialog" :title="editingId ? '编辑用户' : '添加用户'" width="500px">
        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="formData.username" placeholder="请输入用户名" />
          </el-form-item>

          <el-form-item label="密码" prop="password" v-if="!editingId">
            <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword" v-if="!editingId">
            <el-input v-model="formData.confirmPassword" type="password" placeholder="请确认密码" show-password />
          </el-form-item>

          <el-form-item label="用户角色" prop="role">
            <el-select v-model="formData.role" placeholder="请选择用户角色">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showAddUserDialog = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确认</el-button>
          </div>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 表格数据
const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单数据
const showAddUserDialog = ref(false)
const formRef = ref(null)
const editingId = ref(null)
const formData = ref({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user'
})

// 表单验证规则
const formRules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== formData.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'blur' }
  ]
})

// 页面挂载时获取数据
onMounted(() => {
  fetchUsers()
})

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  const token = localStorage.getItem('token')
  const params = new URLSearchParams()
  params.append('page', currentPage.value)
  params.append('page_size', pageSize.value)

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/users?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取用户列表失败')
    }

    const data = await response.json()
    users.value = data.data
    total.value = data.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchUsers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUsers()
}

// 编辑用户
const editUser = (user) => {
  editingId.value = user.id
  formData.value = {
    username: user.username,
    password: '',
    confirmPassword: '',
    role: user.role
  }
  showAddUserDialog.value = true
}

// 提交表单
const submitForm = () => {
  if (!formRef.value) return

  formRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = editingId.value
        ? `http://127.0.0.1:5000/api/admin/users/${editingId.value}`
        : 'http://127.0.0.1:5000/api/admin/users'
      const method = editingId.value ? 'PUT' : 'POST'

      // 如果是编辑用户且没有输入新密码，则不包含密码字段
      const requestData = {
        username: formData.value.username,
        role: formData.value.role
      }

      if (!editingId.value || formData.value.password) {
        requestData.password = formData.value.password
      }

      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(editingId.value ? '更新失败' : '添加失败')
          }
          return response.json()
        })
        .then(() => {
          ElMessage.success(editingId.value ? '更新成功' : '添加成功')
          showAddUserDialog.value = false
          fetchUsers()
          resetForm()
        })
        .catch(error => {
          console.error(editingId.value ? '更新失败:' : '添加失败:', error)
          ElMessage.error(editingId.value ? '更新失败，请重试' : '添加失败，请重试')
        })
    }
  })
}

// 切换用户角色
const toggleRole = async (user) => {
  const token = localStorage.getItem('token')
  const newRole = user.role === 'admin' ? 'user' : 'admin'

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/users/${user.id}/role`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ role: newRole })
    })

    if (!response.ok) {
      throw new Error('角色切换失败')
    }

    ElMessage.success('角色切换成功')
    user.role = newRole
  } catch (error) {
    console.error('角色切换失败:', error)
    ElMessage.error('角色切换失败，请重试')
  }
}

// 删除用户
const deleteUser = async (id) => {
  const token = localStorage.getItem('token')

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/users/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('删除失败')
    }

    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败，请重试')
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  editingId.value = null
  formData.value = {
    username: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  }
}
</script>

<style scoped>
.user-management {
  padding: 0;
}

.management-card {
  height: calc(100vh - 100px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>