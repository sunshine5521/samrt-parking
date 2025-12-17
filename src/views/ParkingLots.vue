<template>
  <div class="parking-lots-page">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <h1 class="page-title">停车场列表</h1>
      <div class="page-actions">
        <el-button type="primary" @click="refreshParkingLots">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 搜索和筛选区域 -->
    <div class="search-filter-section">
      <el-card shadow="hover" class="search-card">
        <div class="search-form">
          <el-form :model="searchForm" label-position="left" label-width="80px" inline>
            <el-form-item label="停车场名称">
              <el-input 
                v-model="searchForm.name" 
                placeholder="请输入停车场名称" 
                clearable
                @input="handleSearch"
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="地址">
              <el-input 
                v-model="searchForm.location" 
                placeholder="请输入地址" 
                clearable
                @input="handleSearch"
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Location /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch" class="search-btn">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="resetSearch" class="reset-btn">
                <el-icon><RefreshRight /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </div>
    
    <!-- 停车场统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card total-lots">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Building /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalParkingLots }}</div>
                <div class="stat-label">总停车场</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card total-spaces">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ totalSpaces }}</div>
                <div class="stat-label">总车位数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card available-spaces">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ availableSpaces }}</div>
                <div class="stat-label">空闲车位数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card occupancy-rate">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ occupancyRate }}%</div>
                <div class="stat-label">平均使用率</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 停车场表格 -->
    <div class="table-section">
      <el-card shadow="hover" class="table-card">
        <div class="table-header">
          <div class="table-title">停车场信息</div>
          <div class="table-actions">
            <el-select v-model="sortBy" placeholder="排序" size="small" @change="handleSort">
              <el-option label="空闲车位（升序）" value="available_spaces_asc"></el-option>
              <el-option label="空闲车位（降序）" value="available_spaces_desc"></el-option>
              <el-option label="小时费率（升序）" value="hourly_rate_asc"></el-option>
              <el-option label="小时费率（降序）" value="hourly_rate_desc"></el-option>
            </el-select>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <!-- 无数据状态 -->
        <div v-else-if="filteredParkingLots.length === 0" class="empty-container">
          <el-empty description="暂无停车场数据" :image-size="120">
            <el-button type="primary" @click="refreshParkingLots">重新加载</el-button>
          </el-empty>
        </div>
        
        <!-- 表格内容 -->
        <el-table 
          v-else 
          :data="pagedParkingLots" 
          stripe 
          border 
          style="width: 100%"
          class="parking-table"
          :header-cell-style="headerCellStyle"
          :row-class-name="rowClassName"
          @row-click="rowClick"
        >
          <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
          <el-table-column prop="name" label="名称" min-width="150">
            <template #default="scope">
              <div class="parking-name">{{ scope.row.name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="地址" min-width="200">
            <template #default="scope">
              <div class="parking-location">{{ scope.row.location }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="gps_coordinates" label="GPS坐标" min-width="180"></el-table-column>
          <el-table-column prop="total_spaces" label="总车位" width="100" align="center"></el-table-column>
          <el-table-column prop="hourly_rate" label="小时费率" width="120" align="center">
            <template #default="scope">
              <span class="hourly-rate">¥{{ scope.row.hourly_rate }}/小时</span>
            </template>
          </el-table-column>
          <el-table-column prop="available_spaces" label="空闲车位" width="120" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.available_spaces > 0 ? 'success' : 'danger'"
                size="large"
                effect="dark"
              >
                {{ scope.row.available_spaces }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center">
            <template #default="scope">
              <el-button 
                type="primary" 
                @click="viewSpace(scope.row.id)"
                size="small"
                :disabled="scope.row.available_spaces === 0"
              >
                查看车位
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <div v-if="!loading && filteredParkingLots.length > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredParkingLots.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElTable, ElTableColumn, ElButton, ElCard, ElRow, ElCol, ElInput, ElForm, ElFormItem, ElSelect, ElOption, ElTag, ElEmpty, ElSkeleton, ElPagination } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Refresh, Search, Location, RefreshRight, Building, Van, CircleCheck, TrendCharts
} from '@element-plus/icons-vue'

const parkingLots = ref([])
const router = useRouter()
const loading = ref(false)

// 搜索表单
const searchForm = ref({
  name: '',
  location: ''
})

// 分页配置
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('')

// 计算过滤后的停车场列表
const filteredParkingLots = computed(() => {
  let result = [...parkingLots.value]
  
  // 应用搜索过滤
  if (searchForm.value.name) {
    result = result.filter(lot => 
      lot.name.toLowerCase().includes(searchForm.value.name.toLowerCase())
    )
  }
  if (searchForm.value.location) {
    result = result.filter(lot => 
      lot.location.toLowerCase().includes(searchForm.value.location.toLowerCase())
    )
  }
  
  // 应用排序
  if (sortBy.value) {
    const [field, order] = sortBy.value.split('_')
    result.sort((a, b) => {
      const aVal = a[field]
      const bVal = b[field]
      if (order === 'asc') {
        return aVal - bVal
      } else {
        return bVal - aVal
      }
    })
  }
  
  return result
})

// 计算分页后的停车场列表
const pagedParkingLots = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredParkingLots.value.slice(startIndex, endIndex)
})

// 统计数据
const totalParkingLots = computed(() => parkingLots.value.length)
const totalSpaces = computed(() => {
  return parkingLots.value.reduce((sum, lot) => sum + lot.total_spaces, 0)
})
const availableSpaces = computed(() => {
  return parkingLots.value.reduce((sum, lot) => sum + lot.available_spaces, 0)
})
const occupancyRate = computed(() => {
  const total = totalSpaces.value
  if (total === 0) return 0
  const occupied = total - availableSpaces.value
  return Math.round((occupied / total) * 100)
})

// 表格头部样式
const headerCellStyle = {
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  fontWeight: '600',
  fontSize: '14px',
  height: '50px',
  textAlign: 'center'
}

// 行样式类
const rowClassName = ({ row }) => {
  return row.available_spaces === 0 ? 'parking-lot-full' : ''
}

// 获取停车场数据
const fetchParkingLots = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/parking/lots', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      parkingLots.value = data.data
      ElMessage.success('获取停车场列表成功')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    console.error('获取停车场列表失败:', error)
    ElMessage.error('获取停车场列表失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 刷新停车场数据
const refreshParkingLots = () => {
  fetchParkingLots()
}

// 查看车位
const viewSpace = (lotId) => {
  router.push({ path: '/reservation', query: { lotId } })
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    name: '',
    location: ''
  }
  sortBy.value = ''
  currentPage.value = 1
}

// 排序处理
const handleSort = () => {
  currentPage.value = 1 // 重置到第一页
}

// 分页大小变化
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1 // 重置到第一页
}

