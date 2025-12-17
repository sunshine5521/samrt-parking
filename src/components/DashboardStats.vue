<template>
  <div class="dashboard-stats">
    <el-card shadow="hover" class="stat-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">停车场统计</span>
          <el-select 
            v-model="timeRange" 
            placeholder="选择时间范围" 
            size="small"
            @change="fetchStatistics"
            class="time-range-select"
          >
            <el-option label="今日" value="today"></el-option>
            <el-option label="本周" value="week"></el-option>
            <el-option label="本月" value="month"></el-option>
            <el-option label="本年" value="year"></el-option>
          </el-select>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>
      
      <div v-else>
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-grid">
          <el-col :span="6">
            <div class="stat-item total-lots">
              <div class="stat-icon">
                <el-icon><Building /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_parking_lots }}</div>
                <div class="stat-label">总停车场数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item total-spaces">
              <div class="stat-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_spaces }}</div>
                <div class="stat-label">总车位数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item occupancy-rate">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.occupancy_rate }}%</div>
                <div class="stat-label">平均使用率</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item revenue">
              <div class="stat-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">¥{{ statistics.today_revenue }}</div>
                <div class="stat-label">{{ getTimeRangeText() }}收入</div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 停车场收入和使用率图表 -->
        <div class="charts-container">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover" class="chart-card">
                <template #header>
                  <div class="chart-title">停车场收入排名</div>
                </template>
                <div class="chart-content">
                  <el-table :data="parkingLotRevenues" stripe style="width: 100%">
                    <el-table-column prop="name" label="停车场" min-width="150"></el-table-column>
                    <el-table-column prop="revenue" label="收入" width="120" align="right">
                      <template #default="scope">¥{{ scope.row.revenue }}</template>
                    </el-table-column>
                    <el-table-column prop="occupancy_rate" label="使用率" width="120" align="right">
                      <template #default="scope">
                        <el-progress 
                          type="dashboard" 
                          :percentage="scope.row.occupancy_rate" 
                          :width="60" 
                          :stroke-width="8"
                        ></el-progress>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card shadow="hover" class="chart-card">
                <template #header>
                  <div class="chart-title">最近停车记录</div>
                </template>
                <div class="chart-content">
                  <el-timeline>
                    <el-timeline-item 
                      v-for="record in parkingRecords" 
                      :key="record.id"
                      :timestamp="formatTime(record.start_time)"
                    >
                      <div class="timeline-content">
                        <div class="timeline-title">{{ record.parking_lot_name }}</div>
                        <div class="timeline-desc">
                          开始时间：{{ formatDateTime(record.start_time) }}<br>
                          结束时间：{{ formatDateTime(record.end_time) }}<br>
                          费用：¥{{ record.cost }}
                        </div>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Building, Van, TrendCharts, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const timeRange = ref('today')
const loading = ref(false)

// 统计数据
const statistics = ref({
  total_parking_lots: 0,
  total_spaces: 0,
  occupancy_rate: 0,
  today_revenue: 0
})

const parkingLotRevenues = ref([])
const parkingRecords = ref([])

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:5000/api/admin/statistics?time_range=${timeRange.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    const data = await response.json()
    if (data.code === 200) {
      statistics.value = data.statistics
      parkingLotRevenues.value = data.parking_lot_revenues
      parkingRecords.value = data.parking_records
      ElMessage.success('获取统计数据成功')
    } else {
      ElMessage.error(data.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期时间
const formatDateTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取时间范围文本
const getTimeRangeText = () => {
  const map = {
    today: '今日',
    week: '本周',
    month: '本月',
    year: '本年'
  }
  return map[timeRange.value] || '今日'
}

// 页面挂载时获取数据
onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.dashboard-stats {
  padding: 0;
}

.stat-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
  margin-bottom: 25px;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.time-range-select {
  width: 120px;
}

.loading-container {
  padding: 40px 20px;
}

/* 统计卡片 */
.stats-grid {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius);
  transition: all var(--transition-normal);
  border-left: 4px solid transparent;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.total-lots {
  border-left-color: var(--primary-color);
}

.total-spaces {
  border-left-color: var(--secondary-color);
}

.occupancy-rate {
  border-left-color: var(--warning-color);
}

.revenue {
  border-left-color: var(--success-color);
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
  background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
}

.occupancy-rate .stat-icon {
  background: linear-gradient(135deg, var(--warning-color), #dd6b20);
}

.revenue .stat-icon {
  background: linear-gradient(135deg, var(--success-color), #38a169);
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

/* 图表区域 */
.charts-container {
  margin-top: 20px;
}

.chart-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
  height: 100%;
}

.chart-card:hover {
  box-shadow: var(--shadow-md);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-content {
  padding: 10px 0;
}

/* 时间线 */
.timeline-content {
  padding: 0;
}

.timeline-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.timeline-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .el-col {
    margin-bottom: 20px;
  }
  
  .el-col :last-child {
    margin-bottom: 0;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .stats-grid {
    margin-bottom: 0;
  }
  
  .stat-item {
    padding: 15px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>