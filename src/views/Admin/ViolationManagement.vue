<template>
  <div class="violation-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>违规停车管理</span>
          <el-button type="primary" @click="showAddDialog = true">添加违规记录</el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="violations"
        style="width: 100%"
        :row-key="row => row.id"
      >
        <el-table-column prop="id" label="记录ID" width="80" align="center" />
        <el-table-column prop="vehicle_license_plate" label="车牌号" width="120" align="center" />
        <el-table-column prop="parking_lot_name" label="停车场" width="180" align="center" />
        <el-table-column prop="violation_type" label="违规类型" width="120" align="center" />
        <el-table-column prop="violation_time" label="违规时间" width="180" align="center" />
        <el-table-column prop="fine_amount" label="罚款金额(元)" width="120" align="center" />
        <el-table-column prop="status" label="处理状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'paid' ? 'success' : 'danger'">
              {{ scope.row.status === 'paid' ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="违规描述" min-width="200" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="editViolation(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteViolation(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
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
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" title="违规记录" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="车牌号" prop="vehicle_license_plate">
          <el-input v-model="formData.vehicle_license_plate" placeholder="请输入车牌号" />
        </el-form-item>

        <el-form-item label="停车场" prop="parking_lot_id">
          <el-select v-model="formData.parking_lot_id" placeholder="请选择停车场">
            <el-option
              v-for="lot in parkingLots"
              :key="lot.id"
              :label="lot.name"
              :value="lot.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="违规类型" prop="violation_type">
          <el-select v-model="formData.violation_type" placeholder="请选择违规类型">
            <el-option label="超时停车" value="超时停车" />
            <el-option label="未支付费用" value="未支付费用" />
            <el-option label="违规停车" value="违规停车" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>

        <el-form-item label="违规时间" prop="violation_time">
          <el-date-picker
            v-model="formData.violation_time"
            type="datetime"
            placeholder="选择日期时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="罚款金额" prop="fine_amount">
          <el-input-number
            v-model="formData.fine_amount"
            :min="0"
            :precision="2"
            style="width: 100%"
            placeholder="请输入罚款金额"
          />
        </el-form-item>

        <el-form-item label="违规描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            rows="3"
            placeholder="请输入违规描述"
          />
        </el-form-item>

        <el-form-item label="处理状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="未处理" value="unpaid" />
            <el-option label="已处理" value="paid" />
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

// 表格数据
const violations = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表单数据
const dialogVisible = ref(false)
const formRef = ref(null)
const editingId = ref(null)
const formData = ref({
  vehicle_license_plate: '',
  parking_lot_id: null,
  violation_type: '',
  violation_time: '',
  fine_amount: 0,
  description: '',
  status: 'unpaid'
})

// 停车场列表
const parkingLots = ref([])

// 表单验证规则
const formRules = ref({
  vehicle_license_plate: [
    { required: true, message: '请输入车牌号', trigger: 'blur' }
  ],
  parking_lot_id: [
    { required: true, message: '请选择停车场', trigger: 'blur' }
  ],
  violation_type: [
    { required: true, message: '请选择违规类型', trigger: 'blur' }
  ],
  violation_time: [
    { required: true, message: '请选择违规时间', trigger: 'blur' }
  ],
  fine_amount: [
    { required: true, message: '请输入罚款金额', trigger: 'blur' },
    { type: 'number', min: 0, message: '罚款金额必须大于等于0', trigger: 'blur' }
  ]
})

// 页面挂载时获取数据
onMounted(() => {
  fetchParkingLots()
  fetchViolations()
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

// 获取违规记录
const fetchViolations = async () => {
  loading.value = true
  const token = localStorage.getItem('token')
  const params = new URLSearchParams()
  params.append('page', currentPage.value)
  params.append('page_size', pageSize.value)

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/admin/violations?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error('获取违规记录失败')
    }

    const data = await response.json()
    violations.value = data.data || []
    total.value = data.total || 0
  } catch (error) {
    console.error('获取违规记录失败:', error)
    ElMessage.error('获取违规记录失败，请重试')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchViolations()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchViolations()
}

// 编辑违规记录
const editViolation = (violation) => {
  editingId.value = violation.id
  formData.value = {
    vehicle_license_plate: violation.vehicle_license_plate,
    parking_lot_id: violation.parking_lot_id,
    violation_type: violation.violation_type,
    violation_time: new Date(violation.violation_time),
    fine_amount: violation.fine_amount,
    description: violation.description,
    status: violation.status
  }
  dialogVisible.value = true
}

// 提交表单
const submitForm = () => {
  if (!formRef.value) return

  formRef.value.validate((valid) => {
    if (valid) {
      const token = localStorage.getItem('token')
      const url = editingId.value
        ? `http://127.0.0.1:5000/api/violations/${editingId.value}`
        : 'http://127.0.0.1:5000/api/violations'
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
            throw new Error(editingId.value ? '更新失败' : '添加失败')
          }
          return response.json()
        })
        .then(() => {
          ElMessage.success(editingId.value ? '更新成功' : '添加成功')
          dialogVisible.value = false
          fetchViolations()
          resetForm()
        })
        .catch(error => {
          console.error(editingId.value ? '更新失败:' : '添加失败:', error)
          ElMessage.error(editingId.value ? '更新失败，请重试' : '添加失败，请重试')
        })
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  editingId.value = null
  formData.value = {
    vehicle_license_plate: '',
    parking_lot_id: null,
    violation_type: '',
    violation_time: '',
    fine_amount: 0,
    description: '',
    status: 'unpaid'
  }
}

// 删除违规记录
const deleteViolation = async (id) => {
  const token = localStorage.getItem('token')

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/violations/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('删除失败')
    }

    ElMessage.success('删除成功')
    fetchViolations()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败，请重试')
  }
}
</script>

<style scoped>
.violation-management {
  padding: 20px;
}

.management-card {
  height: 100%;
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