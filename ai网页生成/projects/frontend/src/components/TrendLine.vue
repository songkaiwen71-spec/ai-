<template>
  <div class="trend-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  // 准备数据
  const dates = props.data.map(item => item.date || item.date?.split(' ')[0] || '')
  const counts = props.data.map(item => item.count || 0)
  const sentiments = props.data.map(item => (item.avg_sentiment || 0.5) * 100)
  const likes = props.data.map(item => item.total_likes || 0)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 14, 39, 0.9)',
      borderColor: 'rgba(79, 195, 247, 0.3)',
      textStyle: {
        color: '#fff'
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: 'rgba(79, 195, 247, 0.5)'
        }
      }
    },
    legend: {
      data: ['发布量', '情感指数', '点赞数'],
      textStyle: {
        color: 'rgba(255, 255, 255, 0.8)'
      },
      top: 0,
      itemWidth: 20,
      itemHeight: 8
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: {
        lineStyle: {
          color: 'rgba(79, 195, 247, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: 11
      },
      axisTick: {
        show: false
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '发布量',
        position: 'left',
        axisLine: {
          show: true,
          lineStyle: {
            color: '#4fc3f7'
          }
        },
        axisLabel: {
          color: 'rgba(255, 255, 255, 0.6)',
          fontSize: 11
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(79, 195, 247, 0.1)'
          }
        }
      },
      {
        type: 'value',
        name: '情感指数',
        position: 'right',
        min: 0,
        max: 100,
        axisLine: {
          show: true,
          lineStyle: {
            color: '#4caf50'
          }
        },
        axisLabel: {
          color: 'rgba(255, 255, 255, 0.6)',
          fontSize: 11,
          formatter: '{value}%'
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '发布量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#4fc3f7' },
            { offset: 1, color: 'rgba(79, 195, 247, 0.3)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '40%'
      },
      {
        name: '情感指数',
        type: 'line',
        yAxisIndex: 1,
        data: sentiments,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          color: '#4caf50',
          width: 3
        },
        itemStyle: {
          color: '#4caf50',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(76, 175, 80, 0.3)' },
            { offset: 1, color: 'rgba(76, 175, 80, 0)' }
          ])
        }
      },
      {
        name: '点赞数',
        type: 'line',
        yAxisIndex: 0,
        data: likes,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 6,
        lineStyle: {
          color: '#ff9800',
          width: 2,
          type: 'dashed'
        },
        itemStyle: {
          color: '#ff9800'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 更新数据
const updateChart = () => {
  if (!chartInstance) {
    initChart()
    return
  }

  const dates = props.data.map(item => item.date || item.date?.split(' ')[0] || '')
  const counts = props.data.map(item => item.count || 0)
  const sentiments = props.data.map(item => (item.avg_sentiment || 0.5) * 100)
  const likes = props.data.map(item => item.total_likes || 0)

  chartInstance.setOption({
    xAxis: {
      data: dates
    },
    series: [
      { data: counts },
      { data: sentiments },
      { data: likes }
    ]
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
.trend-container {
  width: 100%;
  height: 280px;
  min-height: 260px;
}
</style>
