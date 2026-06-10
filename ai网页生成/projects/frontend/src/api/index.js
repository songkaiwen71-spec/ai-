/**
 * API调用封装
 * 大数据舆情可视化分析系统
 */

import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ============ 爬虫相关API ============

/**
 * 开始爬取数据
 * @param {Object} params - { keyword: string, pages: number, use_demo: boolean }
 */
export const startCrawl = (params) => {
  return api.post('/crawl/start', params)
}

/**
 * 生成演示数据
 * @param {Object} params - { keyword: string, count: number }
 */
export const generateDemo = (params) => {
  return api.post('/crawl/demo', params)
}

/**
 * 获取爬取状态
 */
export const getCrawlStatus = () => {
  return api.get('/crawl/status')
}

/**
 * 爬取热搜
 */
export const crawlHotSearch = (params) => {
  return api.post('/crawl/hot', params)
}

// ============ 数据相关API ============

/**
 * 获取数据列表
 * @param {Object} params - { limit: number, offset: number }
 */
export const getDataList = (params) => {
  return api.get('/data/list', { params })
}

/**
 * 获取数据统计
 */
export const getDataStats = () => {
  return api.get('/data/stats')
}

/**
 * 获取数据详情
 * @param {string} weiboId - 微博ID
 */
export const getDataDetail = (weiboId) => {
  return api.get(`/data/detail/${weiboId}`)
}

/**
 * 清空数据
 */
export const clearData = () => {
  return api.post('/data/clear')
}

/**
 * 获取最近数据
 * @param {Object} params - { days: number, limit: number }
 */
export const getRecentData = (params) => {
  return api.get('/data/recent', { params })
}

// ============ 分析相关API ============

/**
 * 获取情感统计
 */
export const getSentiment = () => {
  return api.get('/sentiment')
}

/**
 * 获取词云数据
 * @param {Object} params - { limit: number }
 */
export const getWordcloud = (params) => {
  return api.get('/wordcloud', { params })
}

/**
 * 获取趋势数据
 * @param {Object} params - { days: number }
 */
export const getTrend = (params) => {
  return api.get('/trend', { params })
}

/**
 * 获取热词统计
 * @param {Object} params - { limit: number }
 */
export const getHotwords = (params) => {
  return api.get('/hotwords', { params })
}

/**
 * 获取地理分布
 */
export const getGeo = () => {
  return api.get('/geo')
}

/**
 * 获取仪表盘综合数据
 */
export const getDashboard = () => {
  return api.get('/dashboard')
}

/**
 * 获取实时统计
 */
export const getRealtime = () => {
  return api.get('/realtime')
}

// ============ 健康检查 ============

/**
 * 健康检查
 */
export const healthCheck = () => {
  return api.get('/health')
}

export default {
  // 爬虫
  startCrawl,
  generateDemo,
  getCrawlStatus,
  crawlHotSearch,
  // 数据
  getDataList,
  getDataStats,
  getDataDetail,
  clearData,
  getRecentData,
  // 分析
  getSentiment,
  getWordcloud,
  getTrend,
  getHotwords,
  getGeo,
  getDashboard,
  getRealtime,
  // 健康
  healthCheck
}
