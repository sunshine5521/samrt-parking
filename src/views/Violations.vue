<template>
  <div class="violations-container">
    <el-card class="violations-card">
      <template #header>
        <div class="card-header">
          <span>违规记录</span>
          <div class="card-header-btns">
            <el-input
              v-model="searchQuery"
              placeholder="搜索车牌号"
              style="width: 200px"
              clearable
            />
            <el-button type="primary" @click="fetchViolations">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="violations"
        style="width: 100%"
        :row-key="row => row.id"
      >
        <el-table-column prop="id" label="记录ID" width="80" align="center" />
        <el-table-column prop="license_plate" label="车牌号" width="120" align="center" />
        <el-table-column prop="brand" label="车辆品牌" width="120" align="center" />
        <el-table-column prop="color" label="车辆颜色" width="120" align="center" />
        <el-table-column prop="parking_lot_name" label="停车场" width="180" align="center" />
        <el-table-column prop="violation_type" label="违规类型" width="120" align="center" />
        <el-table-column prop="violation_time" label="违规时间" width="180" align="center" />
        <el-table-column prop="fine_amount" label="罚款金额(元)" width="120" align="center" />
        <el-table-column prop="status" label="处理状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'paid' ? 'success' : 'danger'">
              {{ scope.row.status === 'paid' ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handlePayment(scope.row)"
              :disabled="scope.row.status === 'paid'"
            >
              {{ scope.row.status === 'paid' ? '已支付' : '支付' }}
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

    <!-- 支付对话框 -->
    <el-dialog v-model="paymentDialogVisible" title="违规罚款支付" width="400px">
      <div v-if="selectedViolation" class="payment-info">
        <p><strong>违规类型：</strong>{{ selectedViolation.violation_type }}</p>
        <p><strong>违规时间：</strong>{{ selectedViolation.violation_time }}</p>
        <p><strong>罚款金额：</strong>{{ selectedViolation.fine_amount }}元</p>
        <p><strong>违规描述：</strong>{{ selectedViolation.description }}</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="paymentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmPayment">确认支付</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ViolationRecords',
  data() {
    return {
      violations: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      searchQuery: '',
      paymentDialogVisible: false,
      selectedViolation: null
    }
  },
  mounted() {
    this.fetchViolations()
  },
  methods: {
    fetchViolations() {
      this.loading = true
      const token = localStorage.getItem('token')
      
      // 构建查询参数
      const params = new URLSearchParams()
      params.append('page', this.currentPage)
      params.append('page_size', this.pageSize)
      if (this.searchQuery) {
        params.append('license_plate', this.searchQuery)
      }
      
      fetch(`http://127.0.0.1:5000/api/violations?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('获取违规记录失败')
          }
          return response.json()
        })
        .then(data => {
          this.violations = data.violations
          this.total = data.total
        })
        .catch(error => {
          console.error('获取违规记录失败:', error)
          this.$message.error('获取违规记录失败，请重试')
        })
        .finally(() => {
          this.loading = false
        })
    },
    
    handlePayment(violation) {
      this.selectedViolation = violation
      this.paymentDialogVisible = true
    },
    
    confirmPayment() {
      const token = localStorage.getItem('token')
      
      fetch(`http://127.0.0.1:5000/api/violations/${this.selectedViolation.id}/pay`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('支付失败')
          }
          return response.json()
        })
        .then(() => {
          this.$message.success('支付成功')
          this.paymentDialogVisible = false
          this.fetchViolations()
        })
        .catch(error => {
          console.error('支付失败:', error)
          this.$message.error('支付失败，请重试')
        })
    },
    
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchViolations()
    },
    
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchViolations()
    }
  }
}
</script>

<style scoped>
.violations-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.violations-card {
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

.payment-info {
  line-height: 2;
  margin-bottom: 20px;
}

.payment-info p {
  margin-bottom: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>