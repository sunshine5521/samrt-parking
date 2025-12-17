<template>
  <div class="parking-lot-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>停车场管理</span>
          <el-button type="primary" @click="showAddDialog = true">添加停车场</el-button>
        </div>
      </template>

      <el-table :data="parkingLots" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="停车场名称" />
        <el-table-column prop="location_gps" label="GPS坐标" />
        <el-table-column prop="capacity" label="总车位" />
        <el-table-column prop="available_spaces" label="可用车位" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'open' ? 'success' : 'danger'">
              {{ scope.row.status === 'open' ? '开放' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hourly_rate" label="每小时收费" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editParkingLot(scope.row)">编辑</el-button>
            <el-button type="success" size="small" @click="toggleStatus(scope.row)">
              {{ scope.row.status === 'open' ? '关闭' : '开放' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteParkingLot(scope.row.id)">删除</el-button>
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
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="停车场名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入停车场名称" />
        </el-form-item>

        <el-form-item label="GPS坐标" prop="location_gps">
          <el-input v-model="formData.location_gps" placeholder="格式：纬度,经度" />
        </el-form-item>

        <el-form-item label="总车位" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1" placeholder="请输入总车位数" />
        </el-form-item>

        <el-form-item label="每小时收费" prop="hourly_rate">
          <el-input-number v-model="formData.hourly_rate" :min="0" :step="0.5" placeholder="请输入每小时收费" />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="开放" value="open" />
            <el-option label="关闭" value="closed" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const parkingLots = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框
const dialogVisible = ref(false)
const showAddDialog = ref(false)
const dialogTitle = ref('添加停车场')
const formRef = ref(null)
const editingId = ref(null)

// 表单数据
const formData = ref({
  name: '',
  location_gps: '',
  capacity: null,
  hourly_rate: 0,
  status: 'open'
})

// 表单验证规则
const formRules = ref({
  name: [
    { required: true, message: '请输入停车场名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度应在2-50个字符之间', trigger: 'blur' }
  ],
  location_gps: [
    { required: true, message: '请输入GPS坐标', trigger: 'blur' },
    { pattern: /^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/, message: '请输入正确的GPS坐标格式（纬度,经度）', trigger: 'blur' }
  ],
  capacity: [
    { required: true, message: '请输入总车位数', trigger: 'blur' },
    { type: 'number', min: 1, message: '总车位数必须大于0', trigger: 'blur' }
  ]
})

// 初始化加载数据
onMounted(() => {
  fetchParkingLots()
})

// 获取停车场列表
const fetchParkingLots = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize.value)

    const response = await fetch(`http://127.0.0.1:5000/api/admin/parking-lots?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取停车场列表失败')
    }

    const data = await response.json()
    parkingLots.value = data.data
    total.value = data.total
  } catch (error) {
    console.error('获取停车场列表失败:', error)
    ElMessage.error('获取停车场列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchParkingLots()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchParkingLots()
}

// 显示编辑对话框
const editParkingLot = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑停车场'
  formData.value = {
    name: row.name,
    location_gps: row.location_gps,
    capacity: row.capacity,
    hourly_rate: row.hourly_rate,
    status: row.status
  }
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  editingId.value = null
  formData.value = {
    name: '',
    location_gps: '',
    capacity: null,
    hourly_rate: 0,
    status: 'open'
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  formRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = editingId.value
        ? `http://127.0.0.1:5000/api/admin/parking-lots/${editingId.value}`
        : 'http://127.0.0.1:5000/api/admin/parking-lots'
      const method = editingId.value ? 'PUT' : 'POST'

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
            throw new Error(`${editingId.value ? '更新' : '添加'}停车场失败`)
          }
          return response.json()
        })
        .then(() => {
          ElMessage.success(`${editingId.value ? '更新' : '添加'}停车场成功`)
          dialogVisible.value = false
          fetchParkingLots()
          resetForm()
        })
        .catch(error => {
          console.error(`${editingId.value ? '更新' : '添加'}停车场失败:`, error)
          ElMessage.error(`${editingId.value ? '更新' : '添加'}停车场失败，请重试`)
        })
    }
  })
}

// 切换停车场状态
const toggleStatus = async (row) => {
  const token = localStorage.getItem('token')
  const newStatus = row.status === 'open' ? 'closed' : 'open'

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/parking-lots/${row.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status: newStatus })
    })

    if (!response.ok) {
      throw new Error('更新停车场状态失败')
    }

    ElMessage.success(`停车场已${newStatus === 'open' ? '开放' : '关闭'}`)
    row.status = newStatus
  } catch (error) {
    console.error('更新停车场状态失败:', error)
    ElMessage.error('更新停车场状态失败，请重试')
  }
}

// 删除停车场
const deleteParkingLot = async (id) => {
  const token = localStorage.getItem('token')

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/parking-lots/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('删除停车场失败')
    }

    ElMessage.success('删除停车场成功')
    fetchParkingLots()
  } catch (error) {
    console.error('删除停车场失败:', error)
    ElMessage.error('删除停车场失败，请重试')
  }
}
</script>

<style scoped>
.parking-lot-management {
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