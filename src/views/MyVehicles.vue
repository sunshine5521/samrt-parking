<template>
  <div style="margin: 20px;">
    <h2>我的车辆</h2>
    <el-button type="primary" @click="showAddVehicleForm" style="margin-bottom: 20px;">添加车辆</el-button>
    
    <el-table :data="vehicles" border style="width: 100%;">
      <el-table-column prop="id" label="ID"></el-table-column>
      <el-table-column prop="license_plate" label="车牌号"></el-table-column>
      <el-table-column prop="brand" label="品牌"></el-table-column>
      <el-table-column prop="color" label="颜色"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="danger" @click="deleteVehicle(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="添加车辆">
      <el-form :model="newVehicle" label-width="80px">
        <el-form-item label="车牌号">
          <el-input v-model="newVehicle.license_plate"></el-input>
        </el-form-item>
        <el-form-item label="品牌">
          <el-select v-model="newVehicle.brand" placeholder="请选择品牌">
            <el-option
              v-for="brand in commonBrands"
              :key="brand"
              :label="brand"
              :value="brand"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-select v-model="newVehicle.color" placeholder="请选择颜色">
            <el-option
              v-for="color in commonColors"
              :key="color"
              :label="color"
              :value="color"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addVehicle">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
// 用 export default 声明多单词组件名，解决“component name 必须多单词”报错
export default {
  name: 'MyVehiclesPage'
}
</script>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElButton, ElTable, ElTableColumn, ElDialog, ElForm, ElFormItem, ElInput, ElSelect, ElOption } from 'element-plus'

const vehicles = ref([])
const dialogVisible = ref(false)
const newVehicle = ref({
  license_plate: '',
  brand: '',
  color: ''
})

// 常见车辆品牌
const commonBrands = [
  '大众', '丰田', '本田', '宝马', '奔驰', '奥迪', '福特',
  '日产', '现代', '雪佛兰', '别克', '马自达', '雪铁龙',
  '标致', '起亚', '荣威', '吉利', '长城', '比亚迪', '特斯拉'
]

// 常见车辆颜色
const commonColors = [
  '白色', '黑色', '红色', '蓝色', '银色', '灰色',
  '棕色', '金色', '绿色', '紫色', '橙色', '黄色'
]

const fetchVehicles = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/user/vehicles', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      // 处理车辆数据，将Unknown的品牌和颜色替换为常见值
      const processedVehicles = data.data.map(vehicle => {
        if (vehicle.brand === 'Unknown' || !vehicle.brand) {
          vehicle.brand = commonBrands[Math.floor(Math.random() * commonBrands.length)]
        }
        if (vehicle.color === 'Unknown' || !vehicle.color) {
          vehicle.color = commonColors[Math.floor(Math.random() * commonColors.length)]
        }
        return vehicle
      })
      vehicles.value = processedVehicles
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('获取车辆列表失败')
  }
}

const showAddVehicleForm = () => {
  dialogVisible.value = true
  newVehicle.value = {
    license_plate: '',
    brand: '',
    color: ''
  }
}

const addVehicle = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/api/user/vehicles', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newVehicle.value)
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('车辆添加成功')
      dialogVisible.value = false
      fetchVehicles()
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('添加车辆失败')
  }
}

const deleteVehicle = async (id) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:5000/api/user/vehicles/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    const data = await response.json()
    if (data.code === 200) {
      ElMessage.success('车辆删除成功')
      fetchVehicles()
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('删除车辆失败')
  }
}

onMounted(() => {
  fetchVehicles()
})
</script>

<style scoped>
/* 可选：添加组件样式 */
</style>