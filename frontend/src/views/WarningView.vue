<template>
  <section class="page-grid">
    <WorkflowGuide :active-step="4" />

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>AI 建议中心</h3>
          <p class="subtitle">根据本次成绩和课程目标，生成可放入报告的改进建议。</p>
        </div>
        <div class="action-bar">
          <el-select v-model="suggestionTemplate" style="width: 230px" placeholder="选择生成模板">
            <el-option label="按课程目标逐项生成" value="per_outcome" />
            <el-option label="AI 自由生成" value="free" />
          </el-select>
          <el-select v-model="selectedRunId" style="width: 360px" @change="onRunChange">
            <el-option v-for="item in runs" :key="item.run.id" :label="`${item.course_name} / ${item.run.class_name} / ${item.exam_name}`" :value="item.run.id" />
          </el-select>
          <el-button type="primary" :loading="generating" @click="generateNarrative" :disabled="!selectedRunId">生成 AI 建议</el-button>
        </div>
      </div>
      <div class="template-hint">
        <span class="hint-label">当前模板</span>
        <span>{{ suggestionTemplate === 'per_outcome' ? '逐个课程目标生成针对性建议，并汇总到持续改进建议中。' : '由 AI 根据整体成绩、题型和课程目标自由组织建议。' }}</span>
      </div>

      <div v-if="!aiNarrative" class="empty-state">
        <h4>建议待生成</h4>
        <p>点击“生成 AI 建议”后，将显示本课程的改进建议。</p>
      </div>

      <div v-else class="narrative-grid">
        <article class="narrative-card">
          <h4>成绩统计摘要</h4>
          <p>{{ aiNarrative.score_summary }}</p>
        </article>
        <article class="narrative-card">
          <h4>课程目标支撑度分析</h4>
          <p>{{ aiNarrative.support_analysis }}</p>
        </article>
        <article class="narrative-card">
          <h4>课程目标达成度分析</h4>
          <p>{{ aiNarrative.attainment_analysis }}</p>
        </article>
        <article class="narrative-card emphasis">
          <h4>持续改进建议</h4>
          <p>{{ aiNarrative.improvement_actions }}</p>
        </article>
      </div>
    </article>

    <article class="card panel" v-if="summary">
      <div class="panel-header compact">
        <h3>重点学生预警</h3>
      </div>
      <el-table :data="summary.warnings" class="premium-table">
        <el-table-column prop="student_no" label="学号" width="140" />
        <el-table-column prop="student_name" label="姓名" width="120" />
        <el-table-column prop="final_score" label="期末卷面" width="110" />
        <el-table-column prop="course_total_score" label="课程总评" width="110" />
        <el-table-column prop="level" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="row.level === 'critical' ? 'danger' : 'warning'" effect="light">
              {{ row.level === 'critical' ? '严重' : '一般' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警原因">
          <template #default="{ row }">
            <div class="reason-list">
              <span v-for="reason in row.reasons" :key="reason" class="reason-pill">{{ reason }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import WorkflowGuide from '../components/WorkflowGuide.vue'
import { analysisRunApi, type AiSuggestionTemplate, type AnalysisRunOverview, type RunNarrative, type WarningPreview } from '../api/modules/analysis'
import { useAppStore } from '../stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const runs = ref<AnalysisRunOverview[]>([])
const selectedRunId = ref(0)
const summary = ref<{ warnings: WarningPreview[] } | null>(null)
const aiNarrative = ref<RunNarrative | null>(null)
const generating = ref(false)
const suggestionTemplate = ref<AiSuggestionTemplate>('per_outcome')

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
    await loadSummary()
  }
}

async function loadSummary() {
  if (!selectedRunId.value) return
  try {
    const data = await analysisRunApi.paperSummaryCache(selectedRunId.value)
    summary.value = { warnings: data.warnings }
    aiNarrative.value = data.cached && data.ai_enabled ? data.narrative : null
  } catch (error) {
    ElMessage.error((error as Error).message || '加载预警数据失败')
  }
}

async function generateNarrative() {
  if (!selectedRunId.value) return
  const shouldReplace = Boolean(aiNarrative.value)
  if (shouldReplace) {
    try {
      await ElMessageBox.confirm('当前分析任务已生成过 AI 建议。是否重新生成并替换原来的建议内容？', '重新生成建议', {
        type: 'warning',
        confirmButtonText: '重新生成并替换',
        cancelButtonText: '取消',
      })
    } catch {
      return
    }
  }
  generating.value = true
  try {
    const data = await analysisRunApi.paperSummary(selectedRunId.value, {
      template: suggestionTemplate.value,
      force: shouldReplace,
    })
    aiNarrative.value = data.ai_enabled ? data.narrative : null
    if (data.ai_enabled && data.narrative) {
      ElMessage.success(shouldReplace ? 'AI 建议已重新生成并替换。' : 'AI 建议已生成。')
    } else {
      ElMessage.warning('暂时无法生成建议，请稍后重试。')
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '生成 AI 建议失败，请稍后重试。')
  } finally {
    generating.value = false
  }
}

function onRunChange() {
  appStore.selectedRunId = selectedRunId.value
  router.replace({ path: '/warnings', query: { run: String(selectedRunId.value) } })
  loadSummary()
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

.template-hint {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  margin: -0.55rem 0 1.2rem;
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.07);
  color: var(--ink-muted);
  font-size: 0.88rem;
}

.hint-label {
  font-weight: 800;
  color: #1d4ed8;
}

.empty-state {
  padding: 1.1rem 1.2rem;
  border-radius: var(--radius-lg);
  border: 1px dashed rgba(37, 99, 235, 0.2);
  background: rgba(239, 246, 255, 0.7);
}

.empty-state h4 {
  margin: 0;
  color: var(--ink-title);
}

.empty-state p {
  margin: 0.65rem 0 0;
  color: var(--ink-muted);
  line-height: 1.8;
}

.narrative-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.narrative-card {
  padding: 1rem;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.78);
}

.narrative-card.emphasis {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.07), rgba(16, 185, 129, 0.07));
}

.narrative-card h4 {
  margin: 0;
  color: var(--ink-title);
}

.narrative-card p {
  margin: 0.8rem 0 0;
  color: var(--ink-body);
  line-height: 1.8;
}

.reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reason-pill {
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.18);
  font-size: 0.82rem;
}

@media (max-width: 860px) {
  .narrative-grid {
    grid-template-columns: 1fr;
  }
}
</style>
