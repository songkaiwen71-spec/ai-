<template>
  <div class="dashboard">
    <!-- 顶部数据卡片 -->
    <div class="stats-row">
      <DataStats
        title="数据总量"
        :value="stats.total || 0"
        icon="📊"
        color="#4fc3f7"
      />
      <DataStats
        title="今日新增"
        :value="stats.newToday || 0"
        icon="🆕"
        color="#4caf50"
      />
      <DataStats
        title="总点赞数"
        :value="formatNumber(stats.total_likes || 0)"
        icon="👍"
        color="#ff9800"
      />
      <DataStats
        title="总评论数"
        :value="formatNumber(stats.total_comments || 0)"
        icon="💬"
        color="#e91e63"
      />
      <DataStats
        title="总转发数"
        :value="formatNumber(stats.total_reposts || 0)"
        icon="🔄"
        color="#9c27b0"
      />
      <DataStats
        title="平均情感"
        :value="((stats.avg_sentiment || 0.5) * 100).toFixed(1) + '%'"
        icon="😊"
        :color="getSentimentColor(stats.avg_sentiment || 0.5)"
      />
    </div>

    <!-- 主要可视化区域 -->
    <div class="charts-grid">
      <!-- 词云 -->
      <div class="chart-card wordcloud-card">
        <div class="card-title">📚 关键词词云</div>
        <WordCloud :data="wordcloudData" />
      </div>

      <!-- 情感分布 -->
      <div class="chart-card sentiment-card">
        <div class="card-title">😊 情感分布</div>
        <SentimentPie :data="sentimentData" />
      </div>

      <!-- 舆情热度趋势 -->
      <div class="chart-card trend-card">
        <div class="card-title">📈 舆情热度趋势</div>
        <TrendLine :data="trendData" />
      </div>

      <!-- 热词统计 -->
      <div class="chart-card hotwords-card">
        <div class="card-title">🔥 热词统计 TOP20</div>
        <HotWordsBar :data="hotwordsData" />
      </div>

      <!-- 地理分布 -->
      <div class="chart-card geo-card">
        <div class="card-title">🗺️ 用户地域分布</div>
        <GeoMap :data="geoData" />
      </div>

      <!-- 最新微博 -->
      <div class="chart-card recent-card">
        <div class="card-title">📝 最新微博</div>
        <div class="recent-list">
          <div
            v-for="item in recentData"
            :key="item.weibo_id"
            class="recent-item"
          >
            <div class="recent-header">
              <span class="user-name">{{ item.username }}</span>
              <span :class="['sentiment-tag', `tag-${item.sentiment_label}`]">
                {{ getSentimentLabel(item.sentiment_label) }}
              </span>
            </div>
            <div class="recent-content">{{ item.content }}</div>
            <div class="recent-meta">
              <span>👍 {{ item.like_count }}</span>
              <span>💬 {{ item.comment_count }}</span>
              <span>🔄 {{ item.repost_count }}</span>
              <span class="publish-time">{{ item.publish_time }}</span>
            </div>
          </div>
          <div v-if="recentData.length === 0" class="empty-state">
            暂无数据，请先爬取数据
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import DataStats from '../components/DataStats.vue'
import WordCloud from '../components/WordCloud.vue'
import SentimentPie from '../components/SentimentPie.vue'
import TrendLine from '../components/TrendLine.vue'
import HotWordsBar from '../components/HotWordsBar.vue'
import GeoMap from '../components/GeoMap.vue'
import api from '../api'

// 数据状态
const stats = ref({})
const wordcloudData = ref([])
const sentimentData = ref([])
const trendData = ref([])
const hotwordsData = ref([])
const geoData = ref([])
const recentData = ref([])

// 加载状态
const loading = ref(true)

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num.toString()
}

// 获取情感颜色
const getSentimentColor = (score) => {
  if (score >= 0.6) return '#4caf50'
  if (score <= 0.4) return '#f44336'
  return '#ff9800'
}

// 获取情感标签
const getSentimentLabel = (label) => {
  const labels = {
    positive: '积极',
    neutral: '中性',
    negative: '消极'
  }
  return labels[label] || label
}

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const res = await api.getDashboard()
    if (res.success) {
      const data = res.data
      stats.value = data.summary || {}
      sentimentData.value = data.sentiment?.percentage || {}
      trendData.value = data.trend || []
      hotwordsData.value = data.hotwords || []
      geoData.value = data.geo || []
      recentData.value = data.recent || []
      wordcloudData.value = data.hotwords?.slice(0, 50).map(item => ({
        name: item.word,
        value: item.count
      })) || []
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 定时刷新
let refreshTimer = null

onMounted(() => {
  fetchData()
  // 每30秒刷新一次
  refreshTimer = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.dashboard {
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

/* 数据卡片行 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* 图表卡片 */
.chart-card {
  background: rgba(25, 35, 75, 0.8);
  border: 1px solid rgba(79, 195, 247, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.chart-card:hover {
  border-color: rgba(79, 195, 247, 0.5);
  box-shadow: 0 0 30px rgba(79, 195, 247, 0.1);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #4fc3f7;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 词云卡片 */
.wordcloud-card {
  grid-column: span 2;
  min-height: 350px;
}

/* 情感分布卡片 */
.sentiment-card {
  grid-column: span 1;
  min-height: 350px;
}

/* 趋势卡片 */
.trend-card {
  grid-column: span 3;
  min-height: 320px;
}

/* 热词卡片 */
.hotwords-card {
  grid-column: span 1;
  min-height: 350px;
}

/* 地理分布卡片 */
.geo-card {
  grid-column: span 2;
  min-height: 350px;
}

/* 最新微博卡片 */
.recent-card {
  grid-column: span 3;
  max-height: 400px;
  overflow: hidden;
}

.recent-list {
  max-height: 320px;
  overflow-y: auto;
  padding-right: 5px;
}

.recent-item {
  padding: 12px;
  background: rgba(79, 195, 247, 0.05);
  border-radius: 8px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.recent-item:hover {
  background: rgba(79, 195, 247, 0.1);
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.user-name {
  font-weight: 600;
  color: #4fc3f7;
  font-size: 14px;
}

.sentiment-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.tag-positive {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.tag-neutral {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.tag-negative {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.recent-content {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recent-meta {
  display: flex;
  gap: 15px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.publish-time {
  margin-left: auto;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

/* 响应式 */
@media (max-width: 1400px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }

  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .wordcloud-card,
  .geo-card {
    grid-column: span 2;
  }

  .trend-card,
  .recent-card {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .wordcloud-card,
  .sentiment-card,
  .trend-card,
  .hotwords-card,
  .geo-card,
  .recent-card {
    grid-column: span 1;
  }
}
</style>
