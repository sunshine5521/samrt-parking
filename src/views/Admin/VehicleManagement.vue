<template>
  <div class="vehicle-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>车辆管理</span>
        </div>
      </template>

      <el-table :data="vehicles" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="license_plate" label="车牌号" />
        <el-table-column prop="brand" label="品牌" />
        <el-table-column prop="color" label="颜色" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editVehicle(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteVehicle(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: right"
      />

      <!-- 编辑对话框 -->
      <el-dialog
        :title="dialogTitle"
        v-model="dialogVisible"
        width="600px"
        @close="resetForm"
      >
        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
          <el-form-item label="车牌号" prop="license_plate">
            <el-input v-model="formData.license_plate" placeholder="请输入车牌号" />
          </el-form-item>

          <el-form-item label="品牌" prop="brand">
            <el-input v-model="formData.brand" placeholder="请输入品牌" />
          </el-form-item>

          <el-form-item label="颜色" prop="color">
            <el-input v-model="formData.color" placeholder="请输入颜色" />
          </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
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

const vehicles = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('编辑车辆')
const formRef = ref(null)
const editingId = ref(null)

// 表单数据
const formData = ref({
  license_plate: '',
  brand: '',
  color: ''
})

// 表单验证规则
const formRules = ref({
  license_plate: [
    { required: true, message: '请输入车牌号', trigger: 'blur' },
    { min: 5, max: 20, message: '车牌号长度应在5-20个字符之间', trigger: 'blur' }
  ],
  brand: [
    { required: true, message: '请输入品牌', trigger: 'blur' }
  ],
  color: [
    { required: true, message: '请输入颜色', trigger: 'blur' }
  ]
})

// 初始化加载数据
onMounted(() => {
  fetchVehicles()
})

// 获取车辆列表
const fetchVehicles = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize.value)

    const response = await fetch(`http://127.0.0.1:5000/api/admin/vehicles?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取车辆列表失败')
    }

    const data = await response.json()
    vehicles.value = data.data
    total.value = data.total || data.data.length
  } catch (error) {
    console.error('获取车辆列表失败:', error)
    ElMessage.error('获取车辆列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchVehicles()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchVehicles()
}

// 显示编辑对话框
const editVehicle = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑车辆'
  formData.value = {
    license_plate: row.license_plate,
    brand: row.brand,
    color: row.color
  }
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  editingId.value = null
  formData.value = {
    license_plate: '',
    brand: '',
    color: ''
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  formRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = `http://127.0.0.1:5000/api/admin/vehicles/${editingId.value}`
      const method = 'PUT'

      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData.value)
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('更新车辆失败')
          }
          return response.json()
        })
        .then(() => {
          ElMessage.success('车辆更新成功')
          dialogVisible.value = false
          fetchVehicles()
          resetForm()
        })
        .catch(error => {
          console.error('更新车辆失败:', error)
          ElMessage.error('更新车辆失败，请重试')
        })
    }
  })
}

// 删除车辆
const deleteVehicle = async (id) => {
  const token = localStorage.getItem('token')

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/vehicles/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('删除车辆失败')
    }

    ElMessage.success('删除车辆成功')
    fetchVehicles()
  } catch (error) {
    console.error('删除车辆失败:', error)
    ElMessage.error('删除车辆失败，请重试')
  }
}
</script>

<style scoped>
.vehicle-management {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>