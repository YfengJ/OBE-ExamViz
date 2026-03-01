<template>
  <div ref="container" class="chart" />
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ labels: string[]; values: number[] }>()

const container = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!container.value) return
  if (!chart) {
    chart = echarts.init(container.value)
  }

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.labels },
    yAxis: { type: 'value', max: 1 },
    series: [{ type: 'line', data: props.values, smooth: true, itemStyle: { color: '#00a76f' } }],
  })
}

onMounted(async () => {
  await nextTick()
  renderChart()
  window.addEventListener('resize', renderChart)
})

watch(
  () => [props.labels, props.values],
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
  height: 300px;
}
</style>
