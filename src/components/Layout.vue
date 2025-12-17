<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <el-icon class="logo-icon"><Van /></el-icon>
          <span>智慧停车管理系统</span>
        </div>
      </div>
      <div class="header-right">
        <!-- 通知图标 -->
        <el-popover
          placement="bottom"
          title="通知"
          width="300"
          trigger="click"
          :hide-after="0"
        >
          <template #reference>
            <el-button type="text" class="header-btn notification-btn">
              <el-icon><Bell /></el-icon>
              <span class="notification-badge">3</span>
            </el-button>
          </template>
          <div class="notification-content">
            <div v-for="i in 3" :key="i" class="notification-item">
              <el-icon class="notification-icon"><Warning /></el-icon>
              <div class="notification-text">
                <div class="notification-title">新通知 {{ i }}</div>
                <div class="notification-desc">这是一条测试通知内容</div>
              </div>
            </div>
          </div>
        </el-popover>
        <!-- 用户信息 -->
        <div class="user-info">
          <el-dropdown @command="handleUserCommand">
            <span class="user-dropdown">
              <el-avatar :size="36" class="user-avatar">{{ username && username.charAt(0) || '用' }}</el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>
    
    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <el-icon class="sidebar-logo"><MapLocation /></el-icon>
          <span>菜单导航</span>
        </div>
        <el-menu 
          :default-active="activeMenu" 
          class="sidebar-menu" 
          router
          :collapse-transition="true"
        >


        <!-- 用户菜单 -->
          <template v-if="userRole !== 'admin'">
            <el-menu-item index="/parking-lots">
              <el-icon><MapLocation /></el-icon>
              <template #title>
                <span class="menu-text">停车场列表</span>
                <span class="menu-badge">12</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/my-vehicles">
              <el-icon><Van /></el-icon>
              <template #title>
                <span class="menu-text">我的车辆</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/reservation">
              <el-icon><Ticket /></el-icon>
              <template #title>
                <span class="menu-text">车位预定</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/parking-records">
              <el-icon><Document /></el-icon>
              <template #title>
                <span class="menu-text">停车记录</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/violations">
              <el-icon><Warning /></el-icon>
              <template #title>
                <span class="menu-text">违规记录</span>
                <span class="menu-badge danger">2</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <template #title>
                <span class="menu-text">个人中心</span>
              </template>
            </el-menu-item>
          </template>

          <!-- 管理员菜单 -->
          <el-sub-menu index="/admin" v-if="userRole === 'admin'">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>管理中心</span>
            </template>
            <el-menu-item index="/admin/data-analysis">
              <el-icon><DataAnalysis /></el-icon>
              <template #title>
                <span class="menu-text">数据分析</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/revenue-statistics">
              <el-icon><Money /></el-icon>
              <template #title>
                <span class="menu-text">收入统计</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/parking-records">
              <el-icon><Document /></el-icon>
              <template #title>
                <span class="menu-text">停车记录管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/reservation-management">
              <el-icon><Ticket /></el-icon>
              <template #title>
                <span class="menu-text">预约记录管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/parking-lot-management">
              <el-icon><Location /></el-icon>
              <template #title>
                <span class="menu-text">停车场管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/parking-space-management">
              <el-icon><Location /></el-icon>
              <template #title>
                <span class="menu-text">车位管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/vehicle-management">
              <el-icon><Van /></el-icon>
              <template #title>
                <span class="menu-text">车辆管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/violation-management">
              <el-icon><Warning /></el-icon>
              <template #title>
                <span class="menu-text">违规管理</span>
              </template>
            </el-menu-item>
            <el-menu-item index="/admin/user-management">
              <el-icon><User /></el-icon>
              <template #title>
                <span class="menu-text">用户管理</span>
              </template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>
      
      <!-- 内容区域 -->
      <main class="content">
        <div class="content-header">
          <h1 class="page-title">{{ getPageTitle() }}</h1>
          <div class="page-actions">
            <slot name="actions"></slot>
          </div>
        </div>
        <div class="content-body">
          <router-view></router-view>
        </div>
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
import {
  MapLocation, Van, Ticket, Document, Warning, User, Setting, 
  DataAnalysis, Bell, ArrowDown, SwitchButton, Location, Money
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('用户')
const userRole = ref('user')

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 页面标题映射
const pageTitleMap = {
  '/parking-lots': '停车场列表',
  '/my-vehicles': '我的车辆',
  '/reservation': '车位预定',
  '/parking-records': '停车记录',
  '/violations': '违规记录',
  '/profile': '个人中心',
  '/admin/parking-lot-management': '停车场管理',
  '/admin/vehicle-management': '车辆管理',
  '/admin/data-analysis': '数据分析',
  '/admin/revenue-statistics': '收入统计',
  '/admin/parking-records': '停车记录管理',
  '/admin/reservation-management': '预约记录管理',
  '/admin/violation-management': '违规管理',
  '/admin/parking-space-management': '车位管理',
  '/admin/user-management': '用户管理'
}

// 获取当前页面标题
const getPageTitle = () => {
  return pageTitleMap[route.path] || '智慧停车管理系统'
}

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
      const result = await response.json()
      if (result.code === 200) {
        const data = result.data
        username.value = data.username
        userRole.value = data.role || 'user'
        localStorage.setItem('role', userRole.value)
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 用户下拉菜单命令处理
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('设置功能开发中')
      break
    case 'logout':
      logout()
      break
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
/* 全局样式变量 */
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #48bb78;
  --warning-color: #ed8936;
  --danger-color: #f56565;
  --light-gray: #f7fafc;
  --medium-gray: #e2e8f0;
  --dark-gray: #4a5568;
  --border-radius: 12px;
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

/* 渐变背景动画 */
@keyframes gradientShift {
  0% { background-position: 0% 50% }
  50% { background-position: 100% 50% }
  100% { background-position: 0% 50% }
}

/* 顶部导航栏 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  height: 70px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(15px);
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e8e8e8;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-icon {
  font-size: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: logoPulse 2s ease-in-out infinite;
}

@keyframes logoPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  font-size: 20px;
  color: #666;
  transition: all 0.3s ease;
}

.header-btn:hover {
  color: #667eea;
  background-color: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  transform: translateY(-2px);
}

/* 通知按钮 */
.notification-btn {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  background-color: #f56565;
  color: white;
  border-radius: 9px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: notificationPulse 2s infinite;
}

@keyframes notificationPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 通知内容 */
.notification-content {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.notification-item:hover {
  background-color: #f8fafc;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  font-size: 20px;
  color: #ed8936;
  margin-top: 2px;
}

.notification-text {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: #333;
}

.notification-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 25px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.user-dropdown:hover {
  background-color: rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
}

.user-dropdown:hover .user-avatar {
  transform: scale(1.1);
}

.username {
  font-size: 14px;
  color: #333;
}

.dropdown-icon {
  font-size: 12px;
  color: #999;
  transition: transform 0.3s ease;
}

.user-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
  color: #667eea;
}

/* 主体内容 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  margin: 10px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background-color: white;
}

/* 侧边栏 */
.sidebar {
  width: 250px;
  background-color: #fafafa;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.sidebar:hover {
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-logo {
  font-size: 20px;
  color: #667eea;
}

/* 侧边栏菜单 */
.sidebar-menu {
  border-right: none !important;
  height: calc(100% - 65px);
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  padding: 14px 20px !important;
  margin: 0 10px;
  border-radius: 10px;
  margin-bottom: 4px;
  transition: all 0.3s ease;
  color: #475569;
  font-size: 14px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: rgba(102, 126, 234, 0.1);
  color: #2d3748;
  transform: translateX(5px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.sidebar-menu :deep(.el-menu-item.is-active:hover) {
  background: linear-gradient(135deg, #5568d3 0%, #65408c 100%);
  transform: translateX(5px);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
  font-size: 13px;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, #5568d3 0%, #65408c 100%);
}

.menu-text {
  font-weight: 500;
}

.menu-badge {
  display: inline-block;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 20px;
  background-color: #667eea;
  color: white;
  border-radius: 10px;
  text-align: center;
  margin-left: 8px;
  animation: badgePulse 2s infinite;
}

.menu-badge.danger {
  background-color: #f56565;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* 内容区域 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fafafa;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px 20px;
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.content-body {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: #fafafa;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar,
.content-body::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.sidebar::-webkit-scrollbar-track,
.content-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb,
.content-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
  transition: all 0.3s ease;
}

.sidebar::-webkit-scrollbar-thumb:hover,
.content-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 220px;
  }
  
  .content-header {
    padding: 20px 25px 15px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .content-body {
    padding: 25px;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 20px;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .username {
    display: none;
  }
  
  .main-content {
    margin: 5px;
  }
  
  .sidebar {
    width: 60px;
  }
  
  .sidebar-header {
    justify-content: center;
    padding: 15px 0;
  }
  
  .sidebar-header span {
    display: none;
  }
  
  .sidebar-menu :deep(.el-menu-item),
  .sidebar-menu :deep(.el-sub-menu__title) {
    padding: 14px 10px !important;
    justify-content: center;
  }
  
  .sidebar-menu :deep(.el-menu-item span),
  .sidebar-menu :deep(.el-sub-menu__title span) {
    display: none;
  }
  
  .menu-badge {
    display: none;
  }
}
</style>