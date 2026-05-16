<template>
  <section class="page-grid">
    <WorkflowGuide :active-step="2" />

    <article class="card panel">
      <div class="panel-header">
        <div>
          <h3>数据导入中心</h3>
          <p class="subtitle">上传系统模板或老师原始成绩表，读取原始成绩后再开始计算。</p>
        </div>
        <div class="action-bar">
          <el-select v-model="selectedRunId" style="width: 360px" @change="syncRoute">
            <el-option v-for="item in runs" :key="item.run.id" :label="`${item.course_name} / ${item.run.class_name} / ${item.exam_name}`" :value="item.run.id" />
          </el-select>
          <el-button plain :disabled="!selectedRunId" @click="goAnalysis">查看结构分析</el-button>
        </div>
      </div>

      <div class="io-grid">
        <article class="io-card input">
          <span class="io-badge">输入文件</span>
          <h4>成绩工作簿</h4>
          <p>支持系统简洁模板、老师原始成绩表和达成度分析表，系统会统一识别课程、班级、题型和得分。</p>
        </article>
        <article class="io-card process">
          <span class="io-badge">计算步骤</span>
          <h4>点击开始计算</h4>
          <p>确认文件读取成功后，计算成绩分布、题型表现和课程目标达成度。</p>
        </article>
        <article class="io-card output">
          <span class="io-badge">输出结果</span>
          <h4>分析报告文档</h4>
          <p>核对计算结果后，生成报告正文并导出 Word 文档。</p>
        </article>
      </div>
    </article>

    <article class="card panel">
      <div class="panel-header compact">
        <div>
          <h3>输入要求与生成逻辑</h3>
          <p class="subtitle">换一门课程时，只需要准备这些原始数据。</p>
        </div>
      </div>

      <div class="requirement-grid">
        <article v-for="item in inputRequirementCards" :key="item.name" class="requirement-card">
          <div class="requirement-topline">
            <span>{{ item.required ? '必需' : '可选' }}</span>
            <small v-if="item.current_status">{{ item.current_status === 'ready' ? '已识别' : '待识别' }}</small>
          </div>
          <h4>{{ item.name }}</h4>
          <p>{{ item.source }}</p>
          <div class="field-chips">
            <span v-for="field in item.fields" :key="field">{{ field }}</span>
          </div>
        </article>
      </div>
    </article>

    <article class="card panel">
      <div class="panel-header compact">
        <div>
          <h3>示例文件</h3>
          <p class="subtitle">下载简洁输入模板和输出文档样式，用于核对格式。</p>
        </div>
      </div>
      <div class="template-grid">
        <button
          v-for="item in templates"
          :key="item.file"
          class="template-button"
          type="button"
          @click="downloadTemplate(item.file)"
        >
          <strong>{{ item.label }}</strong>
          <span>{{ item.description }}</span>
        </button>
      </div>
    </article>

    <article class="card panel">
      <div class="panel-header compact">
        <div>
          <h3>上传并识别</h3>
          <p class="subtitle">先上传文件，再点击计算查看结果。</p>
        </div>
      </div>

      <div class="import-card">
        <el-input v-model="teacherExamDate" placeholder="考试日期（可选，如 2025年6月22日）" class="import-input" />
        <div class="field-spec">
          上传后先读取文件中的原始数据，平均分、达成度和图表会在点击“开始计算”后由系统生成。
        </div>
        <el-upload :show-file-list="false" :http-request="(option) => previewTeacherWorkbook(option.file as File)" accept=".xlsx,.xls,.xlsm">
          <el-button type="primary" style="width: 100%">上传成绩文件</el-button>
        </el-upload>

        <div v-if="pendingTeacherPreview && !teacherPreview" class="calculation-ready">
          <div>
            <h4>文件已读取</h4>
            <p>{{ pendingTeacherPreview.source_filename || '成绩输入模板' }} 已完成结构识别。点击开始计算后，将显示成绩统计、课程目标和题型分析结果。</p>
          </div>
          <el-button type="success" :loading="calculating" @click="showCalculationResults">开始计算</el-button>
        </div>

        <div v-if="teacherPreview" class="teacher-preview">
          <div class="preview-grid">
            <div class="preview-item"><span>课程</span><strong>{{ teacherPreview.meta.course_name || '未识别' }}</strong></div>
            <div class="preview-item"><span>班级</span><strong>{{ teacherPreview.meta.class_name || '未识别' }}</strong></div>
            <div class="preview-item"><span>教师</span><strong>{{ teacherPreview.meta.teacher_name || '未识别' }}</strong></div>
            <div class="preview-item"><span>学生数</span><strong>{{ teacherPreview.score_stats.total_students }}</strong></div>
            <div class="preview-item"><span>平均分</span><strong>{{ teacherPreview.score_stats.average_score }}</strong></div>
            <div class="preview-item"><span>报告文字</span><strong>待生成</strong></div>
          </div>

          <div class="preview-block">
            <h4>计算结果</h4>
            <p>工作表：{{ teacherPreview.recognized_sheets.join(' / ') }}</p>
            <p>课程目标：{{ teacherPreview.course_outcome_count }} 个，题型：{{ teacherPreview.question_group_count }} 类，题目项：{{ teacherPreview.question_item_count }} 个。</p>
          </div>

          <div class="preview-block formula-block">
            <h4>计算说明</h4>
            <div class="formula-grid">
              <div v-for="item in calculationNotes" :key="item.title" class="formula-item">
                <strong>{{ item.title }}</strong>
                <span>{{ item.text }}</span>
              </div>
            </div>
          </div>

          <div v-if="teacherPreview.data_sources?.length" class="preview-block">
            <h4>生成依据</h4>
            <div class="source-list">
              <div v-for="item in teacherPreview.data_sources" :key="item.title" class="source-row">
                <span :class="['source-pill', sourceTone(item.source_method)]">{{ item.source_label }}</span>
                <strong>{{ item.title }}</strong>
                <p>{{ item.source }}</p>
              </div>
            </div>
          </div>

          <div class="preview-block">
            <h4>接下来可以做什么</h4>
            <div class="output-list">
              <div class="output-card">
                <strong>创建分析任务</strong>
                <span>保存本次计算结果，后续可以查看结构分析、生成建议和导出报告。</span>
              </div>
              <div class="output-card">
                <strong>直接生成文档</strong>
                <span>适合先快速核对 Word 报告版式和内容。</span>
              </div>
            </div>
          </div>

          <div class="button-stack">
            <el-button type="success" style="width: 100%" :loading="reportLoading" @click="generateTeacherWorkbookReport">
              直接生成文档
            </el-button>
            <el-button type="primary" plain style="width: 100%" :loading="importLoading" @click="importTeacherWorkbookTask">
              导入并创建分析任务
            </el-button>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import WorkflowGuide from '../components/WorkflowGuide.vue'
