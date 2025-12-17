<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 全局样式变量 */
:root {
  /* 主题色 */
  --primary-color: #667eea;
  --primary-light: #7c8ff0;
  --primary-dark: #5a6fd8;
  --secondary-color: #764ba2;
  --secondary-light: #8a5cb8;
  --secondary-dark: #674188;
  
  /* 功能色 */
  --success-color: #48bb78;
  --warning-color: #ed8936;
  --danger-color: #f56565;
  --info-color: #4299e1;
  
  /* 中性色 */
  --lightest-gray: #f7fafc;
  --light-gray: #edf2f7;
  --medium-gray: #e2e8f0;
  --dark-gray: #a0aec0;
  --darker-gray: #4a5568;
  --darkest-gray: #2d3748;
  
  /* 文本色 */
  --text-primary: #2d3748;
  --text-secondary: #718096;
  --text-light: #a0aec0;
  
  /* 边框和阴影 */
  --border-radius: 12px;
  --border-radius-sm: 8px;
  --border-radius-lg: 16px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
  
  /* 过渡动画 */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;
  
  /* 字体 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 全局重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  background-color: var(--lightest-gray);
  line-height: 1.6;
  font-size: 14px;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* 通用容器样式 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  padding: 24px;
  transition: all var(--transition-normal);
  margin-bottom: 20px;
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  font-size: 14px;
  transition: all var(--transition-normal);
  cursor: pointer;
  border: none;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  background: linear-gradient(135deg, var(--primary-light), var(--secondary-light));
}

.btn-secondary {
  background-color: var(--light-gray);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background-color: var(--medium-gray);
  transform: translateY(-1px);
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--medium-gray);
  border-radius: var(--border-radius-sm);
  font-size: 14px;
  transition: all var(--transition-normal);
  background-color: white;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 表格样式 */
.table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.table th,
.table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid var(--light-gray);
}

.table th {
  background-color: var(--lightest-gray);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table tr {
  transition: background-color var(--transition-fast);
}

.table tr:hover {
  background-color: var(--lightest-gray);
}

.table tr:last-child td {
  border-bottom: none;
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 16px;
}

h1 {
  font-size: 32px;
}

h2 {
  font-size: 28px;
}

h3 {
  font-size: 24px;
}

h4 {
  font-size: 20px;
}

h5 {
  font-size: 18px;
}

h6 {
  font-size: 16px;
}

/* 文本样式 */
p {
  margin-bottom: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
}

a {
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--secondary-color);
  text-decoration: underline;
}

/* 辅助类 */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 16px; }
.mt-4 { margin-top: 24px; }
.mt-5 { margin-top: 32px; }

.mb-1 { margin-bottom: 4px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 16px; }
.mb-4 { margin-bottom: 24px; }
.mb-5 { margin-bottom: 32px; }

.ml-1 { margin-left: 4px; }
.ml-2 { margin-left: 8px; }
.ml-3 { margin-left: 16px; }
.ml-4 { margin-left: 24px; }
.ml-5 { margin-left: 32px; }

.mr-1 { margin-right: 4px; }
.mr-2 { margin-right: 8px; }
.mr-3 { margin-right: 16px; }
.mr-4 { margin-right: 24px; }
.mr-5 { margin-right: 32px; }

.p-1 { padding: 4px; }
.p-2 { padding: 8px; }
.p-3 { padding: 16px; }
.p-4 { padding: 24px; }
.p-5 { padding: 32px; }

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 过渡动画 */
.fade-in {
  animation: fadeIn 0.5s ease-out;
}

.slide-up {
  animation: slideUp 0.5s ease-out;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  
  .card {
    padding: 20px;
  }
  
  h1 {
    font-size: 28px;
  }
  
  h2 {
    font-size: 24px;
  }
  
  .table {
    display: block;
    overflow-x: auto;
  }
}
</style>