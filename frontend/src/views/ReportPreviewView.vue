<template>
  <section class="page-grid">
    <WorkflowGuide :active-step="4" />

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>报告预览</h3>
          <p class="subtitle">在导出前核对正文、表格和建议内容。</p>
        </div>
        <div class="action-bar">
          <el-select v-model="selectedRunId" style="width: 360px" @change="onRunChange">
            <el-option v-for="item in runs" :key="item.run.id" :label="`${item.course_name} / ${item.run.class_name} / ${item.exam_name}`" :value="item.run.id" />
          </el-select>
          <el-button type="primary" :loading="generating" @click="generateNarrative" :disabled="!selectedRunId">生成报告文字</el-button>
          <el-button type="success" :loading="exporting" @click="exportDocx" :disabled="!selectedRunId || !reportNarrative">导出报告</el-button>
        </div>
      </div>

      <el-alert
        v-if="dashboard"
        :title="reportNarrative ? '报告正文已生成，可以继续核对并导出。' : '报告正文待生成。'"
        :type="reportNarrative ? 'success' : 'info'"
        :closable="false"
      />
    </article>

    <article class="card lineage-panel" v-if="dataLineage">
      <div class="panel-header compact">
        <div>
          <h3>数据依据</h3>
          <p class="subtitle">基础信息、统计结果、图表和文字来源分别标注，便于核对。</p>
        </div>
      </div>

      <div class="lineage-grid">
        <article v-for="item in dataLineage.data_sources" :key="item.title" class="lineage-card">
          <span :class="['source-pill', sourceTone(item.source_method)]">{{ item.source_label }}</span>
          <h4>{{ item.title }}</h4>
          <p>{{ item.source }}</p>
          <small v-if="item.evidence">{{ item.evidence }}</small>
        </article>
      </div>

      <div class="section-lineage">
        <h4>报告各部分来源</h4>
        <div class="section-source-list">
          <div v-for="item in dataLineage.report_sections" :key="item.section_key" class="section-source-item">
            <strong>{{ item.title }}</strong>
            <span :class="['source-pill', sourceTone(item.source_method)]">{{ item.source_label }}</span>
            <p>{{ item.description }}</p>
          </div>
        </div>
      </div>

      <div class="transfer-checklist">
        <h4>换课前检查</h4>
        <ul>
          <li v-for="item in dataLineage.transfer_checklist" :key="item">{{ item }}</li>
        </ul>
      </div>
    </article>

    <article class="card report-preview" v-if="dashboard">
      <div class="report-header">
        <div>
          <p class="report-kicker">报告预览</p>
          <h2>{{ dashboard.meta.course_name }}</h2>
          <p class="report-meta">
            {{ dashboard.meta.class_name }} · {{ dashboard.meta.academic_year }} · {{ dashboard.meta.term_label }} · {{ dashboard.meta.teacher_name || '未填写教师' }}
          </p>
        </div>
        <div class="report-status">
          <span>平均分 {{ dashboard.score_stats.average_score }}</span>
          <span>及格率 {{ (dashboard.score_stats.pass_rate * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <div v-if="!reportNarrative" class="report-empty">
        <h4>报告正文待生成</h4>
        <p>点击上方按钮后，将根据已完成的计算结果生成正文。</p>
      </div>

      <template v-else>
        <section class="report-section">
          <h3>一、基本情况</h3>
          <div class="meta-grid">
            <article class="meta-card">
              <span>课程名称</span>
              <strong>{{ dashboard.meta.course_name }}</strong>
            </article>
            <article class="meta-card">
              <span>教学班级</span>
              <strong>{{ dashboard.meta.class_name }}</strong>
            </article>
            <article class="meta-card">
              <span>考试名称</span>
              <strong>{{ dashboard.meta.exam_name }}</strong>
            </article>
            <article class="meta-card">
              <span>学生人数</span>
              <strong>{{ dashboard.score_stats.total_students }}</strong>
            </article>
          </div>
        </section>

        <section class="report-section">
          <h3>二、成绩统计</h3>
          <p class="report-paragraph">{{ reportNarrative.score_summary }}</p>
          <div class="stats-grid">
            <article class="stats-card">
              <span>平均分</span>
              <strong>{{ dashboard.score_stats.average_score }}</strong>
            </article>
            <article class="stats-card">
              <span>最高分</span>
              <strong>{{ dashboard.score_stats.max_score }}</strong>
            </article>
            <article class="stats-card">
              <span>最低分</span>
              <strong>{{ dashboard.score_stats.min_score }}</strong>
            </article>
            <article class="stats-card">
              <span>及格率</span>
              <strong>{{ (dashboard.score_stats.pass_rate * 100).toFixed(1) }}%</strong>
            </article>
          </div>
        </section>

        <section class="report-section">
          <h3>三、课程目标分析</h3>
          <p class="report-paragraph">{{ reportNarrative.support_analysis }}</p>
          <p class="report-paragraph">{{ reportNarrative.attainment_analysis }}</p>
          <el-table :data="dashboard.course_outcomes" class="premium-table">
            <el-table-column prop="co_code" label="课程目标" width="120" />
            <el-table-column prop="avg_score" label="平均分" width="110" />
            <el-table-column prop="achievement" label="达成度" width="120">
              <template #default="{ row }">{{ (row.achievement * 100).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="threshold" label="阈值" width="120">
              <template #default="{ row }">{{ (row.threshold * 100).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="result" label="结果">
              <template #default="{ row }">{{ (row.result * 100).toFixed(1) }}%</template>
            </el-table-column>
          </el-table>
        </section>

        <section class="report-section">
          <h3>四、逐题与题型情况</h3>
          <el-table :data="dashboard.question_items" class="premium-table">
            <el-table-column prop="qno" label="题号" width="90" />
            <el-table-column prop="qgroup_name" label="题组 / 题型" width="160" />
            <el-table-column prop="avg_score" label="平均分" width="100" />
            <el-table-column prop="difficulty" label="得分率" width="100">
              <template #default="{ row }">{{ (row.difficulty * 100).toFixed(1) }}%</template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="及格率">
              <template #default="{ row }">{{ (row.pass_rate * 100).toFixed(1) }}%</template>
            </el-table-column>
          </el-table>
        </section>

        <section class="report-section">
          <h3>五、持续改进建议</h3>
          <p v-if="aiSuggestion" class="report-paragraph">{{ aiSuggestion.improvement_actions }}</p>
          <div v-else class="pending-box">
            <div>
              <strong>待使用 AI 生成建议</strong>
              <p>请先生成本课程的 AI 建议，生成后这里会显示具体内容。</p>
            </div>
            <el-button type="primary" plain :loading="suggestionGenerating" @click="generateSuggestion">生成 AI 建议</el-button>
          </div>
        </section>
      </template>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import WorkflowGuide from '../components/WorkflowGuide.vue'
import { analysisRunApi, type AnalysisRunOverview, type DashboardPayload, type DataLineagePayload, type RunNarrative } from '../api/modules/analysis'
import { useAppStore } from '../stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const runs = ref<AnalysisRunOverview[]>([])
const selectedRunId = ref(0)
const dashboard = ref<DashboardPayload | null>(null)
const dataLineage = ref<DataLineagePayload | null>(null)
const reportNarrative = ref<RunNarrative | null>(null)
const aiSuggestion = ref<RunNarrative | null>(null)
const generating = ref(false)
const suggestionGenerating = ref(false)
const exporting = ref(false)

async function loadRuns() {
  runs.value = await analysisRunApi.list()
  const fromRoute = Number(route.query.run || appStore.selectedRunId || 0)
  selectedRunId.value = runs.value.some((item) => item.run.id === fromRoute) ? fromRoute : runs.value[0]?.run.id || 0
  if (selectedRunId.value) {
    appStore.selectedRunId = selectedRunId.value
    await loadDashboard()
  }
}

async function loadDashboard() {
  if (!selectedRunId.value) return
  const [dashboardData, narrativeData, suggestionData, lineageData] = await Promise.all([
    analysisRunApi.dashboard(selectedRunId.value),
    analysisRunApi.narrativeCache(selectedRunId.value),
    analysisRunApi.paperSummaryCache(selectedRunId.value),
    analysisRunApi.dataLineage(selectedRunId.value),
  ])
  dashboard.value = dashboardData
  dataLineage.value = lineageData
  reportNarrative.value = narrativeData.narrative
  aiSuggestion.value = suggestionData.cached && suggestionData.ai_enabled ? suggestionData.narrative : null
}

async function generateNarrative() {
  if (!selectedRunId.value) {
    ElMessage.warning('请先选择分析任务。')
    return
  }
  generating.value = true
  try {
    const data = await analysisRunApi.narrative(selectedRunId.value)
    reportNarrative.value = data.narrative
    ElMessage.success('报告正文已生成，请核对后导出。')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '生成报告文字失败，请稍后重试。')
  } finally {
    generating.value = false
  }
}

async function exportDocx() {
  if (!selectedRunId.value || !reportNarrative.value) {
    ElMessage.warning('请先生成报告文字，再导出报告。')
    return
  }
  exporting.value = true
  try {
    const blob = await analysisRunApi.exportDocx(selectedRunId.value)
    const href = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = href
    anchor.download = `试卷分析报告_${selectedRunId.value}.docx`
    anchor.click()
    URL.revokeObjectURL(href)
    ElMessage.success('报告已开始下载。')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '导出报告失败，请稍后重试。')
  } finally {
    exporting.value = false
  }
}

async function generateSuggestion() {
  if (!selectedRunId.value) return
  suggestionGenerating.value = true
  try {
    const data = await analysisRunApi.paperSummary(selectedRunId.value)
    aiSuggestion.value = data.ai_enabled ? data.narrative : null
    if (data.ai_enabled && data.narrative) {
      ElMessage.success('AI 建议已生成。')
    } else {
      ElMessage.warning('暂时无法生成建议，请稍后重试。')
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '生成 AI 建议失败，请稍后重试。')
  } finally {
    suggestionGenerating.value = false
  }
}

function onRunChange() {
  appStore.selectedRunId = selectedRunId.value
  router.replace({ path: '/report-preview', query: { run: String(selectedRunId.value) } })
  loadDashboard()
}

function sourceTone(method: string) {
  return `source-${method.replace('_', '-')}`
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

.lineage-panel {
  background:
    linear-gradient(135deg, rgba(239, 246, 255, 0.9), rgba(255, 255, 255, 0.96)),
    white;
}

.lineage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.9rem;
}

.lineage-card,
.section-source-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.86);
  padding: 1rem;
}