import { analysisRunApi, importApi, type AnalysisRunOverview, type InputRequirement, type TeacherWorkbookPreview, type TeacherWorkbookTaskResult } from '../api/modules/analysis'
import { useAppStore } from '../stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const runs = ref<AnalysisRunOverview[]>([])
const selectedRunId = ref(0)
const teacherExamDate = ref('')
const teacherWorkbookFile = ref<File | null>(null)
const pendingTeacherPreview = ref<TeacherWorkbookPreview | null>(null)
const teacherPreview = ref<TeacherWorkbookPreview | null>(null)
const calculating = ref(false)
const reportLoading = ref(false)
const importLoading = ref(false)

const templates = [
  { label: '成绩输入模板', description: '只保留系统生成报告所需的原始数据字段。', file: 'teacher_input_template.xlsx' },
  { label: '报告样式示例', description: '用于核对最终输出文档的版式。', file: 'teacher_report_template.docx' },
]

const defaultInputRequirements: InputRequirement[] = [
  {
    name: '课程与考试基本信息',
    required: true,
    source: '成绩文件中的基本信息区域',
    fields: ['课程名称', '教学班级', '院系', '任课教师', '学年学期', '考试日期'],
    used_for: ['报告首页基本信息', '任务列表筛选'],
    current_status: 'pending',
  },
  {
    name: '学生名单与期末卷面成绩',
    required: true,
    source: '成绩文件中的学生成绩表',
    fields: ['学号', '姓名', '期末总分'],
    used_for: ['人数统计', '平均分', '分数段统计'],
    current_status: 'pending',
  },
  {
    name: '题型、题号与逐题得分',
    required: true,
    source: '成绩文件中的试卷结构与学生逐题得分',
    fields: ['题型', '题号', '题目满分', '学生逐题得分'],
    used_for: ['题型分析', '逐题分析', '达成度分布图'],
    current_status: 'pending',
  },
  {
    name: '课程目标与试题支撑关系',
    required: true,
    source: '成绩文件中的课程目标和题目对应关系',
    fields: ['课程目标编号', '课程目标说明', '题目对应课程目标', '目标阈值'],
    used_for: ['支撑度分析', '达成度分析', '持续改进建议'],
    current_status: 'pending',
  },
]

