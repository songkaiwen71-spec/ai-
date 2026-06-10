<template>
  <div class="hotwords-container" ref="chartRef"></div>
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

  // 取前15个热词
  const topData = props.data.slice(0, 15)
  const words = topData.map(item => item.word)
  const counts = topData.map(item => item.count)

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
        type: 'shadow'
      },
      formatter: (params) => {
        const item = params[0]
        return `<div style="padding: 8px;">
          <div style="font-weight: 600; color: #4fc3f7;">${item.name}</div>
          <div style="margin-top: 5px;">出现次数: <span style="color: #4fc3f7; font-size: 16px;">${item.value}</span></div>
        </div>`
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '3%',
      top: '10px',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.4)',
        fontSize: 10
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(79, 195, 247, 0.1)'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: words.reverse(),
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 11
      }
    },
    series: [{
      type: 'bar',
      data: counts.reverse(),
      barWidth: '60%',
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params) => {
          const colorList = [
            '#4fc3f7', '#29b6f6', '#03a9f4', '#00bcd4', '#009688',
            '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107',
            '#ff9800', '#ff5722', '#e91e63', '#9c27b0', '#673ab7'
          ]
          return new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: colorList[params.dataIndex % colorList.length] },
            { offset: 1, color: colorList[params.dataIndex % colorList.length] + '60' }
          ])
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(79, 195, 247, 0.5)'
        }
      },
      label: {
        show: true,
        position: 'right',
        color: 'rgba(255, 255, 255, 0.6)',
        fontSize: 10,
        formatter: '{c}'
      }
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

  const topData = props.data.slice(0, 15)
  const words = topData.map(item => item.word)
  const counts = topData.map(item => item.count)

  chartInstance.setOption({
    yAxis: {
      data: words.reverse()
    },
    series: [{
      data: counts.reverse()
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
.hotwords-container {
  width: 100%;
  height: 300px;
  min-height: 280px;
}
</style>
