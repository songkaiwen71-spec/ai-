<template>
  <div class="crawl-control">
    <div class="control-header">
      <h2>🕷️ 数据爬虫控制</h2>
      <p class="subtitle">从微博平台爬取指定话题的舆情数据</p>
    </div>

    <!-- 爬虫表单 -->
    <div class="crawl-form">
      <div class="form-card">
        <div class="card-title">📥 爬取设置</div>

        <div class="form-group">
          <label>搜索关键词</label>
          <input
            v-model="form.keyword"
            type="text"
            class="input"
            placeholder="请输入要搜索的微博关键词，如：人工智能、新能源汽车..."
          />
        </div>

        <div class="form-group">
          <label>爬取页数</label>
          <input
            v-model.number="form.pages"
            type="number"
            class="input"
            min="1"
            max="50"
            placeholder="1-50"
          />
          <span class="hint">每页约10条数据</span>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-primary"
            @click="handleCrawl"
            :disabled="loading"
          >
            {{ loading ? '爬取中...' : '🚀 开始爬取' }}
          </button>

          <button
            class="btn btn-secondary"
            @click="handleDemo"
            :disabled="loading"
          >
            📊 生成演示数据
          </button>

          <button
            class="btn btn-danger"
            @click="handleClear"
            :disabled="loading"
          >
            🗑️ 清空数据
          </button>
        </div>

        <!-- 爬取日志 -->
        <div class="log-section">
          <div class="log-header">
            <span class="log-title">📜 爬取日志</span>
            <button class="btn-text" @click="clearLog">清空</button>
          </div>
          <div class="log-content" ref="logContainer">
            <div
              v-for="(log, index) in logs"
              :key="index"
              :class="['log-item', `log-${log.type}`]"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="log-empty">
              暂无日志
            </div>
          </div>
        </div>
      </div>

      <!-- 数据统计 -->
      <div class="stats-card">
        <div class="card-title">📊 数据统计</div>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">数据总量</span>
          </div>
          <div class="stat-item">
            <span class="stat-value stat-positive">{{ stats.positive }}</span>
            <span class="stat-label">积极</span>
          </div>
          <div class="stat-item">
            <span class="stat-value stat-neutral">{{ stats.neutral }}</span>
            <span class="stat-label">中性</span>
          </div>
          <div class="stat-item">
            <span class="stat-value stat-negative">{{ stats.negative }}</span>
            <span class="stat-label">消极</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div class="history-section">
      <div class="history-card">
        <div class="card-title">📋 爬取记录</div>
        <div class="history-table">
          <table>
            <thead>
              <tr>
                <th>关键词</th>
                <th>开始时间</th>
                <th>状态</th>
                <th>总数</th>
                <th>成功</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in records" :key="record.id">
                <td>{{ record.keyword }}</td>
                <td>{{ formatTime(record.start_time) }}</td>
                <td>
                  <span :class="['status-tag', `status-${record.status}`]">
                    {{ getStatusText(record.status) }}
                  </span>
                </td>
                <td>{{ record.total_count }}</td>
                <td>{{ record.success_count }}</td>
              </tr>
              <tr v-if="records.length === 0">
                <td colspan="5" class="empty-row">暂无记录</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api'

// 表单数据
const form = ref({
  keyword: '人工智能',
  pages: 10
})

// 加载状态
const loading = ref(false)

// 日志
const logs = ref([])
const logContainer = ref(null)

// 统计数据
const stats = ref({
  total: 0,
  positive: 0,
  neutral: 0,
  negative: 0
})

// 历史记录
const records = ref([])

// 添加日志
const addLog = (message, type = 'info') => {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  logs.value.unshift({
    time,
    message,
    type
  })

  // 只保留最近100条
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(0, 100)
  }

  // 滚动到顶部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = 0
    }
  })
}

