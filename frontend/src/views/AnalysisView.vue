<template>
  <section class="page-grid">
    <WorkflowGuide :active-step="3" />

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>结构分析</h3>
          <p class="subtitle">查看成绩分布、题型表现和课程目标达成情况，确认后即可生成报告。</p>
        </div>
        <div class="action-bar">
          <el-select v-model="selectedRunId" style="width: 360px" @change="onRunChange">
            <el-option v-for="item in runs" :key="item.run.id" :label="`${item.course_name} / ${item.run.class_name} / ${item.exam_name}`" :value="item.run.id" />
          </el-select>
          <el-button type="success" @click="openReportPreview" :disabled="!selectedRunId || hasBlockingDataIssues">查看报告预览</el-button>
          <el-button plain @click="loadDashboard" :disabled="!selectedRunId">刷新分析</el-button>
        </div>
      </div>

      <div v-if="dashboard" class="kpi-grid">
        <article class="kpi">
          <p>平均分</p>
          <h2>{{ dashboard.score_stats.average_score }}</h2>
          <div class="kpi-trend neutral">卷面统计</div>
        </article>
        <article class="kpi">
          <p>及格率</p>
          <h2>{{ (dashboard.score_stats.pass_rate * 100).toFixed(1) }}%</h2>
          <div class="kpi-trend positive">教学结果</div>
        </article>
        <article class="kpi">
          <p>试题难度</p>
          <h2>{{ dashboard.difficulty_label }}</h2>
          <div class="kpi-trend neutral">卷面判断</div>
        </article>
        <article class="kpi">
          <p>重点预警</p>
          <h2>{{ dashboard.warnings.length }}</h2>
          <div class="kpi-trend" :class="dashboard.warnings.length ? 'negative' : 'positive'">
            {{ dashboard.warnings.length ? '需教学干预' : '状态稳定' }}
          </div>
        </article>
      </div>

      <el-alert
        v-if="dashboard?.readiness?.blocking_errors?.length || dashboard?.data_quality?.issues?.length"
        class="data-quality-alert"
        type="warning"
        show-icon
        :closable="false"
        title="数据需要补充后才能生成可信报告"
      >
        <template #default>
          <p v-for="error in dashboard.readiness.blocking_errors" :key="error">{{ error }}</p>
          <p v-for="issue in dashboard.data_quality.issues" :key="issue">{{ issue }}</p>
        </template>
      </el-alert>

      <div v-if="dashboard?.readiness" class="readiness-list">
        <article v-for="item in dashboard.readiness.items" :key="item.key" :class="['readiness-item', item.status]">
          <span>{{ item.status === 'ready' ? '已完成' : '待补充' }}</span>
          <strong>{{ item.label }}</strong>
          <p>{{ item.detail }}</p>
        </article>
      </div>
    </article>

    <article class="card panel next-step-panel" v-if="dashboard">
      <div class="panel-header compact">
        <h3>下一步</h3>
      </div>
      <div class="summary-grid">
        <article class="summary-card">
          <h4>{{ dashboard.readiness.can_generate_report ? '生成报告正文' : '补齐报告数据' }}</h4>
          <p>{{ dashboard.readiness.can_generate_report ? '进入报告预览页，基于本次计算结果生成正文并导出文档。' : '当前任务还缺少关键数据，请先按提示补齐后再生成正式报告。' }}</p>
          <el-button type="primary" plain @click="openReadinessNextAction">{{ dashboard.readiness.next_action.label }}</el-button>
        </article>
        <article class="summary-card">
          <h4>生成改进建议</h4>
          <p>需要教学改进内容时，可在 AI 建议页单独生成并保存。</p>
          <el-button plain @click="openWarnings">去生成建议</el-button>
        </article>
      </div>
    </article>

    <div class="grid-2-col" v-if="dashboard">
      <article class="card panel">
        <div class="panel-header compact">
          <h3>成绩分布</h3>
        </div>
        <ScoreDistributionChart :segments="segmentMap" />
      </article>

      <article class="card panel">
        <div class="panel-header compact">
          <h3>课程目标达成对比</h3>
        </div>
        <LineMetricChart :labels="outcomeLabels" :values="outcomeValues" />
      </article>
    </div>

    <div class="grid-2-col" v-if="dashboard">
      <article class="card panel">
        <div class="panel-header compact">
          <h3>题型平均得分率</h3>
        </div>
        <LineMetricChart :labels="questionGroupLabels" :values="questionGroupValues" />
      </article>

      <article class="card panel">
        <div class="panel-header compact">
          <h3>课程总评构成</h3>
        </div>
        <el-table :data="dashboard.component_summary" class="premium-table" height="280">
          <el-table-column prop="component" label="项目" />
          <el-table-column prop="weight" label="权重" width="120">
            <template #default="{ row }">{{ (row.weight * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column prop="average_score" label="平均分" width="120" />
        </el-table>
      </article>
    </div>

    <article class="card panel" v-if="dashboard">
      <div class="panel-header compact">
        <h3>课程目标平均分和达成度</h3>
      </div>
      <el-table :data="dashboard.course_outcomes" class="premium-table">
        <el-table-column prop="co_code" label="课程目标" width="120" />
        <el-table-column prop="full_score" label="总分" width="100" />
        <el-table-column prop="avg_score" label="平均分" width="110" />
        <el-table-column prop="achievement" label="分项达成度" width="140">
          <template #default="{ row }">{{ (row.achievement * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="120">
          <template #default="{ row }">{{ (row.threshold * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" width="120">
          <template #default="{ row }">{{ (row.weight * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="result" label="达成结果">
          <template #default="{ row }">{{ (row.result * 100).toFixed(1) }}%</template>
        </el-table-column>
      </el-table>
    </article>

    <article class="card panel" v-if="dashboard">
      <div class="panel-header compact">
        <h3>逐题分析</h3>
      </div>
      <el-table :data="dashboard.question_items" class="premium-table">
        <el-table-column prop="qno" label="题号" width="90" />
        <el-table-column prop="qgroup_name" label="题组 / 题型" width="160" />
        <el-table-column prop="full_score" label="满分" width="90" />
        <el-table-column prop="avg_score" label="平均分" width="100" />
        <el-table-column prop="difficulty" label="得分率" width="110">
          <template #default="{ row }">{{ (row.difficulty * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="discrimination" label="区分度" width="100" />
        <el-table-column prop="pass_rate" label="及格率">
          <template #default="{ row }">{{ (row.pass_rate * 100).toFixed(1) }}%</template>
        </el-table-column>
      </el-table>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import ScoreDistributionChart from '../components/charts/ScoreDistributionChart.vue'
