<template>
  <div class="revenue-statistics">
    <el-card class="statistics-card">
      <template #header>
        <div class="card-header">
          <span>收入统计</span>
          <div class="filter-container">
            <el-select v-model="timeRange" placeholder="时间范围" size="small" @change="fetchRevenueData">
              <el-option label="今日" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
              <el-option label="本年" value="year" />
              <el-option label="自定义" value="custom" />
            </el-select>
            <div v-if="timeRange === 'custom'" class="date-range-container">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                size="small"
                @change="fetchRevenueData"
              />
            </div>
            <el-button type="primary" size="small" @click="fetchRevenueData">查询</el-button>
          </div>
        </div>
      </template>

      <!-- 收入概览卡片 -->
      <div class="revenue-overview">
        <el-card class="overview-card success">
          <div class="card-content">
            <div class="card-label">今日总收入</div>
            <div class="card-value">¥{{ revenueData.todayRevenue || '0.00' }}</div>
            <div class="card-change" :class="revenueData.todayChange >= 0 ? 'positive' : 'negative'">
              <el-icon v-if="revenueData.todayChange >= 0">↗</el-icon>
              <el-icon v-else>↘</el-icon>
              {{ Math.abs(revenueData.todayChange) }}%
            </div>
          </div>
        </el-card>
        
        <el-card class="overview-card warning">
          <div class="card-content">
            <div class="card-label">本月总收入</div>
            <div class="card-value">¥{{ revenueData.monthRevenue || '0.00' }}</div>
            <div class="card-change" :class="revenueData.monthChange >= 0 ? 'positive' : 'negative'">
              <el-icon v-if="revenueData.monthChange >= 0">↗</el-icon>
              <el-icon v-else>↘</el-icon>
              {{ Math.abs(revenueData.monthChange) }}%
            </div>
          </div>
        </el-card>
        
        <el-card class="overview-card info">
          <div class="card-content">
            <div class="card-label">本年总收入</div>
            <div class="card-value">¥{{ revenueData.yearRevenue || '0.00' }}</div>
            <div class="card-change" :class="revenueData.yearChange >= 0 ? 'positive' : 'negative'">
              <el-icon v-if="revenueData.yearChange >= 0">↗</el-icon>
              <el-icon v-else>↘</el-icon>
              {{ Math.abs(revenueData.yearChange) }}%
            </div>
          </div>
        </el-card>
        
        <el-card class="overview-card danger">
          <div class="card-content">
            <div class="card-label">总计收入</div>
            <div class="card-value">¥{{ revenueData.totalRevenue || '0.00' }}</div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 收入趋势图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">收入趋势</div>
          </template>
          <div class="chart-content">
            <div id="revenueTrendChart" style="height: 400px;"></div>
          </div>
        </el-card>
        
        <!-- 停车场收入排名 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">停车场收入排名</div>
          </template>
          <div class="chart-content">
            <div id="parkingLotRevenueChart" style="height: 400px;"></div>
          </div>
        </el-card>
      </div>

      <!-- 详细收入列表 -->
      <el-card class="detail-card">
        <template #header>
          <div class="detail-header">
            <span>收入明细</span>
          </div>
        </template>
        <el-table :data="revenueDetails" border stripe style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="parking_lot_name" label="停车场名称" />
          <el-table-column prop="license_plate" label="车牌号" width="120" />
          <el-table-column prop="start_time" label="开始时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="end_time" label="结束时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.end_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="停车时长" width="100">
            <template #default="scope">
              {{ scope.row.duration }}小时
            </template>
          </el-table-column>
          <el-table-column prop="cost" label="费用" width="100" align="right">
            <template #default="scope">
              <span class="cost-text">¥{{ scope.row.cost }}</span>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const timeRange = ref('today')
const dateRange = ref([])
const revenueData = ref({
  todayRevenue: 0,
  monthRevenue: 0,
  yearRevenue: 0,
  totalRevenue: 0,
  todayChange: 0,
  monthChange: 0,
  yearChange: 0
})
const revenueDetails = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 图表实例
let revenueTrendChart = null
let parkingLotRevenueChart = null

// 页面挂载时初始化数据
onMounted(() => {
  fetchRevenueData()
  // 初始化图表
  setTimeout(() => {
    initCharts()
  }, 100)
})

