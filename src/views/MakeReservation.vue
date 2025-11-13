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
    <el-table :data="parkingSpaces" border style="width: 100%; margin-top: 20px;">
      <el-table-column prop="id" label="车位ID"></el-table-column>
      <el-table-column prop="number" label="车位编号"></el-table-column>
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
import { ElMessage, ElSelect, ElOption, ElTable, ElTableColumn, ElButton, ElTag } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'

const parkingLots = ref([])
const parkingSpaces = ref([])
const selectedLotId = ref('')
const route = useRoute()
const router = useRouter()

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
        selectedLotId.value = route.query.lotId
      }
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('获取停车场列表失败')
  }
}

watch(selectedLotId, async (newLotId) => {
  if (newLotId) {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://127.0.0.1:5000/api/parking/space?lot_id=${newLotId}`, {
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
  const user_id = localStorage.getItem('user_id')
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
  const vehicle_id = vehiclesData.data[0].id

  const start_time = new Date().toISOString()
  const end_time = new Date(Date.now() + 3600 * 1000).toISOString()

  try {
    const response = await fetch('http://127.0.0.1:5000/api/reservation', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        vehicle_id,
        parking_lot_id: selectedLotId.value,
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
      const response = await fetch(`http://127.0.0.1:5000/api/parking/space?lot_id=${selectedLotId.value}`, {
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
    