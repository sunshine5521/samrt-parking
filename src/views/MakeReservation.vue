<template>
  <div style="margin: 20px;">
    <h2>车位预定</h2>
    <el-select v-model="selectedLotId" placeholder="选择停车场">
      <el-option
        v-for="lot in parkingLots"
        :key="lot.id"
        :label="lot.name"
        :value="lot.id"
      ></el-option>
    </el-select>

    <!-- 费用计算部分 -->
    <div v-if="selectedLot" style="margin-top: 20px;">
      <h3>费用计算</h3>
      <el-form :model="feeForm" label-width="120px">
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="feeForm.startTime"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 200px;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="feeForm.endTime"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 200px;"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="时薪">
          <el-input
            v-model="selectedLot.hourly_rate"
            readonly
            style="width: 200px;"
          ></el-input>
        </el-form-item>
        <el-form-item label="总费用">
          <el-input
            v-model="totalFee"
            readonly
            style="width: 200px;"
          ></el-input>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="parkingSpaces" border style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="车位ID"></el-table-column>
      <el-table-column prop="space_number" label="车位编号"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag v-if="scope.row.status === 'free'" type="success">空闲</el-tag>
          <el-tag v-else-if="scope.row.status === 'booked' || scope.row.status === 'reserved'" type="warning">已被预订</el-tag>
          <el-tag v-else type="danger">已占用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" v-if="selectedLotId">
        <template #default="scope">
          <el-button 
            v-if="scope.row.status === 'free'" 
            type="primary" 
            @click="makeReservation(scope.row.id)"
          >
            预定
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElSelect, ElOption, ElTable, ElTableColumn, ElButton, ElTag, ElDatePicker, ElForm, ElFormItem, ElInput } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'

const parkingLots = ref([])
const parkingSpaces = ref([])
const selectedLotId = ref(null)
const route = useRoute()
const router = useRouter()

// 费用计算相关变量
const selectedLot = ref(null)
const feeForm = ref({
  startTime: null,
  endTime: null
})
const totalFee = ref(0)

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
    feeForm.value.startTime = null
    feeForm.value.endTime = null
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

  const user_id = localStorage.getItem('user_id')
  let vehicle_id;
  try {
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
  } catch (error) {
    ElMessage.error('获取车辆信息失败')
    return
  }

  // 使用用户选择的时间或默认值
  const start_time = feeForm.value.startTime 
    ? new Date(feeForm.value.startTime).toISOString() 
    : new Date().toISOString()
  const end_time = feeForm.value.endTime 
    ? new Date(feeForm.value.endTime).toISOString() 
    : new Date(Date.now() + 3600 * 1000).toISOString()

  try {
    // 确保selectedLotId是数字类型
    const lotId = parseInt(selectedLotId.value)
    const response = await fetch('http://127.0.0.1:5000/api/reservation', {
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
  if (selectedLotId.value) {
    try {
      const token = localStorage.getItem('token')
      // 确保selectedLotId是数字类型
      const lotId = parseInt(selectedLotId.value)
      const response = await fetch(`http://127.0.0.1:5000/api/parking/spaces?lot_id=${lotId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const spaceData = await response.json()
      if (spaceData.code === 200) {
        parkingSpaces.value = spaceData.data
      }
    } catch (error) {
      ElMessage.error('刷新车位列表失败')
    }
  }
} else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('预定失败')
  }
}

onMounted(() => {
  fetchParkingLots()
})
</script>
    