const inputRequirementCards = computed(() => {
  const preview = teacherPreview.value || pendingTeacherPreview.value
  return preview?.input_requirements?.length ? preview.input_requirements : defaultInputRequirements
})

const calculationNotes = [
  { title: '成绩统计', text: '平均分、最高分、最低分和及格率由期末卷面总分计算。' },
  { title: '分数段', text: '按 90-100、80-89、70-79、60-69、60 分以下统计人数和占比。' },
  { title: '题型表现', text: '先汇总每名学生同一题型得分，再计算题型平均分和得分率。' },
  { title: '课程目标', text: '按题目对应的课程目标汇总得分，达成度 = 平均得分 ÷ 对应满分。' },
]

async function loadRuns() {
  runs.value = await analysisRunApi.list()
  const fromRoute = Number(route.query.run || appStore.selectedRunId || 0)
  selectedRunId.value = runs.value.some((item) => item.run.id === fromRoute) ? fromRoute : runs.value[0]?.run.id || 0
  if (selectedRunId.value) {
    appStore.selectedRunId = selectedRunId.value
  }
}

function syncRoute() {
  appStore.selectedRunId = selectedRunId.value
  router.replace({ path: '/exams', query: { run: String(selectedRunId.value) } })
}

function goAnalysis() {
  if (!selectedRunId.value) return
  appStore.selectedRunId = selectedRunId.value
  router.push({ path: '/analysis', query: { run: String(selectedRunId.value) } })
}

function downloadTemplate(file: string) {
  window.open(`/api/v1/import/templates/${file}?t=${Date.now()}`, '_blank')
}

function sourceTone(method: string) {
  return `source-${method.replace('_', '-')}`
}

async function handleTeacherWorkbook(file: File) {
  reportLoading.value = true
  try {
    const blob = await importApi.teacherWorkbookReport(file, teacherExamDate.value)
    downloadBlob(blob, `${file.name.replace(/\.(xlsx|xls|xlsm)$/i, '')}_试卷分析报告.docx`)
    ElMessage.success('文档已生成，浏览器开始下载。')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '文档生成失败，请稍后重试。')
  } finally {
    reportLoading.value = false
  }
}

async function previewTeacherWorkbook(file: File) {
  teacherWorkbookFile.value = file
  teacherPreview.value = null
  pendingTeacherPreview.value = null
  try {
    pendingTeacherPreview.value = await importApi.teacherWorkbookPreview(file, teacherExamDate.value)
    ElMessage.success('文件已读取，请点击“开始计算”。')
  } catch (error) {
    pendingTeacherPreview.value = null
    teacherPreview.value = null
    ElMessage.error(error instanceof Error ? error.message : '文件识别失败，请检查后重试。')
  }
}

async function showCalculationResults() {
  if (!pendingTeacherPreview.value) return
  calculating.value = true
  try {
    await new Promise<void>((resolve) => window.setTimeout(resolve, 240))
    teacherPreview.value = pendingTeacherPreview.value
    ElMessage.success('计算完成，可以查看结果。')
  } finally {
    calculating.value = false
  }
}

async function generateTeacherWorkbookReport() {
  if (!teacherWorkbookFile.value) {
    ElMessage.warning('请先上传成绩文件并完成计算。')
    return
  }
  if (!teacherPreview.value) {
    ElMessage.warning('请先点击“开始计算”。')
    return
  }
  await handleTeacherWorkbook(teacherWorkbookFile.value)
}

async function importTeacherWorkbookTask() {
  if (!teacherWorkbookFile.value) {
    ElMessage.warning('请先上传成绩文件并完成计算。')
    return
  }
  if (!teacherPreview.value) {
    ElMessage.warning('请先点击“开始计算”。')
    return
  }
  importLoading.value = true
  try {
    const result: TeacherWorkbookTaskResult = await importApi.teacherWorkbookTask(teacherWorkbookFile.value, teacherExamDate.value)
    await loadRuns()
    selectedRunId.value = result.run_overview.run.id
    syncRoute()
    ElMessage.success(`已创建分析任务：${result.run_overview.course_name} / ${result.run_overview.run.class_name}。`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建分析任务失败，请稍后重试。')
  } finally {
    importLoading.value = false
  }
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  window.URL.revokeObjectURL(url)
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

.io-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.io-card {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
  border-radius: var(--radius-lg);
  padding: 1rem;
}

.io-card.input {
  border-color: rgba(37, 99, 235, 0.18);
}

.io-card.process {
  border-color: rgba(16, 185, 129, 0.18);
}

.io-card.output {
  border-color: rgba(245, 158, 11, 0.18);
}

.io-badge {
  display: inline-block;
  margin-bottom: 0.6rem;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 700;
}

.io-card h4 {
  margin: 0 0 0.75rem;
  color: var(--ink-title);
}

.io-card p {
  margin: 0;
  color: var(--ink-muted);
  line-height: 1.7;
}

.requirement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.9rem;
}

.requirement-card {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.84);
  border-radius: var(--radius-lg);
  padding: 1rem;
}

