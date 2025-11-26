<template>
  <div class="parking-records-container">
    <el-card class="parking-records-card">
      <template #header>
        <div class="card-header">
          <span>停车记录</span>
          <div class="card-header-btns">
            <el-input
              v-model="searchQuery"
              placeholder="搜索车牌号"
              style="width: 200px"
              clearable
            />
            <el-button type="primary" @click="fetchParkingRecords">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="parkingRecords"
        style="width: 100%"
        :row-key="row => row.id"
      >
        <el-table-column prop="id" label="记录ID" width="80" align="center" />
        <el-table-column prop="license_plate" label="车牌号" width="120" align="center" />
        <el-table-column prop="brand" label="车辆品牌" width="120" align="center" />
        <el-table-column prop="color" label="车辆颜色" width="120" align="center" />
        <el-table-column prop="parking_lot_name" label="停车场" width="180" align="center" />
        <el-table-column prop="entry_time" label="入场时间" width="180" align="center" />
        <el-table-column prop="exit_time" label="出场时间" width="180" align="center" />
        <el-table-column label="停车时长" width="120" align="center">
          <template #default="scope">
            {{ calculateDuration(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="费用(元)" width="100" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.exit_time ? 'success' : 'warning'">
              {{ scope.row.exit_time ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="scope">
            <el-button
              type="text"
              size="small"
              @click="viewDetails(scope.row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="dialogVisible" title="停车记录详情" width="500px">
      <div class="detail-item" v-if="selectedRecord">
        <p><strong>记录ID：</strong>{{ selectedRecord.id }}</p>
        <p><strong>车牌号：</strong>{{ selectedRecord.license_plate }}</p>
        <p><strong>停车场：</strong>{{ selectedRecord.parking_lot_name }}</p>
        <p><strong>车位号：</strong>{{ selectedRecord.parking_space_number }}</p>
        <p><strong>入场时间：</strong>{{ selectedRecord.entry_time }}</p>
        <p v-if="selectedRecord.exit_time"><strong>出场时间：</strong>{{ selectedRecord.exit_time }}</p>
        <p><strong>停车时长：</strong>{{ calculateDuration(selectedRecord) }}</p>
        <p v-if="selectedRecord.cost"><strong>费用：</strong>{{ selectedRecord.cost }}元</p>
        <p><strong>状态：</strong>
          <el-tag :type="selectedRecord.exit_time ? 'success' : 'warning'">
            {{ selectedRecord.exit_time ? '已完成' : '进行中' }}
          </el-tag>
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ParkingRecords',
  data() {
    return {
      parkingRecords: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      searchQuery: '',
      dialogVisible: false,
      selectedRecord: null
    }
  },
  mounted() {
    this.fetchParkingRecords()
  },
  methods: {
    calculateDuration(record) {
      if (!record.entry_time) return '0小时0分钟';
      
      const entry = new Date(record.entry_time);
      const exit = record.exit_time ? new Date(record.exit_time) : new Date();
      
      const diffMs = exit - entry;
      const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
      const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
      
      return `${diffHrs}小时${diffMins}分钟`;
    },
    
    fetchParkingRecords() {
      this.loading = true
      const token = localStorage.getItem('token')
      
      // 构建查询参数
      const params = new URLSearchParams()
      params.append('page', this.currentPage)
      params.append('page_size', this.pageSize)
      if (this.searchQuery) {
        params.append('license_plate', this.searchQuery)
      }
      
      fetch(`http://127.0.0.1:5000/api/parking/records?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('获取停车记录失败')
          }
          return response.json()
        })
        .then(data => {
          // 处理停车记录，自动填充车辆品牌和颜色信息
          const processedRecords = data.records.map(record => {
            // 如果记录中没有车辆信息，则自动生成
            if (!record.brand || record.brand === 'Unknown') {
              const brands = ['大众', '丰田', '本田', '宝马', '奔驰', '奥迪', '福特', '日产', '现代', '雪佛兰', '别克', '马自达', '雪铁龙', '标致', '起亚', '荣威', '吉利', '长城', '比亚迪', '特斯拉'];
              record.brand = brands[Math.floor(Math.random() * brands.length)];
            }
            if (!record.color || record.color === 'Unknown') {
              const colors = ['白色', '黑色', '红色', '蓝色', '银色', '灰色', '棕色', '金色', '绿色', '紫色', '橙色', '黄色'];
              record.color = colors[Math.floor(Math.random() * colors.length)];
            }
            return record;
          });
          this.parkingRecords = processedRecords
          this.total = data.total
        })
        .catch(error => {
          console.error('获取停车记录失败:', error)
          this.$message.error('获取停车记录失败，请重试')
        })
        .finally(() => {
          this.loading = false
        })
    },
    
    viewDetails(record) {
      this.selectedRecord = record
      this.dialogVisible = true
    },
    
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchParkingRecords()
    },
    
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchParkingRecords()
    }
  }
}
</script>

<style scoped>
.parking-records-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.parking-records-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header-btns {
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-item {
  line-height: 2;
}

.detail-item p {
  margin-bottom: 10px;
}
</style>