// 当前页变化
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

// 行点击事件
const rowClick = (row) => {
  console.log('点击了行:', row)
}

// 页面挂载时获取数据
onMounted(() => {
  fetchParkingLots()
})
</script>

<style scoped>
.parking-lots-page {
  padding: 0;
  background-color: var(--lightest-gray);
}

/* 页面标题和操作区 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 0;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 10px;
}

/* 搜索和筛选区域 */
.search-filter-section {
  margin-bottom: 25px;
}

.search-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.search-card:hover {
  box-shadow: var(--shadow-md);
}

.search-form {
  width: 100%;
}

.search-input {
  width: 280px;
}

.search-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
}

.search-btn:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--secondary-light));
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.reset-btn {
  border-color: var(--medium-gray);
  color: var(--text-secondary);
}

.reset-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  background-color: var(--lightest-gray);
}

/* 统计卡片区域 */
.stats-section {
  margin-bottom: 25px;
}

.stat-card {
  border-radius: var(--border-radius);
  transition: all var(--transition-normal);
  border: none;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.total-lots .stat-icon {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.total-spaces .stat-icon {
  background: linear-gradient(135deg, var(--success-color), #38a169);
}

.available-spaces .stat-icon {
  background: linear-gradient(135deg, var(--info-color), #3182ce);
}

.occupancy-rate .stat-icon {
  background: linear-gradient(135deg, var(--warning-color), #dd6b20);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 表格区域 */
.table-section {
  margin-bottom: 25px;
}

.table-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
}

.table-card:hover {
  box-shadow: var(--shadow-md);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--light-gray);
  margin-bottom: 16px;
}

.table-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 10px;
}

/* 加载状态 */
.loading-container {
  padding: 40px 24px;
}

/* 无数据状态 */
.empty-container {
  padding: 60px 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius-sm);
}

/* 表格样式 */
.parking-table {
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 20px;
}

.parking-table :deep(.el-table__header-wrapper) {
  background-color: var(--lightest-gray);
}

.parking-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  font-weight: 600;
  font-size: 14px;
  text-align: center;
  padding: 16px 12px;
  border-bottom: none;
}

.parking-table :deep(.el-table__body tr) {
  transition: all var(--transition-fast);
}

.parking-table :deep(.el-table__body tr:hover) {
  background-color: var(--lightest-gray);
  transform: translateX(4px);
}

.parking-table :deep(.el-table__body td) {
  padding: 16px 12px;
  border-bottom: 1px solid var(--light-gray);
  font-size: 14px;
  color: var(--text-secondary);
}

.parking-table :deep(.el-table__body tr.parking-lot-full) {
  background-color: rgba(245, 101, 101, 0.05);
}

.parking-table :deep(.el-table__body tr.parking-lot-full:hover) {
  background-color: rgba(245, 101, 101, 0.1);
}

/* 表格内容样式 */
.parking-name {
  font-weight: 500;
  color: var(--text-primary);
}

.parking-location {
  color: var(--text-secondary);
  font-size: 13px;
}

.hourly-rate {
  font-weight: 600;
  color: var(--primary-color);
}

/* 分页区域 */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px 20px;
  background-color: white;
  border-top: 1px solid var(--light-gray);
}

.pagination-container :deep(.el-pagination) {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-container :deep(.el-pager li) {
  border-radius: var(--border-radius-sm);
  margin: 0 4px;
}

.pagination-container :deep(.el-pager li.active) {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-color: transparent;
  color: white;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .search-input {
    width: 220px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .search-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .pagination-container {
    justify-content: center;
  }
}
</style>