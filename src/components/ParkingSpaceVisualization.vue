<template>
  <div class="parking-space-visualization">
    <el-card shadow="hover" class="visualization-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ selectedLot ? selectedLot.name : '停车场可视化' }}</span>
          <el-select 
            v-model="selectedLotId" 
            placeholder="选择停车场" 
            size="small"
            @change="fetchParkingSpaces"
            class="lot-select"
          >
            <el-option
              v-for="lot in parkingLots"
              :key="lot.id"
              :label="lot.name"
              :value="lot.id"
            ></el-option>
          </el-select>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      
      <div v-else-if="!selectedLotId" class="empty-state">
        <el-empty description="请选择停车场" :image-size="120">
          <el-button type="primary" @click="$refs.lotSelect.focus()">选择停车场</el-button>
        </el-empty>
      </div>
      
      <div v-else>
        <!-- 停车场概览 -->
        <div class="parking-overview">
          <div class="overview-item">
            <span class="overview-label">总车位数:</span>
            <span class="overview-value total">{{ parkingSpaces.length }}</span>
          </div>
          <div class="overview-item">
            <span class="overview-label">空闲:</span>
            <span class="overview-value free">{{ freeSpaces }}</span>
          </div>
          <div class="overview-item">
            <span class="overview-label">已预约:</span>
            <span class="overview-value booked">{{ bookedSpaces }}</span>
          </div>
          <div class="overview-item">
            <span class="overview-label">已占用:</span>
            <span class="overview-value occupied">{{ occupiedSpaces }}</span>
          </div>
        </div>
        
        <!-- 车位状态图例 -->
        <div class="legend">
          <div class="legend-item">
            <div class="legend-color free"></div>
            <span class="legend-text">空闲车位</span>
          </div>
          <div class="legend-item">
            <div class="legend-color booked"></div>
            <span class="legend-text">已预约</span>
          </div>
          <div class="legend-item">
            <div class="legend-color occupied"></div>
            <span class="legend-text">已占用</span>
          </div>
        </div>
        
        <!-- 车位网格 -->
        <div class="parking-grid">
          <div 
            v-for="space in parkingSpaces" 
            :key="space.id"
            :class="[
              'parking-space',
              space.status,
              { 'space-selected': selectedSpaceId === space.id }
            ]"
            @click="selectSpace(space)"
            @mouseenter="hoveredSpaceId = space.id"
            @mouseleave="hoveredSpaceId = null"
          >
            <div class="space-number">{{ space.space_number }}</div>
            
            <!-- 悬浮信息 -->
            <div v-if="hoveredSpaceId === space.id" class="space-tooltip">
              <div class="tooltip-title">车位详情</div>
              <div class="tooltip-content">
                <div><strong>车位编号:</strong> {{ space.space_number }}</div>
                <div><strong>状态:</strong> {{ getStatusText(space.status) }}</div>
                <div><strong>停车场:</strong> {{ selectedLot.name }}</div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div v-if="selectedSpaceId === space.id" class="space-actions">
              <el-button 
                v-if="space.status === 'free'" 
                type="primary" 
                size="mini"
                @click.stop="reserveSpace(space)"
              >
                立即预约
              </el-button>
              <el-button 
                v-else-if="space.status === 'booked'"
                type="warning" 
                size="mini"
                disabled
              >
                已预约
              </el-button>
              <el-button 
                v-else
                type="danger" 
                size="mini"
                disabled
              >
                已占用
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 状态管理
const parkingLots = ref([])
const parkingSpaces = ref([])
const selectedLotId = ref(null)
const selectedSpaceId = ref(null)
const hoveredSpaceId = ref(null)
const loading = ref(false)

// 计算属性
const selectedLot = computed(() => {
  if (!selectedLotId.value) return null
  return parkingLots.value.find(lot => lot.id === selectedLotId.value) || null
})

const freeSpaces = computed(() => {
  return parkingSpaces.value.filter(space => space.status === 'free').length
})

const bookedSpaces = computed(() => {
  return parkingSpaces.value.filter(space => space.status === 'booked' || space.status === 'reserved').length
})

const occupiedSpaces = computed(() => {
  return parkingSpaces.value.filter(space => space.status === 'occupied').length
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
    const data = await response.json()
    if (data.code === 200) {
      parkingLots.value = data.data
      // 如果有停车场，默认选择第一个
      if (parkingLots.value.length > 0 && !selectedLotId.value) {
        selectedLotId.value = parkingLots.value[0].id
        fetchParkingSpaces()
      }
    } else {
      ElMessage.error(data.message || '获取停车场列表失败')
    }
  } catch (error) {
    console.error('获取停车场列表失败:', error)
    ElMessage.error('获取停车场列表失败，请检查网络连接')
  }
}