.lineage-card h4,
.section-lineage h4 {
  margin: 0.7rem 0 0.5rem;
  color: var(--ink-title);
}

.lineage-card p,
.section-source-item p {
  margin: 0;
  color: var(--ink-muted);
  line-height: 1.7;
}

.lineage-card small {
  display: block;
  margin-top: 0.55rem;
  color: var(--ink-body);
}

.source-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 0.24rem 0.55rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
}

.source-direct-read {
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
}

.source-computed {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.source-ai-generated {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.source-rendered-chart {
  background: rgba(14, 165, 233, 0.12);
  color: #0369a1;
}

.section-lineage {
  margin-top: 1.2rem;
}

.transfer-checklist {
  margin-top: 1.2rem;
  padding: 1rem;
  border-radius: var(--radius-lg);
  background: rgba(15, 23, 42, 0.03);
}

.transfer-checklist h4 {
  margin: 0 0 0.7rem;
  color: var(--ink-title);
}

.transfer-checklist ul {
  margin: 0;
  padding-left: 1.2rem;
  color: var(--ink-body);
  line-height: 1.85;
}

.section-source-list {
  display: grid;
  gap: 0.75rem;
}

.section-source-item {
  display: grid;
  grid-template-columns: minmax(160px, 220px) auto 1fr;
  align-items: start;
  gap: 0.85rem;
}

.section-source-item strong {
  color: var(--ink-title);
}

.report-preview {
  padding: 2rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 250, 252, 0.98)),
    white;
}

