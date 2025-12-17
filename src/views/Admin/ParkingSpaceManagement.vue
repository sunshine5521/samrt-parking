<template>
  <div class="parking-space-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>停车场车位管理</span>
          <div class="header-actions">
            <el-select v-model="selectedParkingLot" placeholder="选择停车场" @change="handleParkingLotChange">
              <el-option
                v-for="lot in parkingLots"
                :key="lot.id"
                :label="lot.name"
                :value="lot"
              />
            </el-select>
            <el-button type="primary" @click="showAddSpaceDialog = true" :disabled="!selectedParkingLot">添加车位</el-button>
            <el-button type="primary" @click="generateSpacesDialog = true" :disabled="!selectedParkingLot">批量生成车位</el-button>
          </div>
        </div>
      </template>

      <div class="parking-info" v-if="selectedParkingLot">
        <div class="info-item">
          <span class="info-label">停车场名称：</span>
          <span class="info-value">{{ selectedParkingLot.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">总车位数：</span>
          <span class="info-value">{{ selectedParkingLot.total_spaces }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">可用车位数：</span>
          <span class="info-value">{{ selectedParkingLot.available_spaces }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">当前车位数量：</span>
          <span class="info-value">{{ parkingSpaces.length }}</span>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="parkingSpaces"
        style="width: 100%"
        :row-key="row => row.id"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="space_number" label="车位编号" width="120" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getSpaceStatusType(scope.row.status)">
              {{ getSpaceStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editSpace(scope.row)">
              编辑
            </el-button>
            <el-button 
              :type="scope.row.status === 'free' ? 'warning' : 'success'" 
              size="small" 
              @click="toggleSpaceStatus(scope.row)"
            >
              {{ scope.row.status === 'free' ? '占用' : '释放' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteSpace(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="parkingSpaces.length > 0">
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

      <!-- 添加/编辑车位对话框 -->
      <el-dialog v-model="showAddSpaceDialog" title="车位管理" width="400px">
        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
          <el-form-item label="车位编号" prop="space_number">
            <el-input v-model="formData.space_number" placeholder="请输入车位编号" />
          </el-form-item>

          <el-form-item label="状态" prop="status">
            <el-select v-model="formData.status" placeholder="请选择状态">
              <el-option label="空闲" value="free" />
              <el-option label="已预约" value="booked" />
              <el-option label="已占用" value="occupied" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="showAddSpaceDialog = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确认</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 批量生成车位对话框 -->
      <el-dialog v-model="generateSpacesDialog" title="批量生成车位" width="400px">
        <el-form ref="generateFormRef" :model="generateForm" :rules="generateFormRules" label-width="120px">
          <el-form-item label="起始编号" prop="startNumber">
            <el-input v-model="generateForm.startNumber" placeholder="例如：A001" />
          </el-form-item>

          <el-form-item label="生成数量" prop="count">
            <el-input-number v-model="generateForm.count" :min="1" :max="100" placeholder="请输入生成数量" />
          </el-form-item>

          <el-form-item label="车位状态" prop="status">
            <el-select v-model="generateForm.status" placeholder="请选择状态">
              <el-option label="空闲" value="free" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="generateSpacesDialog = false">取消</el-button>
            <el-button type="primary" @click="generateSpaces">生成</el-button>
          </div>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 停车场列表
const parkingLots = ref([])
const selectedParkingLot = ref(null)

// 表格数据
const parkingSpaces = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单数据
const showAddSpaceDialog = ref(false)
const formRef = ref(null)
const editingId = ref(null)
const formData = ref({
  space_number: '',
  status: 'free'
})

// 批量生成表单
const generateSpacesDialog = ref(false)
const generateFormRef = ref(null)
const generateForm = ref({
  startNumber: '',
  count: 10,
  status: 'free'
})

// 表单验证规则
const formRules = ref({
  space_number: [
    { required: true, message: '请输入车位编号', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'blur' }
  ]
})

const generateFormRules = ref({
  startNumber: [
    { required: true, message: '请输入起始编号', trigger: 'blur' }
  ],
  count: [
    { required: true, message: '请输入生成数量', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '生成数量必须在1-100之间', trigger: 'blur' }
  ]
})

// 页面挂载时获取数据
onMounted(() => {
  fetchParkingLots()
})

// 获取停车场列表
const fetchParkingLots = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/parking/lots', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取停车场列表失败')
    }

    const data = await response.json()
    parkingLots.value = data.data
  } catch (error) {
    console.error('获取停车场列表失败:', error)
    ElMessage.error('获取停车场列表失败，请重试')
  }
}

// 获取车位列表
const fetchParkingSpaces = async () => {
  if (!selectedParkingLot.value) return

  loading.value = true
  const token = localStorage.getItem('token')
  const params = new URLSearchParams()
  params.append('page', currentPage.value)
  params.append('page_size', pageSize.value)

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces?lot_id=${selectedParkingLot.value.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取车位列表失败')
    }

    const data = await response.json()
    parkingSpaces.value = data.data
    total.value = data.total
  } catch (error) {
    console.error('获取车位列表失败:', error)
    ElMessage.error('获取车位列表失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchParkingSpaces()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchParkingSpaces()
}

// 停车场选择变化
const handleParkingLotChange = () => {
  currentPage.value = 1
  fetchParkingSpaces()
}

// 编辑车位
const editSpace = (space) => {
  editingId.value = space.id
  formData.value = {
    space_number: space.space_number,
    status: space.status
  }
  showAddSpaceDialog.value = true
}

// 提交表单
const submitForm = () => {
  if (!formRef.value) return

  formRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = editingId.value
        ? `http://127.0.0.1:5000/api/parking/spaces/${editingId.value}`
        : 'http://127.0.0.1:5000/api/parking/spaces'
      const method = editingId.value ? 'PUT' : 'POST'

      const requestData = {
        ...formData.value,
        parking_lot_id: selectedParkingLot.value.id
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
          showAddSpaceDialog.value = false
          fetchParkingSpaces()
          resetForm()
        })
        .catch(error => {
          console.error(editingId.value ? '更新失败:' : '添加失败:', error)
          ElMessage.error(editingId.value ? '更新失败，请重试' : '添加失败，请重试')
        })
    }
  })
}

// 批量生成车位
const generateSpaces = () => {
  if (!generateFormRef.value) return

  generateFormRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = 'http://127.0.0.1:5000/api/parking/spaces/batch'

      const requestData = {
        parking_lot_id: selectedParkingLot.value.id,
        start_number: generateForm.value.startNumber,
        count: generateForm.value.count,
        status: generateForm.value.status
      }

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('批量生成失败')
          }
          return response.json()
        })
        .then(() => {
          ElMessage.success('批量生成成功')
          generateSpacesDialog.value = false
          fetchParkingSpaces()
          resetGenerateForm()
        })
        .catch(error => {
          console.error('批量生成失败:', error)
          ElMessage.error('批量生成失败，请重试')
        })
    }
  })
}

