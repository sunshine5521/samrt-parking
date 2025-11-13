<template>
  <div style="margin: 20px;">
    <h2>停车场列表</h2>
    <el-table :data="parkingLots" border style="width: 100%">
      <el-table-column prop="id" label="ID"></el-table-column>
      <el-table-column prop="name" label="名称"></el-table-column>
      <el-table-column prop="location_gps" label="GPS坐标"></el-table-column>
      <el-table-column prop="capacity" label="总车位"></el-table-column>
      <el-table-column prop="free_spaces" label="空闲车位"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="primary" @click="viewSpace(scope.row.id)">查看车位</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElTable, ElTableColumn, ElButton } from 'element-plus'
import { useRouter } from 'vue-router'

const parkingLots = ref([])
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
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('获取停车场列表失败')
  }
}

const viewSpace = (lotId) => {
  router.push({ path: '/reservation', query: { lotId } })
}

onMounted(() => {
  fetchParkingLots()
})
</script>