// 清空日志
const clearLog = () => {
  logs.value = []
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    running: '进行中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await api.getDataStats()
    if (res.success) {
      const data = res.stats
      stats.value = {
        total: data.total_weibos || 0,
        positive: data.sentiment_distribution?.positive || 0,
        neutral: data.sentiment_distribution?.neutral || 0,
        negative: data.sentiment_distribution?.negative || 0
      }
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

// 获取历史记录
const fetchRecords = async () => {
  try {
    const res = await api.getCrawlStatus()
    if (res.success) {
      records.value = res.records || []
    }
  } catch (error) {
    console.error('获取记录失败:', error)
  }
}

// 开始爬取
const handleCrawl = async () => {
  if (!form.value.keyword.trim()) {
    addLog('请输入搜索关键词', 'warning')
    return
  }

  loading.value = true
  addLog(`开始爬取关键词「${form.value.keyword}」，共${form.value.pages}页...`, 'info')

  try {
    const res = await api.startCrawl({
      keyword: form.value.keyword,
      pages: form.value.pages,
      use_demo: false
    })

    if (res.success) {
      addLog(`爬取完成！共获取 ${res.total} 条数据，保存 ${res.saved} 条`, 'success')
      fetchStats()
      fetchRecords()
    } else {
      addLog(`爬取失败：${res.message}`, 'error')
    }
  } catch (error) {
    // 真实爬取可能失败，尝试使用演示数据
    addLog('真实爬取失败，尝试使用演示数据...', 'warning')
    await handleDemo()
  } finally {
    loading.value = false
  }
}

// 生成演示数据
const handleDemo = async () => {
  if (!form.value.keyword.trim()) {
    addLog('请输入搜索关键词', 'warning')
    return
  }

  loading.value = true
  addLog(`开始生成演示数据，关键词「${form.value.keyword}」...`, 'info')

  try {
    const res = await api.generateDemo({
      keyword: form.value.keyword,
      count: form.value.pages * 10
    })

    if (res.success) {
      addLog(`演示数据生成完成！共 ${res.total} 条，已保存 ${res.saved} 条`, 'success')
      fetchStats()
      fetchRecords()
    } else {
      addLog(`生成失败：${res.message}`, 'error')
    }
  } catch (error) {
    addLog(`生成失败：${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

// 清空数据
const handleClear = async () => {
  if (!confirm('确定要清空所有数据吗？此操作不可恢复！')) {
    return
  }

  loading.value = true
  addLog('正在清空数据...', 'info')

  try {
    const res = await api.clearData()
    if (res.success) {
      addLog('数据已清空', 'success')
      stats.value = { total: 0, positive: 0, neutral: 0, negative: 0 }
      fetchRecords()
    } else {
      addLog(`清空失败：${res.message}`, 'error')
    }
  } catch (error) {
    addLog(`清空失败：${error.message}`, 'error')
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  fetchStats()
  fetchRecords()
  addLog('爬虫控制系统已就绪', 'info')
})
</script>

<style scoped>
.crawl-control {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.control-header {
  margin-bottom: 25px;
}

.control-header h2 {
  font-size: 24px;
  color: #4fc3f7;
  margin-bottom: 8px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* 表单区域 */
.crawl-form {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.form-card,
.stats-card,
.history-card {
  background: rgba(25, 35, 75, 0.8);
  border: 1px solid rgba(79, 195, 247, 0.2);
  border-radius: 12px;
  padding: 25px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #4fc3f7;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(79, 195, 247, 0.2);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.hint {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}

.btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4);
}

.btn-secondary {
  background: rgba(79, 195, 247, 0.2);
  color: #4fc3f7;
  border: 1px solid rgba(79, 195, 247, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(79, 195, 247, 0.3);
}

.btn-danger {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: rgba(244, 67, 54, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 日志区域 */
.log-section {
  margin-top: 25px;
  border-top: 1px solid rgba(79, 195, 247, 0.1);
  padding-top: 15px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.log-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.btn-text {
  background: none;
  border: none;
  color: #4fc3f7;
  cursor: pointer;
  font-size: 12px;
}

.btn-text:hover {
  text-decoration: underline;
}

.log-content {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 10px;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.log-message {
  color: rgba(255, 255, 255, 0.8);
}

.log-success .log-message {
  color: #4caf50;
}

.log-error .log-message {
  color: #f44336;
}

.log-warning .log-message {
  color: #ff9800;
}

.log-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  padding: 20px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: rgba(79, 195, 247, 0.05);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(79, 195, 247, 0.1);
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #4fc3f7;
  font-family: 'Courier New', monospace;
}

.stat-positive {
  color: #4caf50;
}

.stat-neutral {
  color: #ff9800;
}

.stat-negative {
  color: #f44336;
}

.stat-label {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 历史记录 */
.history-section {
  margin-top: 20px;
}

.history-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid rgba(79, 195, 247, 0.1);
}

th {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  font-size: 13px;
}

td {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

tr:hover td {
  background: rgba(79, 195, 247, 0.05);
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.status-running {
  background: rgba(33, 150, 243, 0.2);
  color: #2196f3;
}

.status-completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.status-failed {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.empty-row {
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  padding: 30px !important;
}

/* 响应式 */
@media (max-width: 1024px) {
  .crawl-form {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .form-actions {
    flex-wrap: wrap;
  }

  .btn {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
}
</style>
