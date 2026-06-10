<template>
  <div class="data-stats" :style="{ '--accent-color': color }">
    <div class="stats-icon">{{ icon }}</div>
    <div class="stats-content">
      <div class="stats-value" ref="valueRef">{{ displayValue }}</div>
      <div class="stats-title">{{ title }}</div>
    </div>
    <div class="stats-decoration"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  value: {
    type: [Number, String],
    default: 0
  },
  icon: {
    type: String,
    default: '📊'
  },
  color: {
    type: String,
    default: '#4fc3f7'
  }
})

// 显示值
const displayValue = ref(0)

// 数值动画
const animateValue = (start, end, duration) => {
  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    // 使用easeOutExpo缓动
    const easeProgress = 1 - Math.pow(1 - progress, 4)
    displayValue.value = Math.floor(start + (end - start) * easeProgress)

    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }

  requestAnimationFrame(step)
}

// 处理数值
const targetValue = computed(() => {
  if (typeof props.value === 'string') {
    return parseFloat(props.value.replace(/[^0-9.-]/g, '')) || 0
  }
  return props.value || 0
})

onMounted(() => {
  animateValue(0, targetValue.value, 1500)
})

watch(() => props.value, (newVal) => {
  const oldVal = displayValue.value
  const newTarget = typeof newVal === 'string'
    ? parseFloat(newVal.replace(/[^0-9.-]/g, '')) || 0
    : newVal
  animateValue(oldVal, newTarget, 800)
})
</script>

<style scoped>
.data-stats {
  background: rgba(25, 35, 75, 0.8);
  border: 1px solid rgba(79, 195, 247, 0.2);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.data-stats:hover {
  border-color: var(--accent-color);
  box-shadow: 0 0 20px rgba(79, 195, 247, 0.1);
  transform: translateY(-2px);
}

.stats-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(79, 195, 247, 0.1);
  border-radius: 12px;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-color);
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px var(--accent-color);
}

.stats-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.stats-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: radial-gradient(
    circle at center,
    rgba(79, 195, 247, 0.1) 0%,
    transparent 70%
  );
  pointer-events: none;
}

@media (max-width: 768px) {
  .data-stats {
    padding: 15px;
  }

  .stats-icon {
    width: 45px;
    height: 45px;
    font-size: 24px;
  }

  .stats-value {
    font-size: 22px;
  }

  .stats-title {
    font-size: 12px;
  }
}
</style>
