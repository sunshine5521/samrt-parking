<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">智慧停车管理系统</div>
      <div class="user-info">
        <span>欢迎，{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </header>
    
    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <el-menu :default-active="activeMenu" class="sidebar-menu" router>
          <!-- 用户菜单 -->
          <el-menu-item index="/parking-lots">
            <el-icon><MapLocation /></el-icon>
            <span>停车场列表</span>
          </el-menu-item>
          <el-menu-item index="/my-vehicles">
            <el-icon><Van /></el-icon>
            <span>我的车辆</span>
          </el-menu-item>
          <el-menu-item index="/reservation">
            <el-icon><Ticket /></el-icon>
            <span>车位预定</span>
          </el-menu-item>
          <el-menu-item index="/parking-records">
            <el-icon><Document /></el-icon>
            <span>停车记录</span>
          </el-menu-item>
          <el-menu-item index="/violations">
            <el-icon><Warning /></el-icon>
            <span>违规记录</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </el-menu-item>

          <!-- 管理员菜单 -->
          <el-menu-item index="/admin/parking-lot-management" v-if="userRole === 'admin'">
            <el-icon><Setting /></el-icon>
            <span>停车场管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/data-analysis" v-if="userRole === 'admin'">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <!-- 内容区域 -->
      <main class="content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LayoutContainer'
}
</script>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MapLocation, Van, Ticket, Document, Warning, User, Setting, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('用户')
const userRole = ref('user')

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 获取用户信息
const fetchUserInfo = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const response = await fetch('http://127.0.0.1:5000/api/user/profile', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      username.value = data.username
      userRole.value = data.role || 'user'
      localStorage.setItem('role', userRole.value)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('role')
  ElMessage.success('退出登录成功')
  router.push('/login')
}

// 页面挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
  userRole.value = localStorage.getItem('role') || 'user'
})
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e8e8e8;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 25px;
  font-size: 14px;
  font-weight: 500;
}

.user-info span {
  color: #555;
}

.user-info .el-button {
  color: #667eea;
  border-color: #667eea;
  padding: 6px 18px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.user-info .el-button:hover {
  background-color: #667eea;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  margin: 10px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background-color: white;
}

.sidebar {
  width: 220px;
  background-color: #f8fafc;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  padding: 10px 0;
}

.sidebar-menu {
  border-right: none !important;
  height: 100%;
}

.sidebar-menu :deep(.el-menu-item) {
  padding: 12px 20px !important;
  margin: 0 10px;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.3s ease;
  color: #475569;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #e2e8f0;
  color: #2d3748;
  transform: translateX(5px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #5568d3 0%, #65408c 100%);
}

.content {
  flex: 1;
  padding: 25px;
  overflow-y: auto;
  background-color: #fafafa;
}
</style>