<template>
  <div class="parking-records-management">
    <el-card class="management-card">
      <template #header>
        <div class="card-header">
          <span>停车记录管理</span>
          <div class="filter-container">
            <el-select v-model="statusFilter" placeholder="状态" size="small" @change="handleSearch">
              <el-option label="全部" value="" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
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
              placeholder="搜索车牌号或停车场名称" 
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
        </div>
      </template>

      <!-- 数据统计 -->
      <div class="stats-container">
        <el-card class="stat-item">
          <div class="stat-content">
            <div class="stat-label">总记录数</div>
            <div class="stat-value">{{ totalRecords }}</div>
          </div>
        </el-card>
        <el-card class="stat-item success">
          <div class="stat-content">
            <div class="stat-label">已完成</div>
            <div class="stat-value">{{ completedRecords }}</div>
          </div>
        </el-card>
        <el-card class="stat-item warning">
          <div class="stat-content">
            <div class="stat-label">进行中</div>
            <div class="stat-value">{{ inProgressRecords }}</div>
          </div>
        </el-card>
        <el-card class="stat-item danger">
          <div class="stat-content">
            <div class="stat-label">已取消</div>
            <div class="stat-value">{{ cancelledRecords }}</div>
          </div>
        </el-card>
      </div>

      <!-- 停车记录表格 -->
      <el-table 
        :data="filteredRecords" 
        border 
        stripe 
        style="width: 100%"
        v-loading="loading"
        :header-cell-style="headerCellStyle"
      >
        <el-table-column prop="id" label="记录ID" width="100" align="center" />
        <el-table-column prop="parking_lot_name" label="停车场名称" min-width="180" />
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template #default="scope">
            {{ scope.row.end_time ? formatDate(scope.row.end_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="停车时长" width="120" align="center">
          <template #default="scope">
            {{ scope.row.duration ? scope.row.duration + '小时' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="费用" width="100" align="right">
          <template #default="scope">
            <span class="cost-text">¥{{ scope.row.cost || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag 
              :type="getStatusTagType(scope.row.status)"
              size="large"
              effect="dark"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'in_progress'"
              type="primary" 
              size="small" 
              @click="completeParking(scope.row.id)"
            >
              结束停车
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
        title="停车记录详情"
        v-model="detailDialogVisible"
        width="600px"
      >
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="停车场名称">{{ selectedRecord.parking_lot_name }}</el-descriptions-item>
          <el-descriptions-item label="车牌号">{{ selectedRecord.license_plate }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ selectedRecord.user_id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedRecord.username }}</el-descriptions-item>
          <el-descriptions-item label="车位ID">{{ selectedRecord.parking_space_id }}</el-descriptions-item>
          <el-descriptions-item label="车位编号">{{ selectedRecord.space_number }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(selectedRecord.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ selectedRecord.end_time ? formatDate(selectedRecord.end_time) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="停车时长">{{ selectedRecord.duration ? selectedRecord.duration + '小时' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="费用">{{ selectedRecord.cost ? '¥' + selectedRecord.cost : '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(selectedRecord.status) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedRecord.created_at ? formatDate(selectedRecord.created_at) : '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const parkingRecords = ref([])
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

// 表格头部样式
const headerCellStyle = {
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  fontWeight: '600',
  fontSize: '14px',
  height: '50px',
  textAlign: 'center'
}

// 数据统计
const totalRecords = computed(() => parkingRecords.value.length)
const completedRecords = computed(() => parkingRecords.value.filter(record => record.status === 'completed').length)
const inProgressRecords = computed(() => parkingRecords.value.filter(record => record.status === 'in_progress').length)
const cancelledRecords = computed(() => parkingRecords.value.filter(record => record.status === 'cancelled').length)

// 过滤后的记录
const filteredRecords = computed(() => {
  let result = [...parkingRecords.value]
  
  // 应用搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(record => 
      record.license_plate.toLowerCase().includes(keyword) ||
      record.parking_lot_name.toLowerCase().includes(keyword)
    )
  }
  
  // 应用状态过滤
  if (statusFilter.value) {
    result = result.filter(record => record.status === statusFilter.value)
  }
  
  // 应用日期范围过滤
  if (dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)
    
    result = result.filter(record => {
      const recordDate = new Date(record.start_time)
      return recordDate >= startDate && recordDate <= endDate
    })
  }
  
  return result
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'in_progress': return 'warning'
    case 'cancelled': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'in_progress': return '进行中'
    case 'cancelled': return '已取消'
    default: return status
  }
}

// 获取停车记录
const fetchParkingRecords = async () => {
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

    const response = await fetch(`http://127.0.0.1:5000/api/admin/parking-records?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取停车记录失败')
    }

    const data = await response.json()
    parkingRecords.value = data.data
    total.value = data.total
    
    ElMessage.success('获取停车记录成功')
  } catch (error) {
    console.error('获取停车记录失败:', error)
    ElMessage.error('获取停车记录失败，请重试')
    // 使用模拟数据
    useMockData()
  } finally {
    loading.value = false
  }
}

// 使用模拟数据
const useMockData = () => {
  parkingRecords.value = [
    { 
      id: 1, 
      parking_lot_name: '中央停车场', 
      license_plate: '京A12345', 
      username: '张三',
      user_id: 1,
      parking_space_id: 1,
      space_number: 'A001',
      start_time: '2024-05-20T08:30:00', 
      end_time: '2024-05-20T12:45:00', 
      duration: 4.25, 
      cost: '40.5', 
      status: 'completed',
      created_at: '2024-05-20T08:30:00'
    },
    { 
      id: 2, 
      parking_lot_name: '商业中心停车场', 
      license_plate: '沪B67890', 
      username: '李四',
      user_id: 2,
      parking_space_id: 2,
      space_number: 'B002',
      start_time: '2024-05-20T09:15:00', 
      end_time: null, 
      duration: null, 
      cost: '0', 
      status: 'in_progress',
      created_at: '2024-05-20T09:15:00'
    },
    { 
      id: 3, 
      parking_lot_name: '地铁口停车场', 
      license_plate: '粤C24680', 
      username: '王五',
      user_id: 3,
      parking_space_id: 3,
      space_number: 'C003',
      start_time: '2024-05-20T10:00:00', 
      end_time: '2024-05-20T13:45:00', 
      duration: 3.75, 
      cost: '37.5', 
      status: 'completed',
      created_at: '2024-05-20T10:00:00'
    }
  ]
  
  total.value = 150
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
  fetchParkingRecords()
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  dateRange.value = []
  currentPage.value = 1
  fetchParkingRecords()
}

// 分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchParkingRecords()
}

// 当前页变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchParkingRecords()
}

// 查看详情
const viewDetails = (record) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
}

// 结束停车
const completeParking = async (recordId) => {
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch(`http://127.0.0.1:5000/api/admin/parking-records/${recordId}/complete`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('结束停车失败')
    }
    
    ElMessage.success('结束停车成功')
    // 刷新数据
    fetchParkingRecords()
  } catch (error) {
    console.error('结束停车失败:', error)
    ElMessage.error('结束停车失败，请重试')
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchParkingRecords()
})
</script>

<style scoped>
.parking-records-management {
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
}

.stats-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-item {
  flex: 1;
  min-width: 180px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  text-align: center;
  padding: 20px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.cost-text {
  font-weight: bold;
  color: #E53935;
}

@media (max-width: 1200px) {
  .filter-container {
    flex-wrap: wrap;
  }
  
  .stats-container {
    justify-content: center;
  }
  
  .stat-item {
    min-width: 150px;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-container {
    flex-direction: column;
  }
  
  .stat-item {
    min-width: 100%;
  }
}
</style>