// 页面卸载时销毁图表
onUnmounted(() => {
  if (revenueTrendChart) revenueTrendChart.destroy()
  if (parkingLotRevenueChart) parkingLotRevenueChart.destroy()
})

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取收入数据
const fetchRevenueData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    params.append('time_range', timeRange.value)
    params.append('page', currentPage.value)
    params.append('page_size', pageSize.value)
    
    if (timeRange.value === 'custom' && dateRange.value.length === 2) {
      params.append('start_date', dateRange.value[0].toISOString())
      params.append('end_date', dateRange.value[1].toISOString())
    }

    const response = await fetch(`http://127.0.0.1:5000/api/admin/revenue-statistics?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取收入数据失败')
    }

    const data = await response.json()
    revenueData.value = data.revenue_summary || {
      todayRevenue: 0,
      monthRevenue: 0,
      yearRevenue: 0,
      totalRevenue: 0,
      todayChange: 0,
      monthChange: 0,
      yearChange: 0
    }
    revenueDetails.value = data.revenue_details || []
    total.value = data.total || 0

    // 更新图表
    updateCharts(data.chart_data || {})
  } catch (error) {
    console.error('获取收入数据失败:', error)
    ElMessage.error('获取收入数据失败，请重试')
    // 使用模拟数据
    useMockData()
  } finally {
    loading.value = false
  }
}

// 使用模拟数据
const useMockData = () => {
  revenueData.value = {
    todayRevenue: 1250.5,
    monthRevenue: 38500.8,
    yearRevenue: 462009.6,
    totalRevenue: 1256789.3,
    todayChange: 12.5,
    monthChange: 8.2,
    yearChange: 15.8
  }
  
  revenueDetails.value = [
    { id: 1, parking_lot_name: '中央停车场', license_plate: '京A12345', start_time: '2024-05-20T08:30:00', end_time: '2024-05-20T12:45:00', duration: 4.25, cost: '40.5' },
    { id: 2, parking_lot_name: '商业中心停车场', license_plate: '沪B67890', start_time: '2024-05-20T09:15:00', end_time: '2024-05-20T11:30:00', duration: 2.25, cost: '22.5' },
    { id: 3, parking_lot_name: '地铁口停车场', license_plate: '粤C24680', start_time: '2024-05-20T10:00:00', end_time: '2024-05-20T13:45:00', duration: 3.75, cost: '37.5' },
    { id: 4, parking_lot_name: '火车站停车场', license_plate: '浙D13579', start_time: '2024-05-20T07:45:00', end_time: '2024-05-20T15:20:00', duration: 7.58, cost: '74.5' },
    { id: 5, parking_lot_name: '医院停车场', license_plate: '苏E97531', start_time: '2024-05-20T08:20:00', end_time: '2024-05-20T14:10:00', duration: 5.83, cost: '58.5' }
  ]
  
  total.value = 125
  
  // 更新图表
  updateCharts()
}

// 初始化图表
const initCharts = () => {
  // 检查是否有ECharts
  if (typeof window.echarts === 'undefined') {
    // 动态加载ECharts
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js'
    script.onload = () => {
      initCharts()
    }
    document.head.appendChild(script)
    return
  }

  // 收入趋势图
  const revenueTrendDom = document.getElementById('revenueTrendChart')
  if (revenueTrendDom) {
    revenueTrendChart = window.echarts.init(revenueTrendDom)
  }

  // 停车场收入排名
  const parkingLotRevenueDom = document.getElementById('parkingLotRevenueChart')
  if (parkingLotRevenueDom) {
    parkingLotRevenueChart = window.echarts.init(parkingLotRevenueDom)
  }

  updateCharts()
}

// 更新图表
const updateCharts = (chartData = {}) => {
  if (!revenueTrendChart || !parkingLotRevenueChart) return

  // 收入趋势图
  const trendOption = {
    title: {
      text: '收入趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        return `${params[0].axisValue}<br/>收入: ¥${params[0].value}`
      }
    },
    xAxis: {
      type: 'category',
      data: chartData.trend_dates || ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value',
      name: '收入 (元)'
    },
    series: [
      {
        data: chartData.trend_data || [800, 950, 1200, 1100, 1350, 1500, 1400],
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#43A047'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(67, 160, 71, 0.3)'
            }, {
              offset: 1, color: 'rgba(67, 160, 71, 0.05)'
            }]
          }
        }
      }
    ]
  }

  // 停车场收入排名
  const parkingLotOption = {
    title: {
      text: '停车场收入排名',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        return `${params[0].name}<br/>收入: ¥${params[0].value}`
      }
    },
    xAxis: {
      type: 'value',
      name: '收入 (元)'
    },
    yAxis: {
      type: 'category',
      data: chartData.parking_lot_names || ['中央停车场', '商业中心停车场', '地铁口停车场', '火车站停车场', '医院停车场']
    },
    series: [
      {
        data: chartData.parking_lot_revenues || [1250.5, 980.2, 765.8, 1560.3, 890.6],
        type: 'bar',
        itemStyle: {
          color: function(params) {
            const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            return colors[params.dataIndex % colors.length]
          }
        }
      }
    ]
  }

  revenueTrendChart.setOption(trendOption)
  parkingLotRevenueChart.setOption(parkingLotOption)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchRevenueData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchRevenueData()
}
</script>

<style scoped>
.revenue-statistics {
  padding: 0;
}

.statistics-card {
  height: calc(100vh - 100px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

.date-range-container {
  display: flex;
  gap: 10px;
}

.revenue-overview {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.overview-card {
  flex: 1;
  min-width: 220px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.overview-card.success {
  border-left: 4px solid #43A047;
}

.overview-card.warning {
  border-left: 4px solid #FB8C00;
}

.overview-card.info {
  border-left: 4px solid #1E88E5;
}

.overview-card.danger {
  border-left: 4px solid #E53935;
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.card-change {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.card-change.positive {
  color: #43A047;
}

.card-change.negative {
  color: #E53935;
}

.charts-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.chart-card {
  flex: 1;
  min-width: 45%;
  height: 450px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-header {
  font-size: 16px;
  font-weight: bold;
}

.chart-content {
  height: calc(100% - 60px);
  width: 100%;
}

.detail-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.detail-header {
  font-size: 16px;
  font-weight: bold;
}

.cost-text {
  font-weight: bold;
  color: #E53935;
}

@media (max-width: 1200px) {
  .chart-card {
    min-width: 100%;
  }
}

@media (max-width: 768px) {
  .revenue-overview {
    flex-direction: column;
  }
  
  .overview-card {
    min-width: 100%;
  }
  
  .filter-container {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>