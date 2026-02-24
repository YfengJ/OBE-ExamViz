<template>
  <div class="analysis-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成绩分析</span>
          <el-button type="primary" @click="handleCalculate">重新计算</el-button>
        </div>
      </template>

      <div class="analysis-controls">
        <el-form :inline="true" :model="analysisForm">
          <el-form-item label="课程">
            <el-select v-model="analysisForm.course_id" placeholder="选择课程" style="width: 200px">
              <el-option
                v-for="course in courses"
                :key="course.id"
                :label="course.course_name"
                :value="course.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="班级">
            <el-select v-model="analysisForm.class_name" placeholder="选择班级" style="width: 150px">
              <el-option label="全部" value="" />
              <el-option label="计算机2101" value="计算机2101" />
              <el-option label="计算机2102" value="计算机2102" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="handleSearch">查询</el-button>
            <el-button type="warning" @click="handleExportReport">导出报告</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 统计概览 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="6">
          <el-statistic title="学生总数" :value="stats.total_students" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均成绩" :value="stats.average_score.toFixed(2)" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="最高分" :value="stats.max_score" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="最低分" :value="stats.min_score" />
        </el-col>
      </el-row>

      <!-- 成绩分布图表 -->
      <el-card style="margin-top: 20px" shadow="hover">
        <template #header>
          <span>成绩分布</span>
        </template>
        <div ref="scoreDistributionChart" style="height: 400px"></div>
      </el-card>

      <!-- 题目分析 -->
      <el-card style="margin-top: 20px" shadow="hover">
        <template #header>
          <span>题目分析</span>
        </template>
        <el-table :data="questionAnalysis" style="width: 100%" border>
          <el-table-column prop="qno" label="题号" width="80" />
          <el-table-column prop="qtype" label="题型" width="100" />
          <el-table-column prop="avg_score" label="平均分" width="100" />
          <el-table-column prop="difficulty" label="难度系数" width="120">
            <template #default="scope">
              <el-tag :type="getDifficultyTag(scope.row.difficulty)">
                {{ scope.row.difficulty.toFixed(3) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="discrimination" label="区分度" width="120">
            <template #default="scope">
              <el-tag :type="getDiscriminationTag(scope.row.discrimination)">
                {{ scope.row.discrimination.toFixed(3) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pass_rate" label="得分率" width="100">
            <template #default="scope">
              {{ (scope.row.pass_rate * 100).toFixed(1) }}%
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- OBE达成度 -->
      <el-card style="margin-top: 20px" shadow="hover">
        <template #header>
          <span>OBE达成度分析</span>
        </template>
        <el-table :data="obeOutcomes" style="width: 100%" border>
          <el-table-column prop="co_code" label="CO代码" width="100" />
          <el-table-column prop="co_name" label="课程目标" width="200" />
          <el-table-column prop="achievement" label="达成度" width="150">
            <template #default="scope">
              <el-progress :percentage="scope.row.achievement * 100" :status="getAchievementStatus(scope.row.achievement)">
                {{ (scope.row.achievement * 100).toFixed(1) }}%
              </el-progress>
            </template>
          </el-table-column>
          <el-table-column prop="threshold" label="阈值" width="100">
            <template #default="scope">
              {{ (scope.row.threshold * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.achievement >= scope.row.threshold ? 'success' : 'danger'">
                {{ scope.row.achievement >= scope.row.threshold ? '达成' : '未达成' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface Course {
  id: number
  course_name: string
}

interface Stats {
  total_students: number
  average_score: number
  max_score: number
  min_score: number
}

interface QuestionAnalysis {
  qno: string
  qtype: string
  avg_score: number
  difficulty: number
  discrimination: number
  pass_rate: number
}

interface OBEOutcome {
  co_code: string
  co_name: string
  achievement: number
  threshold: number
}

const courses = ref<Course[]>([])
const analysisForm = ref({
  course_id: 0,
  class_name: ''
})
const stats = ref<Stats>({
  total_students: 56,
  average_score: 78.5,
  max_score: 98,
  min_score: 42
})
const questionAnalysis = ref<QuestionAnalysis[]>([])
const obeOutcomes = ref<OBEOutcome[]>([])
const scoreDistributionChart = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const fetchCourses = async () => {
  try {
    const response = await axios.get('/api/analysis/courses')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const getDifficultyTag = (difficulty: number) => {
  if (difficulty < 0.3) return 'success' // 容易
  if (difficulty > 0.7) return 'danger' // 困难
  return 'warning' // 中等
}

const getDiscriminationTag = (discrimination: number) => {
  if (discrimination >= 0.4) return 'success' // 优秀
  if (discrimination >= 0.3) return 'warning' // 良好
  return 'danger' // 较差
}

const getAchievementStatus = (achievement: number) => {
  if (achievement >= 0.8) return 'success'
  if (achievement >= 0.6) return 'warning'
  return 'exception'
}

const handleSearch = () => {
  ElMessage.info('查询功能待实现')
  // 模拟数据
  questionAnalysis.value = [
    { qno: '1', qtype: '单选题', avg_score: 8.5, difficulty: 0.15, discrimination: 0.45, pass_rate: 0.85 },
    { qno: '2', qtype: '多选题', avg_score: 7.2, difficulty: 0.28, discrimination: 0.38, pass_rate: 0.72 },
    { qno: '3', qtype: '填空题', avg_score: 6.8, difficulty: 0.32, discrimination: 0.42, pass_rate: 0.68 },
    { qno: '4', qtype: '简答题', avg_score: 12.5, difficulty: 0.41, discrimination: 0.35, pass_rate: 0.625 },
    { qno: '5', qtype: '论述题', avg_score: 18.2, difficulty: 0.36, discrimination: 0.48, pass_rate: 0.73 }
  ]

  obeOutcomes.value = [
    { co_code: 'CO1', co_name: '掌握基本概念', achievement: 0.82, threshold: 0.6 },
    { co_code: 'CO2', co_name: '理解核心原理', achievement: 0.75, threshold: 0.6 },
    { co_code: 'CO3', co_name: '应用知识解决问题', achievement: 0.68, threshold: 0.6 },
    { co_code: 'CO4', co_name: '分析和评价能力', achievement: 0.58, threshold: 0.6 }
  ]
}

const handleCalculate = () => {
  ElMessage.info('计算功能待实现')
}

const handleExportReport = () => {
  ElMessage.info('导出报告功能待实现')
}

// 初始化成绩分布图表
const initScoreDistributionChart = () => {
  if (!scoreDistributionChart.value) return

  chartInstance = echarts.init(scoreDistributionChart.value)
  const option: echarts.EChartsOption = {
    title: {
      text: '期末成绩分布直方图'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['优秀(90-100)', '良好(80-89)', '中等(70-79)', '及格(60-69)', '不及格(<60)'],
      axisLabel: {
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '学生人数'
    },
    series: [{
      name: '人数',
      type: 'bar',
      data: [12, 18, 15, 8, 3],
      itemStyle: {
        color: '#409eff'
      }
    }]
  }

  chartInstance.setOption(option)

  // 响应式处理
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

onMounted(() => {
  fetchCourses()
  handleSearch()
  initScoreDistributionChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<style scoped>
.analysis-view {
  padding: 20px;
}

.analysis-controls {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>