<template>
  <div class="reservation-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>预约记录管理</span>
        </div>
      </template>

      <div class="filter-container">
        <el-select v-model="statusFilter" placeholder="状态" size="small" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="已预约" value="booked" />
          <el-option label="已使用" value="used" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          @change="handleSearch"
        />
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索车牌号或用户名" 
          size="small" 
          clearable
          @keyup.enter="handleSearch"
          style="width: 240px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="small" @click="handleSearch">搜索</el-button>
        <el-button type="default" size="small" @click="resetSearch">重置</el-button>
      </div>

      <el-table 
        :data="reservations" 
        border 
        stripe 
        style="width: 100%" 
        v-loading="loading"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="parking_lot_name" label="停车场名称" width="180" />
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag 
              :type="getStatusTagType(scope.row.status)"
              size="large"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'booked'"
              type="warning" 
              size="small" 
              @click="cancelReservation(scope.row.id)"
            >
              取消
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="viewDetails(scope.row)"
            >
              详情
            </el-button>
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

      <!-- 详情对话框 -->
      <el-dialog
        title="预约记录详情"
        v-model="detailDialogVisible"
        width="600px"
      >
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="停车场名称">{{ selectedRecord.parking_lot_name }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">{{ selectedRecord.license_plate }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedRecord.username }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ selectedRecord.start_time }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ selectedRecord.end_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedRecord.status) }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const reservations = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const statusFilter = ref('')
const dateRange = ref([])

// 详情对话框
const detailDialogVisible = ref(false)
const selectedRecord = ref({})

// 页面挂载时获取数据
onMounted(() => {
  fetchReservations()
})

// 获取预约记录
const fetchReservations = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    params.append('page', currentPage.value)
    params.append('page_size', pageSize.value)
    
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value)
    }
    
    if (statusFilter.value) {
      params.append('status', statusFilter.value)
    }
    
    if (dateRange.value.length === 2) {
      params.append('start_date', dateRange.value[0].toISOString())
      params.append('end_date', dateRange.value[1].toISOString())
    }

    const response = await fetch(`http://127.0.0.1:5000/api/admin/reservations?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取预约记录失败')
    }

    const data = await response.json()
    reservations.value = data.data || []
    total.value = data.total || 0
    
    ElMessage.success('获取预约记录成功')
  } catch (error) {
    console.error('获取预约记录失败:', error)
    ElMessage.error('获取预约记录失败，请重试')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
  fetchReservations()
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  dateRange.value = []
  currentPage.value = 1
  fetchReservations()
}

// 分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchReservations()
}

// 当前页变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchReservations()
}

// 查看详情
const viewDetails = (record) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
}

// 取消预约
const cancelReservation = async (reservationId) => {
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch(`http://127.0.0.1:5000/api/reservation/${reservationId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('取消预约失败')
    }
    
    ElMessage.success('取消预约成功')
    fetchReservations()
  } catch (error) {
    console.error('取消预约失败:', error)
    ElMessage.error('取消预约失败，请重试')
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'booked': return 'info'
    case 'used': return 'success'
    case 'cancelled': return 'danger'
    default: return 'warning'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'booked': return '已预约'
    case 'used': return '已使用'
    case 'cancelled': return '已取消'
    default: return status
  }
}
</script>

<style scoped>
.reservation-management {
  padding: 0;
}

.management-card {
  height: calc(100vh - 100px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}
</style>