// 获取车位列表
const fetchParkingSpaces = async () => {
  if (!selectedLotId.value) return
  
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces?lot_id=${selectedLotId.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      parkingSpaces.value = data.data
      // 按车位号排序
      parkingSpaces.value.sort((a, b) => {
        return a.space_number.localeCompare(b.space_number, 'zh-CN', { numeric: true })
      })
      ElMessage.success('获取车位列表成功')
    } else {
      ElMessage.error(data.message || '获取车位列表失败')
    }
  } catch (error) {
    console.error('获取车位列表失败:', error)
    ElMessage.error('获取车位列表失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    free: '空闲',
    booked: '已预约',
    reserved: '已预约',
    occupied: '已占用'
  }
  return statusMap[status] || status
}

// 选择车位
const selectSpace = (space) => {
  selectedSpaceId.value = space.id
}

// 预约车位
const reserveSpace = async (space) => {
  try {
    // 跳转到预约页面
    router.push({
      path: '/reservation',
      query: {
        lotId: selectedLotId.value,
        spaceId: space.id
      }
    })
    
    selectedSpaceId.value = null
  } catch (error) {
    console.error('预约失败:', error)
    ElMessage.error('预约失败，请稍后重试')
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchParkingLots()
})
</script>

<style scoped>
.parking-space-visualization {
  padding: 0;
}

.visualization-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
  margin-bottom: 25px;
}

.visualization-card:hover {
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

.lot-select {
  width: 200px;
}

.loading-container {
  padding: 40px 20px;
}

.empty-state {
  padding: 60px 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius-sm);
}

/* 停车场概览 */
.parking-overview {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius-sm);
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.overview-value {
  font-size: 20px;
  font-weight: bold;
}

.overview-value.total {
  color: var(--text-primary);
}

.overview-value.free {
  color: var(--success-color);
}

.overview-value.booked {
  color: var(--warning-color);
}

.overview-value.occupied {
  color: var(--danger-color);
}

/* 图例 */
.legend {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
  padding: 15px;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid var(--medium-gray);
}

.legend-color.free {
  background-color: var(--success-color);
  opacity: 0.7;
}

.legend-color.booked {
  background-color: var(--warning-color);
  opacity: 0.7;
}

.legend-color.occupied {
  background-color: var(--danger-color);
  opacity: 0.7;
}

.legend-text {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 车位网格 */
.parking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  padding: 15px;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius);
  min-height: 400px;
}

/* 车位样式 */
.parking-space {
  position: relative;
  width: 100%;
  aspect-ratio: 3/2;
  border-radius: 8px;
  border: 2px solid var(--medium-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: white;
  overflow: hidden;
}

/* 车位状态 */
.parking-space.free {
  background-color: rgba(72, 187, 120, 0.2);
  border-color: var(--success-color);
}

.parking-space.booked {
  background-color: rgba(237, 137, 54, 0.2);
  border-color: var(--warning-color);
}

.parking-space.reserved {
  background-color: rgba(237, 137, 54, 0.2);
  border-color: var(--warning-color);
}

.parking-space.occupied {
  background-color: rgba(245, 101, 101, 0.2);
  border-color: var(--danger-color);
}

/* 车位选择状态 */
.parking-space.space-selected {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

/* 车位编号 */
.space-number {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  z-index: 1;
  transition: all 0.3s ease;
}

/* 车位悬浮信息 */
.space-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: white;
  border: 1px solid var(--medium-gray);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  width: 250px;
  pointer-events: none;
  margin-top: 8px;
  animation: fadeIn 0.3s ease-out;
}

.tooltip-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-size: 14px;
}

.tooltip-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 车位操作按钮 */
.space-actions {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 5;
  display: flex;
  gap: 8px;
  width: 90%;
  animation: slideUp 0.3s ease-out;
}

.space-actions .el-button {
  flex: 1;
  font-size: 11px;
  padding: 4px;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .lot-select {
    width: 100%;
  }
  
  .parking-overview {
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .legend {
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .parking-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
    padding: 10px;
  }
  
  .space-number {
    font-size: 16px;
  }
  
  .space-tooltip {
    width: 200px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .parking-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 8px;
  }
  
  .space-number {
    font-size: 14px;
  }
}
</style>