import LineMetricChart from '../components/charts/LineMetricChart.vue'
import WorkflowGuide from '../components/WorkflowGuide.vue'
import { analysisRunApi, type AnalysisRunOverview, type DashboardPayload } from '../api/modules/analysis'
import { useAppStore } from '../stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const runs = ref<AnalysisRunOverview[]>([])
const selectedRunId = ref(0)
const dashboard = ref<DashboardPayload | null>(null)

const segmentMap = computed(() =>
  (dashboard.value?.score_segments || []).reduce<Record<string, number>>((acc, item) => {
    acc[item.label === '<60' ? '0-59' : item.label] = item.count
    return acc
  }, {})
)
const outcomeLabels = computed(() => dashboard.value?.course_outcomes.map((item) => item.co_code) || [])
const outcomeValues = computed(() => dashboard.value?.course_outcomes.map((item) => Number(item.achievement.toFixed(4))) || [])
const questionGroupLabels = computed(() => dashboard.value?.question_groups.map((item) => item.qgroup_name) || [])
const questionGroupValues = computed(() => dashboard.value?.question_groups.map((item) => Number(item.achievement.toFixed(4))) || [])
const hasBlockingDataIssues = computed(() => dashboard.value?.readiness?.can_generate_report === false)

async function loadRuns() {
  try {
    runs.value = await analysisRunApi.list()
  } catch (error) {
    ElMessage.error((error as Error).message || '加载分析任务失败')
    return
  }
  const fromRoute = Number(route.query.run || appStore.selectedRunId || 0)
  selectedRunId.value = runs.value.some((item) => item.run.id === fromRoute) ? fromRoute : runs.value[0]?.run.id || 0
  if (selectedRunId.value) {
    appStore.selectedRunId = selectedRunId.value
    await loadDashboard()
  }
}

async function loadDashboard() {
  if (!selectedRunId.value) return
  try {
    dashboard.value = await analysisRunApi.dashboard(selectedRunId.value)
  } catch (error) {
    ElMessage.error((error as Error).message || '加载分析看板失败')
  }
}

function onRunChange() {
  appStore.selectedRunId = selectedRunId.value
  router.replace({ path: '/analysis', query: { run: String(selectedRunId.value) } })
  loadDashboard()
}

function openReportPreview() {
  if (!selectedRunId.value) return
  if (hasBlockingDataIssues.value) {
    ElMessage.warning(dashboard.value?.readiness?.blocking_errors?.[0] || '请先补齐关键数据后再生成报告。')
    return
  }
  appStore.selectedRunId = selectedRunId.value
  router.push({ path: '/report-preview', query: { run: String(selectedRunId.value) } })
}

function openReadinessNextAction() {
  if (!selectedRunId.value || !dashboard.value?.readiness) return
  appStore.selectedRunId = selectedRunId.value
  router.push({ path: dashboard.value.readiness.next_action.path, query: { run: String(selectedRunId.value) } })
}

function openWarnings() {
  if (!selectedRunId.value) return
  appStore.selectedRunId = selectedRunId.value
  router.push({ path: '/warnings', query: { run: String(selectedRunId.value) } })
}

onMounted(loadRuns)
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.panel-header.compact {
  margin-bottom: 1rem;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--ink-muted);
}

.action-bar {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.data-quality-alert {
  margin-top: 1rem;
}

.data-quality-alert p {
  margin: 0.25rem 0;
  line-height: 1.7;
}

.readiness-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.readiness-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 0.85rem;
  background: rgba(255, 255, 255, 0.78);
}

.readiness-item span {
  display: inline-flex;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
}

.readiness-item.ready span {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.readiness-item.pending span {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.readiness-item strong {
  display: block;
  margin-top: 0.55rem;
  color: var(--ink-title);
}

.readiness-item p {
  margin: 0.45rem 0 0;
  color: var(--ink-muted);
  line-height: 1.6;
}

.grid-2-col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.summary-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.76);
  padding: 1rem;
}

.summary-card h4 {
  margin: 0;
  color: var(--ink-title);
}

.summary-card p {
  margin: 0.7rem 0 0;
  color: var(--ink-body);
  line-height: 1.75;
}

.summary-card .el-button {
  margin-top: 1rem;
}

@media (max-width: 720px) {
  .action-bar {
    width: 100%;
  }
}
</style>
