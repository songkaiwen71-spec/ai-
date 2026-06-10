<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="navbar-content">
        <div class="logo">
          <span class="logo-icon">📊</span>
          <span class="logo-text">大数据舆情可视化分析</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <span class="nav-icon">📈</span>
            数据大屏
          </router-link>
          <router-link to="/crawl" class="nav-link" :class="{ active: $route.path === '/crawl' }">
            <span class="nav-icon">🕷️</span>
            爬虫控制
          </router-link>
        </div>
        <div class="nav-time">
          <span class="time-label">当前时间</span>
          <span class="time-value">{{ currentTime }}</span>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 底部信息 -->
    <footer class="footer">
      <div class="footer-content">
        <span>大数据舆情可视化分析系统 v1.0</span>
        <span class="separator">|</span>
        <span>基于 Vue3 + Flask</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 当前时间
const currentTime = ref('')
let timeTimer = null

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeTimer) {
    clearInterval(timeTimer)
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f4e 50%, #0a0e27 100%);
}

/* 导航栏 */
.navbar {
  height: 70px;
  background: rgba(10, 14, 39, 0.9);
  border-bottom: 1px solid rgba(79, 195, 247, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.navbar-content {
  max-width: 1920px;
  margin: 0 auto;
  height: 100%;
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, #4fc3f7, #29b6f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(79, 195, 247, 0.1);
  color: #4fc3f7;
}

.nav-link.active {
  background: rgba(79, 195, 247, 0.2);
  color: #4fc3f7;
}

.nav-icon {
  font-size: 16px;
}

.nav-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.time-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.time-value {
  font-size: 14px;
  color: #4fc3f7;
  font-family: 'Courier New', monospace;
}

/* 主内容 */
.main-content {
  flex: 1;
  padding: 20px 30px;
  max-width: 1920px;
  margin: 0 auto;
  width: 100%;
}

/* 底部 */
.footer {
  height: 50px;
  background: rgba(10, 14, 39, 0.9);
  border-top: 1px solid rgba(79, 195, 247, 0.2);
}

.footer-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.separator {
  opacity: 0.3;
}

/* 响应式 */
@media (max-width: 768px) {
  .navbar-content {
    padding: 0 15px;
  }

  .logo-text {
    display: none;
  }

  .nav-link {
    padding: 8px 12px;
    font-size: 13px;
  }

  .nav-time {
    display: none;
  }

  .main-content {
    padding: 15px;
  }
}
</style>
