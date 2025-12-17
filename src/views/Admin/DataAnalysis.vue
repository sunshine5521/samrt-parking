<template>
  <div class="data-analysis">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>数据分析</span>
          <div class="filter-container">
            <el-select v-model="timeRange" placeholder="时间范围" size="small">
              <el-option label="今日" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
              <el-option label="本年" value="year" />
            </el-select>
            <el-button type="primary" size="small" @click="fetchStatistics">查询</el-button>
          </div>
        </div>
      </template>

      <!-- 统计卡片 -->
      <div class="statistics-cards">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-label">总停车场数</div>
            <div class="stat-value">{{ statistics.total_parking_lots || 0 }}</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-label">总车位数</div>
            <div class="stat-value">{{ statistics.total_spaces || 0 }}</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-label">当前占用率</div>
            <div class="stat-value">{{ (statistics.occupancy_rate || 0).toFixed(2) }}%</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-label">今日收入</div>
            <div class="stat-value">¥{{ statistics.today_revenue || 0 }}</div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 车位占用率趋势 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">车位占用率趋势</div>
          </template>
          <div class="chart-content">
            <div id="occupancyChart" style="height: 300px;"></div>
          </div>
        </el-card>

        <!-- 收入统计 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">收入统计</div>
          </template>
          <div class="chart-content">
            <div id="revenueChart" style="height: 300px;"></div>
          </div>
        </el-card>
      </div>

      <!-- 详细数据 -->
      <div class="detail-section">
        <el-card class="detail-card">
          <template #header>
            <div class="chart-header">停车场收入排名</div>
          </template>
          <el-table :data="parkingLotRevenues" border stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="停车场名称" />
            <el-table-column prop="revenue" label="收入" />
            <el-table-column prop="occupancy_rate" label="占用率" />
          </el-table>
        </el-card>

        <el-card class="detail-card">
          <template #header>
            <div class="chart-header">停车记录统计</div>
          </template>
          <el-table :data="parkingRecords" border stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="parking_lot_name" label="停车场名称" />
            <el-table-column prop="start_time" label="开始时间" />
            <el-table-column prop="end_time" label="结束时间" />
            <el-table-column prop="cost" label="费用" />
          </el-table>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const timeRange = ref('today')
const statistics = ref({})
const parkingLotRevenues = ref([])
const parkingRecords = ref([])

// 图表实例
let occupancyChart = null
let revenueChart = null

// 页面挂载时初始化数据
onMounted(() => {
  fetchStatistics()
  // 初始化图表
  setTimeout(() => {
    initCharts()
  }, 100)
})

// 页面卸载时销毁图表
onUnmounted(() => {
  if (occupancyChart && typeof occupancyChart.destroy === 'function') {
    occupancyChart.destroy()
  }
  if (revenueChart && typeof revenueChart.destroy === 'function') {
    revenueChart.destroy()
  }
})

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const token = localStorage.getItem('token')
    const params = new URLSearchParams()
    params.append('time_range', timeRange.value)

    const response = await fetch(`http://127.0.0.1:5000/api/admin/statistics?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      throw new Error('获取统计数据失败')
    }

    const data = await response.json()
    statistics.value = data.statistics || {}
    parkingLotRevenues.value = data.parking_lot_revenues || []
    parkingRecords.value = data.parking_records || []

    // 更新图表
    updateCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请重试')
    // 使用模拟数据
    useMockData()
  }
}

// 使用模拟数据
const useMockData = () => {
  statistics.value = {
    total_parking_lots: 10,
    total_spaces: 500,
    occupancy_rate: 75.5,
    today_revenue: 1250.5
  }

  parkingLotRevenues.value = [
    { id: 1, name: '中央停车场', revenue: '¥1250.5', occupancy_rate: '75.5%' },
    { id: 2, name: '商业中心停车场', revenue: '¥980.2', occupancy_rate: '68.3%' },
    { id: 3, name: '地铁口停车场', revenue: '¥765.8', occupancy_rate: '55.2%' },
    { id: 4, name: '火车站停车场', revenue: '¥1560.3', occupancy_rate: '85.7%' },
    { id: 5, name: '医院停车场', revenue: '¥890.6', occupancy_rate: '62.8%' }
  ]

  parkingRecords.value = [
    { id: 1, parking_lot_name: '中央停车场', start_time: '2024-05-20 08:30', end_time: '2024-05-20 12:45', cost: '¥40.5' },
    { id: 2, parking_lot_name: '商业中心停车场', start_time: '2024-05-20 09:15', end_time: '2024-05-20 11:30', cost: '¥22.5' },
    { id: 3, parking_lot_name: '地铁口停车场', start_time: '2024-05-20 10:00', end_time: '2024-05-20 13:45', cost: '¥37.5' },
    { id: 4, parking_lot_name: '火车站停车场', start_time: '2024-05-20 07:45', end_time: '2024-05-20 15:20', cost: '¥74.5' },
    { id: 5, parking_lot_name: '医院停车场', start_time: '2024-05-20 08:20', end_time: '2024-05-20 14:10', cost: '¥58.5' }
  ]

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

  // 车位占用率趋势图
  const occupancyChartDom = document.getElementById('occupancyChart')
  if (occupancyChartDom) {
    occupancyChart = window.echarts.init(occupancyChartDom)
  }

  // 收入统计图
  const revenueChartDom = document.getElementById('revenueChart')
  if (revenueChartDom) {
    revenueChart = window.echarts.init(revenueChartDom)
  }

  updateCharts()
}

// 更新图表
const updateCharts = () => {
  if (!occupancyChart || !revenueChart) return

  // 车位占用率趋势图
  const occupancyOption = {
    title: {
      text: '车位占用率趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        data: [45, 55, 75, 85, 65, 50],
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#1E88E5'
        }
      }
    ]
  }

  // 收入统计图
  const revenueOption = {
    title: {
      text: '收入统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [800, 950, 1200, 1100, 1350, 1500, 1400],
        type: 'bar',
        itemStyle: {
          color: '#43A047'
        }
      }
    ]
  }

  occupancyChart.setOption(occupancyOption)
  revenueChart.setOption(revenueOption)
}
</script>

<style scoped>
.data-analysis {
  padding: 0;
}

.analysis-card {
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
}

.statistics-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
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
  height: 350px;
}

.chart-header {
  font-size: 16px;
  font-weight: bold;
}

.chart-content {
  height: calc(100% - 60px);
  width: 100%;
}

.detail-section {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.detail-card {
  flex: 1;
  min-width: 45%;
  margin-bottom: 20px;
}
</style>