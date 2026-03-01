<template>
  <div ref="container" class="chart" />
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ segments: Record<string, number> }>()

const container = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!container.value) return
  if (!chart) {
    chart = echarts.init(container.value)
  }

  const labels = ['90-100', '80-89', '70-79', '60-69', '0-59']
  const data = labels.map((label) => props.segments[label] ?? 0)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value', name: '人数' },
    series: [{ type: 'bar', data, itemStyle: { color: '#1b6ef3' }, barWidth: '45%' }],
  })
}

onMounted(async () => {
  await nextTick()
  renderChart()
  window.addEventListener('resize', renderChart)
})

watch(
  () => props.segments,
  () => {
    renderChart()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderChart)
  chart?.dispose()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 340px;
}
</style>
