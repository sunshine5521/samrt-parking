<template>
  <div class="make-reservation-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">车位预定</h1>
    </div>
    
    <!-- 已预约车辆信息 -->
    <div v-if="reservations.length > 0" class="my-reservations-section">
      <el-card shadow="hover" class="reservations-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">我的预约</span>
            <el-button 
              type="primary" 
              size="small"
              @click="fetchReservations"
              class="refresh-btn"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <!-- 加载状态 -->
        <div v-if="loadingReservations" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        
        <!-- 预约列表 -->
        <el-table 
          v-else 
          :data="reservations" 
          border 
          class="reservations-table"
          :header-cell-style="headerCellStyle"
          :row-class-name="rowClassName"
        >
          <el-table-column prop="id" label="预约ID" width="100" align="center"></el-table-column>
          <el-table-column prop="parking_lot_name" label="停车场" min-width="180"></el-table-column>
          <el-table-column prop="license_plate" label="车牌号" width="120"></el-table-column>
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
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.status === 'completed' ? 'success' : 
                       (scope.row.status === 'canceled' || scope.row.status === 'cancelled') ? 'danger' : 
                       scope.row.status === 'booked' ? 'warning' : 
                       scope.row.status === 'checked_in' ? 'info' : 
                       (scope.row.status === 'expired' || scope.row.status === 'no_show') ? 'danger' : 
                       (scope.row.status === 'confirmed' || scope.row.status === 'pending') ? 'info' : 'danger'"
                size="large"
                effect="dark"
              >
                {{ scope.row.status === 'completed' ? '已完成' : 
                   (scope.row.status === 'canceled' || scope.row.status === 'cancelled') ? '已取消' : 
                   scope.row.status === 'booked' ? '已预约' : 
                   scope.row.status === 'checked_in' ? '已入场' : 
                   (scope.row.status === 'expired' || scope.row.status === 'no_show') ? '已过期' : 
                   (scope.row.status === 'confirmed' || scope.row.status === 'pending') ? '已确认' : '未知状态' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_cost" label="总费用" width="120" align="center">
            <template #default="scope">
              <span class="total-cost">¥{{ parseFloat(scope.row.total_cost).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="scope">
              <el-button 
                v-if="scope.row.status === 'booked'" 
                type="danger" 
                size="small"
                @click="cancelReservation(scope.row.id)"
              >
                取消预约
              </el-button>
              <span v-else class="no-action">-</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 左侧：停车场选择和费用计算 -->
      <div class="left-section">
        <!-- 停车场选择 -->
        <el-card shadow="hover" class="parking-lot-select-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">选择停车场</span>
            </div>
          </template>
          <el-select 
            v-model="selectedLotId" 
            placeholder="请选择停车场"
            class="lot-select"
            filterable
            clearable
          >
            <el-option
              v-for="lot in parkingLots"
              :key="lot.id"
              :label="lot.name"
              :value="lot.id"
            ></el-option>
          </el-select>
        </el-card>

        <!-- 费用计算部分 -->
        <el-card 
          v-if="selectedLot" 
          shadow="hover" 
          class="fee-calculator-card"
        >
          <template #header>
            <div class="card-header">
              <span class="card-title">费用计算</span>
            </div>
          </template>
          
          <el-form :model="feeForm" class="fee-form">
            <el-row :gutter="20">
              <el-col :xs="24" :md="12">
                <el-form-item label="开始时间" class="form-item">
                  <el-date-picker
                    v-model="feeForm.startTime"
                    type="datetime"
                    placeholder="选择开始时间"
                    class="date-picker"
                  ></el-date-picker>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="结束时间" class="form-item">
                  <el-date-picker
                    v-model="feeForm.endTime"
                    type="datetime"
                    placeholder="选择结束时间"
                    class="date-picker"
                  ></el-date-picker>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="时薪" class="form-item">
                  <el-input
                    v-model="selectedLot.hourly_rate"
                    readonly
                    class="input"
                  ></el-input>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-form-item label="总费用" class="form-item">
                  <el-input
                    v-model="totalFee"
                    readonly
                    class="input total-cost-input"
                  ></el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </div>
      
      <!-- 右侧：车位列表 -->
      <div class="right-section">
        <el-card shadow="hover" class="parking-spaces-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                {{ selectedLot ? selectedLot.name + ' - 车位列表' : '车位列表' }}
              </span>
              <el-button 
                v-if="selectedLotId" 
                type="primary" 
                size="small"
                @click="fetchParkingSpaces"
                class="refresh-btn"
              >
                <el-icon><Refresh /></el-icon>
                刷新车位
              </el-button>
            </div>
          </template>
          
          <!-- 无选择停车场提示 -->
          <div v-if="!selectedLotId" class="empty-state">
            <el-empty description="请先选择停车场" :image-size="100">
              <el-button type="primary" @click="$refs.lotSelect.focus()">选择停车场</el-button>
            </el-empty>
          </div>
          
          <!-- 加载状态 -->
          <div v-else-if="loadingSpaces" class="loading-container">
            <el-skeleton :rows="8" animated />
          </div>
          
          <!-- 车位列表 -->
          <el-table 
            v-else 
            :data="parkingSpaces" 
            border 
            class="parking-spaces-table"
            :header-cell-style="headerCellStyle"
            :row-class-name="spaceRowClassName"
          >
            <el-table-column prop="id" label="车位ID" width="100" align="center"></el-table-column>
            <el-table-column prop="space_number" label="车位编号" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="120" align="center">
              <template #default="scope">
                <el-tag 
                  v-if="scope.row.status === 'free'" 
                  type="success"
                  size="large"
                  effect="dark"
                >空闲</el-tag>
                <el-tag 
                  v-else-if="scope.row.status === 'booked' || scope.row.status === 'reserved'" 
                  type="warning"
                  size="large"
                  effect="dark"
                >已被预订</el-tag>
                <el-tag 
                  v-else 
                  type="danger"
                  size="large"
                  effect="dark"
                >已占用</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center">
              <template #default="scope">
                <el-button 
                  v-if="scope.row.status === 'free'" 
                  type="primary" 
                  @click="makeReservation(scope.row.id)"
                  size="small"
                  :loading="reservingSpaceId === scope.row.id"
                >
                  <el-icon v-if="reservingSpaceId === scope.row.id"><Loading /></el-icon>
                  预定
                </el-button>
                <el-button 
                  v-else-if="scope.row.status === 'booked' || scope.row.status === 'reserved'" 
                  type="warning" 
                  disabled
                  size="small"
                >
                  已预约
                </el-button>
                <el-button 
                  v-else 
                  type="danger" 
                  disabled
                  size="small"
                >
                  已占用
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElSelect, ElOption, ElTable, ElTableColumn, ElButton, ElTag, ElDatePicker, ElForm, ElFormItem, ElInput, ElCard, ElSkeleton, ElEmpty } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { Refresh, Loading } from '@element-plus/icons-vue'

// 状态管理
const parkingLots = ref([])
const parkingSpaces = ref([])
const reservations = ref([])
const selectedLotId = ref(null)
const route = useRoute()
const router = useRouter()

// 加载状态
const loadingReservations = ref(false)
const loadingSpaces = ref(false)
const reservingSpaceId = ref(null)

// 费用计算相关变量
const selectedLot = ref(null)
const feeForm = ref({
  startTime: undefined,
  endTime: undefined
})
const totalFee = ref(0)

// 表格头部样式
const headerCellStyle = {
  background: 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))',
  color: 'white',
  fontWeight: '600',
  fontSize: '14px',
  height: '50px',
  textAlign: 'center'
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 行样式
const rowClassName = ({ row }) => {
  if (row.status === 'cancelled') {
    return 'reservation-cancelled'
  }
  if (row.status === 'completed') {
    return 'reservation-completed'
  }
  return ''
}

// 车位行样式
const spaceRowClassName = ({ row }) => {
  if (row.status === 'free') {
    return 'space-free'
  }
  if (row.status === 'booked' || row.status === 'reserved') {
    return 'space-booked'
  }
  return 'space-occupied'
}

// 获取用户预约信息
const fetchReservations = async () => {
  loadingReservations.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/user/reservations', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      reservations.value = data.data
      ElMessage.success('获取预约信息成功')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    console.error('获取预约信息失败:', error)
    ElMessage.error('获取预约信息失败，请检查网络连接')
  } finally {
    loadingReservations.value = false
  }
}

// 获取车位列表
const fetchParkingSpaces = async () => {
  if (!selectedLotId.value) return
  
  loadingSpaces.value = true
  try {
    const token = localStorage.getItem('token')
    // 确保selectedLotId是数字类型
    const lotId = parseInt(selectedLotId.value)
    
    // 构建请求URL，如果有时间范围则调用可预约车位API
    let url = `http://127.0.0.1:5000/api/parking/spaces?lot_id=${lotId}`
    if (feeForm.value.startTime && feeForm.value.endTime) {
      const start_time = new Date(feeForm.value.startTime).toISOString()
      const end_time = new Date(feeForm.value.endTime).toISOString()
      url = `http://127.0.0.1:5000/api/parking/spaces/available?lot_id=${lotId}&start_time=${encodeURIComponent(start_time)}&end_time=${encodeURIComponent(end_time)}`
    }
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      parkingSpaces.value = data.data
      ElMessage.success('获取车位列表成功')
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    console.error('获取车位列表失败:', error)
    ElMessage.error('获取车位列表失败，请检查网络连接')
  } finally {
    loadingSpaces.value = false
  }
}

// 取消预约
const cancelReservation = async (reservationId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:5000/api/reservations/${reservationId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('预约已取消')
      // 刷新预约列表
      fetchReservations()
      // 刷新当前选择停车场的车位列表
      if (selectedLotId.value) {
        try {
          const lotId = parseInt(selectedLotId.value)
          const spacesResponse = await fetch(`http://127.0.0.1:5000/api/parking/spaces?lot_id=${lotId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
          const spacesData = await spacesResponse.json()
          if (spacesData.code === 200) {
            parkingSpaces.value = spacesData.data
          }
        } catch (error) {
          console.error('刷新车位列表失败:', error)
        }
      }
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    console.error('取消预约失败:', error)
    ElMessage.error('取消预约失败')
  }
}

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
      if (route.query.lotId) {
        selectedLotId.value = parseInt(route.query.lotId)
      }
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('获取停车场列表失败')
  }
}

// 监控selectedLotId变化，更新selectedLot
watch(selectedLotId, (newLotId) => {
  if (newLotId) {
    // 确保newLotId是数字类型
    const lotId = parseInt(newLotId)
    selectedLot.value = parkingLots.value.find(lot => lot.id === lotId)
    feeForm.value.startTime = undefined
    feeForm.value.endTime = undefined
    totalFee.value = 0
  } else {
    selectedLot.value = null
  }
})

// 监控开始时间和结束时间变化，计算总费用
watch(() => [feeForm.value.startTime, feeForm.value.endTime], () => {
  if (feeForm.value.startTime && feeForm.value.endTime && selectedLot.value) {
    const start = new Date(feeForm.value.startTime)
    const end = new Date(feeForm.value.endTime)
    if (end > start) {
      const duration = (end - start) / (1000 * 60 * 60) // 小时数
      totalFee.value = (duration * selectedLot.value.hourly_rate).toFixed(2)
    } else {
      totalFee.value = 0
    }
  } else {
    totalFee.value = 0
  }
})

watch(selectedLotId, async (newLotId) => {
  if (newLotId) {
    try {
      const token = localStorage.getItem('token')
      // 确保newLotId是数字类型
      const lotId = parseInt(newLotId)
      const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces?lot_id=${lotId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const data = await response.json()
      if (data.code === 200) {
        parkingSpaces.value = data.data
      } else {
        ElMessage.error(data.message)
      }
    } catch (error) {
      ElMessage.error('获取车位列表失败')
    }
  } else {
    parkingSpaces.value = []
  }
})

const makeReservation = async (spaceId) => {
  // 检查时间有效性
  if (feeForm.value.startTime && feeForm.value.endTime) {
    const start = new Date(feeForm.value.startTime)
    const end = new Date(feeForm.value.endTime)
    if (end <= start) {
      ElMessage.error('结束时间必须晚于开始时间')
      return
    }
  }

  // 设置加载状态
  reservingSpaceId.value = spaceId
  
  try {
    const user_id = localStorage.getItem('user_id')
    let vehicle_id;
    
    // 获取用户车辆
    const vehiclesResponse = await fetch('http://127.0.0.1:5000/api/user/vehicles', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    })
    const vehiclesData = await vehiclesResponse.json()
    if (vehiclesData.code !== 200 || vehiclesData.data.length === 0) {
      ElMessage.error('请先添加车辆')
      router.push('/my-vehicles')
      return
    }
    vehicle_id = vehiclesData.data[0].id

    // 使用用户选择的时间或默认值
    const start_time = feeForm.value.startTime 
      ? new Date(feeForm.value.startTime).toISOString() 
      : new Date().toISOString()
    const end_time = feeForm.value.endTime 
      ? new Date(feeForm.value.endTime).toISOString() 
      : new Date(Date.now() + 3600 * 1000).toISOString()

    // 发送预约请求
    // 确保selectedLotId是数字类型
    const lotId = parseInt(selectedLotId.value)
    const response = await fetch('http://127.0.0.1:5000/api/reservations', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user_id,
          vehicle_id,
          parking_lot_id: lotId,
          parking_space_id: spaceId,
          start_time,
          end_time
        })
      })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('预定成功')
      // 刷新车位列表以更新状态
      await fetchParkingSpaces()
      // 刷新预约列表
      await fetchReservations()
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    console.error('预定失败:', error)
    ElMessage.error('预定失败，请检查网络连接')
  } finally {
    // 重置加载状态
    reservingSpaceId.value = null
  }
}

onMounted(() => {
  fetchParkingLots()
  fetchReservations()
})
</script>

<style scoped>
.make-reservation-page {
  padding: 0;
  background-color: var(--lightest-gray);
}

/* 页面标题 */
.page-header {
  margin-bottom: 25px;
  padding: 0;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

/* 我的预约区域 */
.my-reservations-section {
  margin-bottom: 25px;
}

.reservations-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
}

.reservations-card:hover {
  box-shadow: var(--shadow-md);
}

/* 卡片头部 */
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

.refresh-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  padding: 6px 12px;
  font-size: 12px;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--secondary-light));
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* 加载状态 */
.loading-container {
  padding: 40px 20px;
}

/* 预约表格 */
.reservations-table {
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 0;
}

.reservations-table :deep(.el-table__header-wrapper) {
  background-color: var(--lightest-gray);
}

.reservations-table :deep(.el-table__body tr) {
  transition: all var(--transition-fast);
}

.reservations-table :deep(.el-table__body tr:hover) {
  background-color: var(--lightest-gray);
  transform: translateX(4px);
}

.reservations-table :deep(.el-table__body td) {
  padding: 12px 16px;
  border-bottom: 1px solid var(--light-gray);
}

.reservations-table :deep(.el-table__body tr.reservation-cancelled) {
  background-color: rgba(245, 101, 101, 0.05);
}

.reservations-table :deep(.el-table__body tr.reservation-cancelled:hover) {
  background-color: rgba(245, 101, 101, 0.1);
}

.reservations-table :deep(.el-table__body tr.reservation-completed) {
  background-color: rgba(72, 187, 120, 0.05);
}

.reservations-table :deep(.el-table__body tr.reservation-completed:hover) {
  background-color: rgba(72, 187, 120, 0.1);
}

.total-cost {
  font-weight: 600;
  color: var(--primary-color);
}

.no-action {
  color: var(--text-light);
  font-size: 14px;
}

/* 主要内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 25px;
  align-items: start;
}

/* 左侧区域 */
.left-section {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* 停车场选择卡片 */
.parking-lot-select-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
}

.parking-lot-select-card:hover {
  box-shadow: var(--shadow-md);
}

.lot-select {
  width: 100%;
  font-size: 16px;
  padding: 12px 0;
}

/* 费用计算卡片 */
.fee-calculator-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
}

.fee-calculator-card:hover {
  box-shadow: var(--shadow-md);
}

.fee-form {
  width: 100%;
}

.form-item {
  margin-bottom: 20px;
}

.date-picker {
  width: 100%;
}

.input {
  width: 100%;
  font-size: 14px;
}

.total-cost-input {
  font-weight: 600;
  color: var(--primary-color);
}

/* 右侧区域 */
.right-section {
  width: 100%;
}

.parking-spaces-card {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  border: none;
  height: 100%;
}

.parking-spaces-card:hover {
  box-shadow: var(--shadow-md);
}

/* 空状态 */
.empty-state {
  padding: 60px 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--lightest-gray);
  border-radius: var(--border-radius-sm);
}

/* 车位表格 */
.parking-spaces-table {
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 0;
}

.parking-spaces-table :deep(.el-table__header-wrapper) {
  background-color: var(--lightest-gray);
}

.parking-spaces-table :deep(.el-table__body tr) {
  transition: all var(--transition-fast);
}

.parking-spaces-table :deep(.el-table__body tr:hover) {
  background-color: var(--lightest-gray);
  transform: translateX(4px);
}

.parking-spaces-table :deep(.el-table__body td) {
  padding: 12px 16px;
  border-bottom: 1px solid var(--light-gray);
}

/* 车位状态行样式 */
.parking-spaces-table :deep(.el-table__body tr.space-free) {
  background-color: rgba(72, 187, 120, 0.05);
}

.parking-spaces-table :deep(.el-table__body tr.space-free:hover) {
  background-color: rgba(72, 187, 120, 0.1);
}

.parking-spaces-table :deep(.el-table__body tr.space-booked) {
  background-color: rgba(237, 137, 54, 0.05);
}

.parking-spaces-table :deep(.el-table__body tr.space-booked:hover) {
  background-color: rgba(237, 137, 54, 0.1);
}

.parking-spaces-table :deep(.el-table__body tr.space-occupied) {
  background-color: rgba(245, 101, 101, 0.05);
}

.parking-spaces-table :deep(.el-table__body tr.space-occupied:hover) {
  background-color: rgba(245, 101, 101, 0.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .left-section {
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .reservations-table :deep(.el-table__body td),
  .parking-spaces-table :deep(.el-table__body td) {
    padding: 10px 8px;
    font-size: 13px;
  }
  
  .el-button {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  .total-cost {
    font-size: 13px;
  }
  
  .date-picker,
  .input {
    font-size: 13px;
  }
}
</style>
    