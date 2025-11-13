import { createRouter, createWebHistory } from 'vue-router'
// 从路由文件夹（src/router）到视图文件夹（src/views）需用 ../ 表示上一级目录
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../components/Layout.vue'
import ParkingLots from '../views/ParkingLots.vue'
import MyVehicles from '../views/MyVehicles.vue'
import MakeReservation from '../views/MakeReservation.vue'
import ParkingRecords from '../views/ParkingRecords.vue'
import Violations from '../views/Violations.vue'
import Profile from '../views/Profile.vue'
// 导入管理员页面组件
import ParkingLotManagement from '../views/Admin/ParkingLotManagement.vue'
import DataAnalysis from '../views/Admin/DataAnalysis.vue'

// 路由规则配置
const routes = [
  { path: '/', redirect: '/login' }, // 根路径自动跳转到登录页
  { path: '/login', component: Login }, // 登录页
  { path: '/register', component: Register }, // 注册页
  
  // 主布局路由（需要登录权限）
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      // 停车场列表
      { 
        path: 'parking-lots', 
        component: ParkingLots 
      },
      // 我的车辆
      { 
        path: 'my-vehicles', 
        component: MyVehicles 
      },
      // 车位预定
      { 
        path: 'reservation', 
        component: MakeReservation 
      },
      // 停车记录
      { 
        path: 'parking-records', 
        component: ParkingRecords 
      },
      // 违规记录
      { 
        path: 'violations', 
        component: Violations 
      },
      // 个人中心
      {
        path: 'profile',
        component: Profile
      },
      // 管理员功能
      {
        path: 'admin/parking-lot-management',
        component: ParkingLotManagement,
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/data-analysis',
        component: DataAnalysis,
        meta: { requiresAdmin: true }
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // HTML5 history模式（无#号）
  routes // 注入路由规则
})

// 路由守卫：验证登录状态和权限
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') || 'user'

  // 未登录用户访问受保护页面时，强制跳转到登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && role !== 'admin') {
    next('/parking-lots')
    return
  }

  next() // 已登录或无需权限，正常跳转
})

export default router