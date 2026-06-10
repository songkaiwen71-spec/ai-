<template>
  <div class="sentiment-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      positive: 0,
      neutral: 0,
      negative: 0
    })
  }
})

const chartRef = ref(null)
let chartInstance = null

// 颜色配置
const colors = {
  positive: '#4caf50',
  neutral: '#ff9800',
  negative: '#f44336'
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 14, 39, 0.9)',
      borderColor: 'rgba(79, 195, 247, 0.3)',
      textStyle: {
        color: '#fff'
      },
      formatter: (params) => {
        return `<div style="padding: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${params.color};"></span>
            <span>${params.name}</span>
          </div>
          <div style="margin-top: 8px; font-size: 18px; font-weight: 600; color: ${params.color};">${params.value}%</div>
          <div style="margin-top: 4px; color: rgba(255,255,255,0.6);">数量: ${getCount(params.name)}</div>
        </div>`
      }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: {
        color: 'rgba(255, 255, 255, 0.8)',
        fontSize: 13
      },
      itemWidth: 12,
      itemHeight: 12,
      itemGap: 15
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 6,
        borderColor: 'rgba(10, 14, 39, 0.8)',
        borderWidth: 3
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}\n{d}%',
        color: 'rgba(255, 255, 255, 0.9)',
        fontSize: 12
      },
      labelLine: {
        show: true,
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(79, 195, 247, 0.5)'
        },
        label: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: [
        {
          value: props.data.positive || 0,
          name: '积极',
          itemStyle: { color: colors.positive }
        },
        {
          value: props.data.neutral || 0,
          name: '中性',
          itemStyle: { color: colors.neutral }
        },
        {
          value: props.data.negative || 0,
          name: '消极',
          itemStyle: { color: colors.negative }
        }
      ]
    }]
  }

  chartInstance.setOption(option)
}

// 获取数量
const getCount = (label) => {
  const map = {
    '积极': props.data.positive,
    '中性': props.data.neutral,
    '消极': props.data.negative
  }
  const total = props.data.positive + props.data.neutral + props.data.negative
  if (total === 0) return 0
  const percent = map[label] || 0
  return Math.round(percent * total / 100)
}

// 更新数据
const updateChart = () => {
  if (!chartInstance) {
    initChart()
    return
  }

  chartInstance.setOption({
    series: [{
      data: [
        {
          value: props.data.positive || 0,
          name: '积极',
          itemStyle: { color: colors.positive }
        },
        {
          value: props.data.neutral || 0,
          name: '中性',
          itemStyle: { color: colors.neutral }
        },
        {
          value: props.data.negative || 0,
          name: '消极',
          itemStyle: { color: colors.negative }
        }
      ]
    }]
  })
}

// 监听数据变化
watch(() => props.data, updateChart, { deep: true })

// 响应窗口变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.sentiment-container {
  width: 100%;
  height: 300px;
  min-height: 280px;
}
</style>