// 切换车位状态
const toggleSpaceStatus = async (space) => {
  const token = localStorage.getItem('token')
  const newStatus = space.status === 'free' ? 'occupied' : 'free'

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces/${space.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status: newStatus })
    })

    if (!response.ok) {
      throw new Error('状态更新失败')
    }

    ElMessage.success('状态更新成功')
    space.status = newStatus
    fetchParkingSpaces() // 刷新列表以更新可用车位数
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败，请重试')
  }
}

// 删除车位
const deleteSpace = async (id) => {
  const token = localStorage.getItem('token')

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('删除失败')
    }

    ElMessage.success('删除成功')
    fetchParkingSpaces()
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
    space_number: '',
    status: 'free'
  }
}

const resetGenerateForm = () => {
  generateFormRef.value?.resetFields()
  generateForm.value = {
    startNumber: '',
    count: 10,
    status: 'free'
  }
}

// 获取车位状态类型
const getSpaceStatusType = (status) => {
  const statusMap = {
    free: 'success',
    booked: 'warning',
    occupied: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取车位状态文本
const getSpaceStatusText = (status) => {
  const statusMap = {
    free: '空闲',
    booked: '已预约',
    occupied: '已占用'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.parking-space-management {
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

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.parking-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.info-value {
  font-weight: 600;
  color: #333;
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