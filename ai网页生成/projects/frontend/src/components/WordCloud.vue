<template>
  <div class="wordcloud-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

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

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      backgroundColor: 'rgba(10, 14, 39, 0.9)',
      borderColor: 'rgba(79, 195, 247, 0.3)',
      textStyle: {
        color: '#fff'
      },
      formatter: (params) => {
        return `<div style="padding: 5px;">
          <div style="font-weight: 600; color: #4fc3f7;">${params.name}</div>
          <div style="margin-top: 5px;">出现次数: <span style="color: #4fc3f7;">${params.value}</span></div>
        </div>`
      }
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      sizeRange: [14, 60],
      rotationRange: [-45, 45],
      rotationStep: 15,
      gridSize: 8,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: 'Microsoft YaHei, sans-serif',
        fontWeight: 'bold',
        color: () => {
          const colors = [
            '#4fc3f7', '#29b6f6', '#03a9f4', '#00bcd4',
            '#4caf50', '#8bc34a', '#cddc39',
            '#ff9800', '#ff5722', '#e91e63'
          ]
          return colors[Math.floor(Math.random() * colors.length)]
        },
        emphasis: {
          shadowBlur: 10,
          shadowColor: '#4fc3f7'
        }
      },
      data: props.data.map(item => ({
        name: item.name,
        value: item.value
      }))
    }]
  }

  chartInstance.setOption(option)
}

// 更新数据
const updateChart = () => {
  if (!chartInstance) {
    initChart()
    return
  }

  chartInstance.setOption({
    series: [{
      data: props.data.map(item => ({
        name: item.name,
        value: item.value
      }))
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
.wordcloud-container {
  width: 100%;
  height: 300px;
  min-height: 280px;
}
</style>
