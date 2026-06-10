<template>
  <div class="geo-container" ref="chartRef"></div>
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

// 省份坐标映射（简化的中国地图坐标）
const provinceCoordinates = {
  '北京': [116.46, 39.92],
  '天津': [117.2, 39.13],
  '河北': [114.48, 38.03],
  '山西': [112.53, 37.87],
  '内蒙古': [111.65, 40.82],
  '辽宁': [123.38, 41.8],
  '吉林': [125.35, 43.88],
  '黑龙江': [126.63, 45.75],
  '上海': [121.48, 31.22],
  '江苏': [118.78, 32.04],
  '浙江': [120.19, 30.26],
  '安徽': [117.27, 31.86],
  '福建': [119.3, 26.08],
  '江西': [115.89, 28.68],
  '山东': [118, 36.65],
  '河南': [113.65, 34.76],
  '湖北': [114.31, 30.52],
  '湖南': [113, 28.21],
  '重庆': [106.54, 29.59],
  '四川': [104.06, 30.67],
  '贵州': [106.71, 26.57],
  '云南': [102.73, 25.04],
  '西藏': [91.11, 29.97],
  '陕西': [108.95, 34.27],
  '甘肃': [103.73, 36.03],
  '青海': [101.74, 36.56],
  '宁夏': [106.27, 38.47],
  '新疆': [87.68, 43.77],
  '广东': [113.23, 23.16],
  '广西': [108.33, 22.84],
  '海南': [110.35, 20.02],
  '香港': [114.1, 22.2],
  '澳门': [113.33, 22.13],
  '台湾': [121.38, 25.08]
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  // 处理数据，创建散点图
  const scatterData = props.data.map((item, index) => {
    const coord = provinceCoordinates[item.name]
    if (coord) {
      return {
        name: item.name,
        value: [...coord, item.value]
      }
    }
    return null
  }).filter(item => item !== null)

  // 如果没有数据，生成示例数据
  if (scatterData.length === 0) {
    const sampleProvinces = ['北京', '上海', '广东', '浙江', '江苏', '四川', '湖北', '河南', '山东', '福建']
    sampleProvinces.forEach((name, index) => {
      const coord = provinceCoordinates[name]
      if (coord) {
        scatterData.push({
          name,
          value: [...coord, Math.floor(Math.random() * 500) + 100]
        })
      }
    })
  }

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
        return `<div style="padding: 10px;">
          <div style="font-weight: 600; color: #4fc3f7; margin-bottom: 5px;">${params.name}</div>
          <div>活跃度: <span style="color: #ff9800; font-weight: 600;">${params.value[2]}</span></div>
        </div>`
      }
    },
    visualMap: {
      min: 0,
      max: 500,
      left: 'left',
      top: 'bottom',
      text: ['高', '低'],
      textStyle: {
        color: 'rgba(255, 255, 255, 0.8)'
      },
      calculable: true,
      inRange: {
        color: ['rgba(79, 195, 247, 0.2)', 'rgba(79, 195, 247, 0.6)', '#4fc3f7']
      },
      itemWidth: 15,
      itemHeight: 100
    },
    geo: {
      map: 'china',
      roam: false,
      zoom: 1.2,
      center: [105, 36],
      label: {
        show: false
      },
      itemStyle: {
        areaColor: 'rgba(79, 195, 247, 0.1)',
        borderColor: 'rgba(79, 195, 247, 0.3)',
        borderWidth: 1
      },
      emphasis: {
        label: {
          show: true,
          color: '#fff'
        },
        itemStyle: {
          areaColor: 'rgba(79, 195, 247, 0.3)'
        }
      }
    },
    series: [
      {
        name: '用户分布',
        type: 'map',
        geoIndex: 0,
        data: props.data.map(item => ({
          name: item.name,
          value: item.value
        }))
      },
      {
        name: '活跃度',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: scatterData,
        symbolSize: (val) => {
          const size = Math.sqrt(val[2]) / 3
          return Math.max(8, Math.min(25, size))
        },
        showEffectOn: 'render',
        rippleEffect: {
          brushType: 'stroke',
          scale: 3
        },
        itemStyle: {
          color: '#ff9800',
          shadowBlur: 10,
          shadowColor: 'rgba(255, 152, 0, 0.5)'
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params) => params.name,
          fontSize: 10,
          color: 'rgba(255, 255, 255, 0.8)'
        },
        zlevel: 1
      }
    ]
  }

  // 注册中国地图
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    .then(response => response.json())
    .then(chinaJson => {
      echarts.registerMap('china', chinaJson)
      chartInstance.setOption(option)
    })
    .catch(() => {
      // 如果地图加载失败，使用备选方案
      option.geo.map = 'china'
      option.series[0].geoIndex = undefined
      option.series[0].type = 'bar'
      chartInstance.setOption(option)
    })
}

// 更新数据
const updateChart = () => {
  if (!chartInstance) {
    initChart()
    return
  }

  const scatterData = props.data.map((item) => {
    const coord = provinceCoordinates[item.name]
    if (coord) {
      return {
        name: item.name,
        value: [...coord, item.value]
      }
    }
    return null
  }).filter(item => item !== null)

  chartInstance.setOption({
    series: [
      {
        data: props.data.map(item => ({
          name: item.name,
          value: item.value
        }))
      },
      {
        data: scatterData
      }
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
.geo-container {
  width: 100%;
  height: 300px;
  min-height: 280px;
}
</style>
