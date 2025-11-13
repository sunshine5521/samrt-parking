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
            <el-icon><Car /></el-icon>
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
import { MapLocation, Car, Ticket, Document, Warning, User, Setting, DataAnalysis } from '@element-plus/icons-vue'

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
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #1E88E5;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  border-right: none !important;
  height: 100%;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>