.report-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.report-kicker {
  margin: 0 0 0.5rem;
  color: var(--brand-primary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  font-weight: 700;
}

.report-header h2 {
  margin: 0;
  color: var(--ink-title);
}

.report-meta {
  margin: 0.7rem 0 0;
  color: var(--ink-muted);
}

.report-status {
  display: grid;
  gap: 0.7rem;
  align-content: start;
}

.report-status span {
  padding: 0.5rem 0.8rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: var(--brand-primary);
  font-weight: 600;
}

.report-empty {
  padding: 1.2rem;
  border-radius: var(--radius-lg);
  border: 1px dashed rgba(37, 99, 235, 0.18);
  background: rgba(239, 246, 255, 0.8);
}

.report-empty h4,
.report-section h3 {
  margin: 0;
  color: var(--ink-title);
}

.report-empty p,
.report-paragraph {
  margin: 0.8rem 0 0;
  color: var(--ink-body);
  line-height: 1.85;
}

.report-section + .report-section {
  margin-top: 1.8rem;
}

.pending-box {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-top: 0.9rem;
  padding: 1rem;
  border-radius: var(--radius-lg);
  background: rgba(241, 245, 249, 0.76);
  border: 1px dashed rgba(100, 116, 139, 0.24);
}

.pending-box strong {
  color: var(--ink-title);
}

.pending-box p {
  margin: 0.35rem 0 0;
  color: var(--ink-muted);
  line-height: 1.65;
}

.meta-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.9rem;
  margin-top: 1rem;
}

.meta-card,
.stats-card {
  padding: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
}

.meta-card span,
.stats-card span {
  display: block;
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.meta-card strong,
.stats-card strong {
  display: block;
  margin-top: 0.45rem;
  color: var(--ink-title);
  font-size: 1.1rem;
}

@media (max-width: 860px) {
  .report-header,
  .panel-header {
    flex-direction: column;
  }

  .section-source-item {
    grid-template-columns: 1fr;
  }

  .pending-box {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