.requirement-topline {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 700;
}

.requirement-topline small {
  color: var(--ink-muted);
  font-weight: 600;
}

.requirement-card h4 {
  margin: 0.65rem 0 0.45rem;
  color: var(--ink-title);
}

.requirement-card p {
  margin: 0;
  color: var(--ink-muted);
  line-height: 1.65;
}

.field-chips {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-top: 0.85rem;
}

.field-chips span {
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: var(--ink-body);
  font-size: 0.78rem;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
}

.template-button {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.85);
  padding: 1rem;
  text-align: left;
  cursor: pointer;
  transition: var(--trans-fast);
}

.template-button:hover {
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.2);
  box-shadow: 0 8px 18px -14px rgba(15, 23, 42, 0.55);
}

.template-button strong {
  display: block;
  color: var(--ink-title);
}

.template-button span {
  display: block;
  margin-top: 0.45rem;
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.import-card {
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
  border-radius: var(--radius-lg);
  padding: 1rem;
}

.import-input {
  margin-bottom: 0.85rem;
}

.field-spec {
  margin-bottom: 1rem;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-lg);
  background: rgba(59, 130, 246, 0.07);
  color: var(--ink-muted);
  line-height: 1.75;
}

.teacher-preview {
  margin-top: 1rem;
  display: grid;
  gap: 1rem;
}

.calculation-ready {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(16, 185, 129, 0.22);
  background:
    linear-gradient(135deg, rgba(236, 253, 245, 0.92), rgba(255, 255, 255, 0.92)),
    white;
}

.calculation-ready h4 {
  margin: 0;
  color: var(--ink-title);
}

.calculation-ready p {
  margin: 0.45rem 0 0;
  color: var(--ink-muted);
  line-height: 1.65;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.85rem;
}

.preview-item,
.output-card,
.preview-block {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.82);
}

.preview-item {
  padding: 0.95rem;
}

.preview-item span {
  display: block;
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.preview-item strong {
  display: block;
  margin-top: 0.45rem;
  color: var(--ink-title);
}

.preview-block {
  padding: 1rem;
}

.preview-block h4 {
  margin: 0 0 0.7rem;
  color: var(--ink-title);
}

.preview-block p {
  margin: 0.4rem 0 0;
  color: var(--ink-muted);
  line-height: 1.75;
}

.formula-block {
  background:
    linear-gradient(135deg, rgba(239, 246, 255, 0.88), rgba(255, 255, 255, 0.9)),
    rgba(255, 255, 255, 0.82);
}

.formula-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
}

.formula-item {
  padding: 0.85rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(37, 99, 235, 0.1);
}

.formula-item strong {
  display: block;
  color: var(--ink-title);
}

.formula-item span {
  display: block;
  margin-top: 0.4rem;
  color: var(--ink-muted);
  line-height: 1.6;
}

.source-list {
  display: grid;
  gap: 0.75rem;
}

.source-row {
  display: grid;
  grid-template-columns: auto minmax(120px, 180px) 1fr;
  gap: 0.75rem;
  align-items: start;
  padding: 0.8rem;
  border-radius: var(--radius-md);
  background: rgba(248, 250, 252, 0.86);
}

.source-row strong {
  color: var(--ink-title);
}

.source-row p {
  margin: 0;
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

.output-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.85rem;
}

.output-card {
  padding: 0.95rem;
}

.output-card strong {
  display: block;
  color: var(--ink-title);
}

.output-card span {
  display: block;
  margin-top: 0.45rem;
  color: var(--ink-muted);
  line-height: 1.7;
}

.button-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.85rem;
}

@media (max-width: 720px) {
  .panel-header {
    flex-direction: column;
  }

  .calculation-ready {
    align-items: stretch;
    flex-direction: column;
  }

  .source-row {
    grid-template-columns: 1fr;
  }
}
</style>
