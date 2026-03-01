<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header" style="margin-bottom: 1.5rem;">
        <div class="header-titles">
          <h3>分析中心</h3>
          <p class="subtitle">多维度解读考试成绩、题目难度与知识点掌握情况</p>
        </div>
        <div class="action-bar gap">
          <el-select v-model="courseId" class="premium-select" style="width: 240px" @change="loadExamsByCourse" placeholder="选择课程...">
            <el-option v-for="course in courses" :key="course.id" :label="course.course_name" :value="course.id" />
          </el-select>
          <el-select v-model="examId" class="premium-select" style="width: 200px" placeholder="选择考试...">
            <el-option v-for="exam in filteredExams" :key="exam.id" :label="exam.name" :value="exam.id" />
          </el-select>
          <el-input 
            v-model="className" 
            placeholder="选择班级 (可选)" 
            class="premium-input"
            style="width: 160px" 
            clearable 
          />
          <el-button type="primary" class="primary-action-btn" @click="loadAll" :disabled="!courseId">确认分析</el-button>
          <el-button plain type="success" class="action-btn" @click="exportReport" :disabled="!examId">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right:6px">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            导出报告
          </el-button>
        </div>
      </div>

      <div class="kpi-grid" style="margin-top: 2rem;">
        <div class="kpi-wrapper">
          <article class="kpi">
            <p>参与人数</p>
            <h2>{{ stats.total_students }}</h2>
            <div class="kpi-trend neutral">人已评估</div>
          </article>
        </div>
        <div class="kpi-wrapper">
          <article class="kpi">
            <p>平均分</p>
            <h2>{{ stats.average_score.toFixed(1) }}</h2>
            <div class="kpi-trend" :class="stats.average_score >= 75 ? 'positive' : 'negative'">班级均分</div>
          </article>
        </div>
        <div class="kpi-wrapper">
          <article class="kpi">
            <p>最高分</p>
            <h2>{{ stats.max_score }}</h2>
            <div class="kpi-trend positive">本次最高</div>
          </article>
        </div>
        <div class="kpi-wrapper">
          <article class="kpi">
            <p>及格率</p>
            <h2 :class="{'text-danger': stats.pass_rate < 0.6}">{{ (stats.pass_rate * 100).toFixed(1) }}%</h2>
            <div class="kpi-trend" :class="stats.pass_rate >= 0.6 ? 'positive' : 'negative'">
              {{ stats.pass_rate >= 0.6 ? '状况良好' : '需重点关注' }}
            </div>
          </article>
        </div>
      </div>
    </article>

    <div class="grid-2-col">
      <article class="card panel">
        <div class="panel-header">
          <h3>分数段分布</h3>
        </div>
        <div class="chart-container">
          <ScoreDistributionChart :segments="stats.score_segments" />
        </div>
      </article>

      <article class="card panel">
        <div class="panel-header">
          <h3>历史趋势分析</h3>
          <p class="subtitle">班级最近各次考试的平均分走势</p>
        </div>
        <div class="chart-container">
          <LineMetricChart :labels="trendLabels" :values="trendValues" />
        </div>
      </article>
    </div>

    <article class="card panel">
      <div class="panel-header">
        <h3>题目难度与区分度分析</h3>
      </div>
      <div class="chart-container" style="height: 250px; margin-bottom: 2rem;">
        <LineMetricChart :labels="questionLabels" :values="questionDifficulty" />
      </div>
      <div class="table-container">
        <el-table :data="questionRows" class="premium-table borderless-table">
          <el-table-column prop="qno" label="题号" width="90">
             <template #default="{ row }"><span class="mono-id fw-bold">{{ row.qno }}</span></template>
          </el-table-column>
          <el-table-column prop="qtype" label="题型" width="130">
            <template #default="{ row }">
              <el-tag size="small" type="info" effect="plain">{{ row.qtype || '基本题' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="avg_score" label="平均得分" width="110" align="center">
            <template #default="{ row }"><span class="mono-id">{{ row.avg_score.toFixed(1) }}</span></template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度系数" width="110" align="center">
            <template #default="{ row }"><span class="mono-id">{{ row.difficulty.toFixed(2) }}</span></template>
          </el-table-column>
          <el-table-column prop="discrimination" label="区分度" width="120" align="center">
            <template #default="{ row }"><span class="mono-id">{{ row.discrimination.toFixed(2) }}</span></template>
          </el-table-column>
          <el-table-column prop="pass_rate" label="得分率">
            <template #default="{ row }">
               <div style="display: flex; align-items: center; gap: 8px;">
                 <el-progress 
                   :percentage="Number((row.pass_rate * 100).toFixed(1))" 
                   :status="row.pass_rate > 0.5 ? 'success' : 'exception'"
                   :stroke-width="8"
                   style="width: 120px;"
                 />
               </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>

    <article class="card panel mb-extended">
      <div class="panel-header">
        <h3>OBE 毕业要求达成度</h3>
        <p class="subtitle">实际达成情况与期望阈值直观比照</p>
      </div>
      <div class="table-container">
        <el-table :data="obeRows" class="premium-table">
          <el-table-column prop="co_code" label="目标节点" width="140">
             <template #default="{ row }">
               <span class="indigo-badge">{{ row.co_code }}</span>
             </template>
          </el-table-column>
          <el-table-column prop="co_name" label="目标详细描述" min-width="250">
             <template #default="{ row }">
               <span class="fw-bold">{{ row.co_name }}</span>
             </template>
          </el-table-column>
          <el-table-column prop="threshold" label="期望阈值" width="100" align="center">
             <template #default="{ row }"><span class="mono-id">{{ row.threshold.toFixed(2) }}</span></template>
          </el-table-column>
          <el-table-column prop="achievement" label="实际达成进度" width="280">
            <template #default="{ row }">
              <div class="attainment-bar" :class="{'passed': row.achievement >= row.threshold}">
                <div class="attainment-track">
                   <div class="attainment-fill" :style="{ width: `${Math.min(row.achievement * 100, 100)}%` }"></div>
                   <div class="threshold-marker" :style="{ left: `${row.threshold * 100}%` }" title="期望阈值"></div>
                </div>
                <span class="mono-id val">{{ (row.achievement * 100).toFixed(1) }}%</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import ScoreDistributionChart from '../components/charts/ScoreDistributionChart.vue'
import LineMetricChart from '../components/charts/LineMetricChart.vue'
import {
  analysisApi,
  courseApi,
  examApi,
  type Course,
  type Exam,
  type ObeAchievement,
  type QuestionAnalysisItem,
  type ScoreStats,
  type ScoreTrendPoint,
} from '../api/modules/analysis'

const courses = ref<Course[]>([])
const exams = ref<Exam[]>([])
const filteredExams = ref<Exam[]>([])
const courseId = ref<number>(1)
const examId = ref<number>(1)
const className = ref('')

const stats = ref<ScoreStats>({
  total_students: 0,
  average_score: 0,
  max_score: 0,
  min_score: 0,
  pass_rate: 0,
  score_segments: { '90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0, '0-59': 0 },
})
const questionRows = ref<QuestionAnalysisItem[]>([])
const obeRows = ref<ObeAchievement[]>([])
const trends = ref<ScoreTrendPoint[]>([])

const questionLabels = computed(() => questionRows.value.map((item) => item.qno))
const questionDifficulty = computed(() => questionRows.value.map((item) => Number(item.difficulty.toFixed(3))))
const trendLabels = computed(() => trends.value.map((item) => item.exam_name))
const trendValues = computed(() => trends.value.map((item) => Number((item.avg_score / 100).toFixed(3))))

async function loadBase() {
  courses.value = await courseApi.list()
  exams.value = await examApi.list()
  courseId.value = courses.value[0]?.id || 1
  loadExamsByCourse()
}

function loadExamsByCourse() {
  filteredExams.value = exams.value.filter((exam) => exam.course_id === courseId.value)
  if (!filteredExams.value.length) {
    examId.value = 0
    return
  }
  if (!filteredExams.value.some((item) => item.id === examId.value)) {
    examId.value = filteredExams.value[0].id
  }
}

async function loadAll() {
  if (!courseId.value) {
    ElMessage.warning('Course required for analysis')
    return
  }
  stats.value = await analysisApi.scoreStats(courseId.value, className.value || undefined)
  trends.value = await analysisApi.scoreTrend(courseId.value)
  if (examId.value) {
    questionRows.value = await analysisApi.questionAnalysis(examId.value)
  }
  obeRows.value = await analysisApi.obeAchievement(courseId.value, examId.value || undefined)
}

async function exportReport() {
  if (!courseId.value || !examId.value) {
    ElMessage.warning('Course and Exam required to yield report.')
    return
  }

  const blob = await analysisApi.exportScoreReport(courseId.value, examId.value, className.value || undefined)
  const href = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = href
  a.download = `成绩分析报告_${courseId.value}_${examId.value}.xlsx`
  a.click()
  URL.revokeObjectURL(href)
}

onMounted(async () => {
  await loadBase()
  await loadAll()
})
</script>

<style scoped>
.header-titles .subtitle {
  margin: 0.25rem 0 0 0;
  color: var(--ink-muted);
  font-size: 0.9rem;
}

.action-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.primary-action-btn {
  padding: 0 1.25rem;
}

.action-btn {
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
}

.premium-select {
  --el-border-radius-base: var(--radius-sm);
}

.grid-2-col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
}

.chart-container {
  min-height: 280px;
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
/* Ensure inner echarts fill the space */
.chart-container > * {
  width: 100% !important;
  height: 100% !important;
}

.kpi-wrapper {
  position: relative;
  transition: var(--trans-smooth);
}

.kpi-wrapper:hover {
  transform: translateY(-4px);
}

.kpi-wrapper::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px -15px rgba(37, 99, 235, 0.15);
  opacity: 0;
  transition: var(--trans-smooth);
  z-index: 0;
}

.kpi-wrapper:hover::after {
  opacity: 1;
}

.kpi-trend {
  margin-top: 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  display: inline-table;
}

.positive { background: #ecfdf5; color: var(--status-good); }
.negative { background: #fef2f2; color: var(--status-danger); }
.neutral { background: #f1f5f9; color: var(--ink-muted); }
.text-danger {
  background: linear-gradient(135deg, #ef4444, #f97316);
  -webkit-background-clip: text;
  background-clip: text;
}


.table-container {
  margin: 0 -0.5rem;
}

.borderless-table {
  --el-table-border: none;
  --el-table-bg-color: transparent;
}
.borderless-table::before { display: none; }

.mono-id {
  font-family: var(--font-display);
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  color: var(--ink-title);
  font-size: 0.95rem;
}

.fw-bold {
  font-weight: 600;
  color: var(--ink-title);
}

.indigo-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 700;
}

/* Custom Attainment Visualizer */
.attainment-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.attainment-track {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  position: relative;
  overflow: visible;
}

.attainment-fill {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  background: var(--status-warning);
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.attainment-bar.passed .attainment-fill {
  background: var(--status-good);
}

.threshold-marker {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 2px;
  background: var(--ink-title);
  transform: translateX(-50%);
  z-index: 10;
  border-radius: 1px;
}

.attainment-bar .val {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
}

.mb-extended {
  margin-bottom: 2rem;
}

@media (max-width: 960px) {
  .grid-2-col {
    grid-template-columns: 1fr;
  }
}
</style>
