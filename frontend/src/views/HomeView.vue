<template>
  <section class="page-grid">
    <WorkflowGuide :active-step="1" />

    <article class="card panel hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">试卷分析工作台</p>
        <h2>上传成绩，生成一份可检查的试卷分析报告</h2>
        <p class="hero-text">
          选择课程后上传成绩工作簿，先查看计算结果，再生成报告文字和改进建议。
          关键数据都能回到本次班级和试卷，后续核对更清楚。
        </p>
      </div>
      <div class="hero-stats">
        <div class="stat-box">
          <span>分析任务</span>
          <strong>{{ runs.length }}</strong>
        </div>
        <div class="stat-box">
          <span>已就绪任务</span>
          <strong>{{ readyCount }}</strong>
        </div>
        <div class="stat-box">
          <span>待关注任务</span>
          <strong>{{ warningCount }}</strong>
        </div>
      </div>
    </article>

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>本次分析怎么完成</h3>
          <p class="subtitle">先导入成绩，再核对计算结果，最后生成报告。</p>
        </div>
        <el-button type="primary" class="primary-action-btn" @click="goImportCenter">打开数据导入</el-button>
      </div>
      <div class="guide-grid">
        <article class="guide-card">
          <span class="guide-index">01</span>
          <h4>输入文件</h4>
          <p>上传课程成绩工作簿，读取课程、班级、学生成绩和试卷结构。</p>
        </article>
        <article class="guide-card">
          <span class="guide-index">02</span>
          <h4>计算结果</h4>
          <p>生成成绩分布、题型表现、课程目标达成度和重点预警。</p>
        </article>
        <article class="guide-card">
          <span class="guide-index">03</span>
          <h4>报告导出</h4>
          <p>预览报告正文，确认内容后导出 Word 文档。</p>
        </article>
      </div>
    </article>

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>任务列表</h3>
          <p class="subtitle">选择一门课程，继续导入、计算或生成报告。</p>
        </div>
        <div class="panel-actions">
          <el-button plain @click="loadRuns">刷新</el-button>
          <el-button type="primary" class="primary-action-btn" @click="goCreateCourse">+ 新建课程</el-button>
        </div>
      </div>
      <div class="run-grid">
        <article v-for="item in runs" :key="item.run.id" class="run-card">
          <div class="run-card-top">
            <div>
              <h4>{{ item.course_name }}</h4>
              <p>{{ item.run.class_name }} · {{ item.exam_name }}</p>
            </div>
            <el-tag :type="item.run.status === 'ready' ? 'success' : (item.run.status === 'partial' ? 'warning' : 'info')" effect="light">
              {{ item.run.status }}
            </el-tag>
          </div>
          <div class="run-meta">
            <span>{{ item.run.academic_year }}</span>
            <span>{{ item.run.term_label }}</span>
            <span>{{ item.run.teacher_name || '未填写教师' }}</span>
          </div>
          <div class="progress-list">
            <span :class="{ ok: item.progress.has_students }">学生成绩</span>
            <span :class="{ ok: item.progress.has_final_scores }">卷面总分</span>
            <span :class="{ ok: item.progress.has_questions }">试卷结构</span>
            <span :class="{ ok: item.run.status === 'ready' }">可生成报告</span>
          </div>
          <div class="run-next">
            <span>建议下一步</span>
            <strong>{{ runNextAction(item).label }}</strong>
            <el-button size="small" type="primary" plain @click="goWithRun(runNextAction(item).path, item.run.id)">继续</el-button>
          </div>
          <div class="run-actions">
            <el-button text type="primary" @click="goWithRun('/exams', item.run.id)">数据导入</el-button>
            <el-button text type="success" @click="goWithRun('/analysis', item.run.id)">结构分析</el-button>
            <el-button text type="warning" @click="goWithRun('/report-preview', item.run.id)">报告预览</el-button>
            <el-button text @click="goWithRun('/warnings', item.run.id)">AI建议</el-button>
          </div>
        </article>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import WorkflowGuide from '../components/WorkflowGuide.vue'
import { analysisRunApi, type AnalysisRunOverview } from '../api/modules/analysis'
import { useAppStore } from '../stores/app'

const router = useRouter()
const appStore = useAppStore()

const runs = ref<AnalysisRunOverview[]>([])
const readyCount = computed(() => runs.value.filter((item) => item.run.status === 'ready').length)
const warningCount = computed(() => runs.value.filter((item) => item.run.status !== 'ready').length)

async function loadRuns() {
  runs.value = await analysisRunApi.list()
}

function goImportCenter() {
  router.push('/exams')
}

function goCreateCourse() {
  router.push({ path: '/courses', query: { create: '1' } })
}

function goWithRun(path: string, runId: number) {
  appStore.selectedRunId = runId
  router.push({ path, query: { run: String(runId) } })
}

function runNextAction(item: AnalysisRunOverview) {
  if (item.run.status === 'ready') {
    return { label: '生成或核对报告', path: '/report-preview' }
  }
  if (!item.progress.has_final_scores) {
    return { label: '导入学生成绩', path: '/exams' }
  }
  if (!item.progress.has_questions) {
    return { label: '补齐试卷结构', path: '/exams' }
  }
  return { label: '补齐逐题得分并重新计算', path: '/exams' }
}

onMounted(loadRuns)
</script>

<style scoped>
.hero-panel {
  display: grid;
  grid-template-columns: 1.7fr 1fr;
  gap: 1.5rem;
  align-items: center;
}

.eyebrow {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 700;
}

.hero-copy h2 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.25;
  color: var(--ink-title);
}

.hero-text {
  margin: 1rem 0 0;
  color: var(--ink-muted);
  line-height: 1.8;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-box {
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-subtle);
  padding: 1rem;
}

.stat-box span {
  display: block;
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.stat-box strong {
  display: block;
  margin-top: 0.65rem;
  font-size: 1.6rem;
  color: var(--ink-title);
  font-family: var(--font-display);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.panel-actions {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--ink-muted);
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.guide-card {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
  border-radius: var(--radius-lg);
  padding: 1rem;
}

.guide-index {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: var(--brand-gradient);
  color: white;
  font-weight: 700;
}

.guide-card h4 {
  margin: 0.9rem 0 0.6rem;
  color: var(--ink-title);
}

.guide-card p {
  margin: 0;
  color: var(--ink-muted);
  line-height: 1.7;
}

.run-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.run-card {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
  border-radius: var(--radius-xl);
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  min-height: 255px;
}

.run-card-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.run-card-top h4 {
  margin: 0;
  color: var(--ink-title);
}

.run-card-top p {
  margin: 0.4rem 0 0;
  color: var(--ink-muted);
  line-height: 1.6;
}

.run-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
  color: var(--ink-muted);
  font-size: 0.9rem;
}

.progress-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 1rem;
}

.progress-list span {
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.14);
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.progress-list span.ok {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.run-next {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.6rem;
  margin-top: 1rem;
  padding: 0.7rem;
  border-radius: var(--radius-lg);
  background: rgba(37, 99, 235, 0.06);
}

.run-next span {
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.run-next strong {
  color: var(--ink-title);
  font-size: 0.92rem;
}

.run-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: auto;
  padding-top: 1rem;
}

@media (max-width: 960px) {
  .hero-panel {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .hero-stats {
    grid-template-columns: 1fr;
  }

  .panel-header {
    flex-direction: column;
  }
}
</style>
