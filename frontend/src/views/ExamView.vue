<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header">
        <div class="header-titles">
          <h3>考试管理</h3>
          <p class="subtitle">统筹安排试卷、考核结构及细分成绩录入</p>
        </div>
        <div class="action-bar gap">
          <el-button-group class="modern-btn-group">
            <el-upload :show-file-list="false" :http-request="uploadQuestions" accept=".csv,.xlsx,.xls" class="upload-inline">
              <el-button plain class="action-btn">导入试卷结构</el-button>
            </el-upload>
            <el-upload :show-file-list="false" :http-request="uploadQuestionScores" accept=".csv,.xlsx,.xls" class="upload-inline">
              <el-button plain type="success" class="action-btn">导入分项成绩</el-button>
            </el-upload>
          </el-button-group>

          <el-button type="primary" class="primary-action-btn" @click="openCreateExam">
            + 新增考试
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="exams" class="premium-table" row-key="id">
          <el-table-column prop="name" label="考试名称" min-width="240">
            <template #default="{ row }">
              <span class="fw-bold">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="exam_type" label="考试类型" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="row.exam_type === 'final' ? 'danger' : (row.exam_type === 'mid' ? 'warning' : 'info')" effect="light" class="type-tag">
                {{ row.exam_type?.toUpperCase() === 'FINAL' ? '期末考试' : (row.exam_type?.toUpperCase() === 'MID' ? '期中考试' : '平时测验') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="考试日期" width="140">
            <template #default="{ row }">
              <span class="mono-id">{{ row.date }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_score" label="总分" width="100" align="center">
            <template #default="{ row }">
              <span class="mono-id">{{ row.total_score }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button link type="success" @click="openQuestionPanel(row)">试卷设计</el-button>
                <el-divider direction="vertical" />
                <el-button link type="primary" @click="openEditExam(row)">编辑</el-button>
                <el-divider direction="vertical" />
                <el-button link type="danger" @click="removeExam(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>

    <!-- EXAM DIALOG -->
    <el-dialog v-model="examDialog" :title="editingExamId ? '编辑考试设置' : '创建新考试'" width="540px" class="premium-dialog" destroy-on-close>
      <el-form :model="examForm" label-position="top" class="premium-form">
        <el-form-item label="所属课程" class="full-width">
          <el-select v-model="examForm.course_id" style="width: 100%" placeholder="选择课程...">
            <el-option v-for="course in courses" :key="course.id" :label="course.course_name" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试名称" class="full-width">
          <el-input v-model="examForm.name" placeholder="例如：2025期中考试..." />
        </el-form-item>
        
        <div class="form-grid" style="grid-template-columns: 1fr 1.5fr 1fr;">
          <el-form-item label="类型">
            <el-select v-model="examForm.exam_type" style="width: 100%">
              <el-option label="平时测试" value="usual" />
              <el-option label="期中考试" value="mid" />
              <el-option label="期末考试" value="final" />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker v-model="examForm.date" value-format="YYYY-MM-DD" style="width: 100%" placeholder="选择日期" />
          </el-form-item>
          <el-form-item label="试卷总分">
            <el-input-number v-model="examForm.total_score" :min="0" :max="500" style="width: 100%" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button plain @click="examDialog = false">取消</el-button>
        <el-button type="primary" @click="saveExam">保存考试</el-button>
      </template>
    </el-dialog>

    <!-- QUESTION STRUCTURE DRAWER -->
    <el-drawer v-model="questionDrawer" title="试卷结构设计" size="65%" class="premium-drawer">
      <div class="drawer-header-actions">
        <p class="subtitle">定义题目、分值以及认知能力和知识点的结构映射关系</p>
        <el-button type="primary" @click="openCreateQuestion">+ 添加大题/小题</el-button>
      </div>
      
      <div class="table-container" style="padding: 0 1rem;">
        <el-table :data="questions" class="premium-table borderless-drawer" height="calc(100vh - 180px)">
          <el-table-column prop="qno" label="题号" width="70">
            <template #default="{ row }">
              <span class="mono-id fw-bold">{{ row.qno }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="qtype" label="题型" width="120">
            <template #default="{ row }">
              <el-tag size="small" type="info" class="class-tag">{{ row.qtype || '基础类' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="分数" width="70" align="center">
            <template #default="{ row }">
              <span class="mono-id">{{ row.score }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="section" label="所属模块" width="110" />
          <el-table-column prop="knowledge_point" label="知识点 / 考核点" show-overflow-tooltip />
          <el-table-column prop="co_code" label="课程目标" width="100">
            <template #default="{ row }">
              <span v-if="row.co_code" class="indigo-badge">{{ row.co_code }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" align="center">
            <template #default="{ row }">
              <div class="row-actions always-visible">
                <el-button link type="primary" @click="openEditQuestion(row)">编辑</el-button>
                <el-divider direction="vertical" />
                <el-button link type="danger" @click="removeQuestion(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>

    <!-- QUESTION DIALOG -->
    <el-dialog v-model="questionDialog" :title="editingQuestionId ? '修改题目信息' : '添加题目信息'" width="500px" class="premium-dialog" destroy-on-close append-to-body>
      <el-form :model="questionForm" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="题号"><el-input v-model="questionForm.qno" placeholder="例如：1a" /></el-form-item>
          <el-form-item label="题型类别"><el-input v-model="questionForm.qtype" placeholder="单选题" /></el-form-item>
          <el-form-item label="分配分数"><el-input-number v-model="questionForm.score" :min="0" :max="100" style="width: 100%" /></el-form-item>
          <el-form-item label="所属大题板块"><el-input v-model="questionForm.section" placeholder="第一部分" /></el-form-item>
        </div>
        <el-form-item label="主要考查知识点" class="full-width"><el-input v-model="questionForm.knowledge_point" placeholder="例如：数据结构与算法..." /></el-form-item>
        <div class="form-grid">
          <el-form-item label="支撑课程目标 (CO)"><el-input v-model="questionForm.co_code" placeholder="CO-1" /></el-form-item>
          <el-form-item label="指标点编号 (可选)"><el-input v-model="questionForm.indicator_code" placeholder="1.2.3" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button plain @click="questionDialog = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存题目</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { importApi, type Course, type Exam, type Question, courseApi, examApi, questionApi } from '../api/modules/analysis'

const courses = ref<Course[]>([])
const exams = ref<Exam[]>([])
const questions = ref<Question[]>([])

const examDialog = ref(false)
const editingExamId = ref<number | null>(null)
const examForm = reactive<Omit<Exam, 'id'>>({
  course_id: 1,
  exam_type: 'final',
  name: '',
  date: new Date().toISOString().slice(0, 10),
  total_score: 100,
})

const questionDrawer = ref(false)
const questionDialog = ref(false)
const currentExamId = ref<number>(0)
const editingQuestionId = ref<number | null>(null)
const questionForm = reactive<Omit<Question, 'id'>>({
  exam_id: 0,
  qno: '',
  qtype: '',
  score: 0,
  section: '',
  knowledge_point: '',
  co_code: '',
  indicator_code: '',
})

async function load() {
  courses.value = await courseApi.list()
  exams.value = await examApi.list()
}

function resetExamForm() {
  examForm.course_id = courses.value[0]?.id || 1
  examForm.exam_type = 'final'
  examForm.name = ''
  examForm.date = new Date().toISOString().slice(0, 10)
  examForm.total_score = 100
}

function openCreateExam() {
  editingExamId.value = null
  resetExamForm()
  examDialog.value = true
}

function openEditExam(row: Exam) {
  editingExamId.value = row.id
  Object.assign(examForm, row)
  examDialog.value = true
}

async function saveExam() {
  if (editingExamId.value) {
    await examApi.update(editingExamId.value, examForm)
    ElMessage.success('Exam successfully updated.')
  } else {
    await examApi.create(examForm)
    ElMessage.success('Exam generated.')
  }
  examDialog.value = false
  await load()
}

async function removeExam(id: number) {
  await ElMessageBox.confirm('Permanent deletion will erase all mapped structure logs. Proceed?', 'Confirm Deletion', { 
    type: 'warning',
    confirmButtonText: 'Destroy',
    cancelButtonText: 'Cancel'
  })
  await examApi.remove(id)
  ElMessage.success('Exam wiped.')
  await load()
}

async function openQuestionPanel(exam: Exam) {
  currentExamId.value = exam.id
  questionDrawer.value = true
  questions.value = await questionApi.list(exam.id)
}

function resetQuestionForm() {
  questionForm.exam_id = currentExamId.value
  questionForm.qno = ''
  questionForm.qtype = ''
  questionForm.score = 0
  questionForm.section = ''
  questionForm.knowledge_point = ''
  questionForm.co_code = ''
  questionForm.indicator_code = ''
}

function openCreateQuestion() {
  editingQuestionId.value = null
  resetQuestionForm()
  questionDialog.value = true
}

function openEditQuestion(row: Question) {
  editingQuestionId.value = row.id
  Object.assign(questionForm, row)
  questionDialog.value = true
}

async function saveQuestion() {
  if (editingQuestionId.value) {
    await questionApi.update(editingQuestionId.value, questionForm)
  } else {
    questionForm.exam_id = currentExamId.value
    await questionApi.create(questionForm)
  }
  questionDialog.value = false
  questions.value = await questionApi.list(currentExamId.value)
  ElMessage.success('Blueprint item solidified.')
}

async function removeQuestion(id: number) {
  await ElMessageBox.confirm('Are you sure you want to drop this structural map item?', 'Delete Item', { 
    type: 'warning',
    confirmButtonText: 'Drop',
    cancelButtonText: 'Cancel'
  })
  await questionApi.remove(id)
  questions.value = await questionApi.list(currentExamId.value)
}

async function uploadQuestions(option: { file: File }) {
  const result = await importApi.questions(option.file)
  ElMessage.success(`Structures sync success: ${result.inserted} added, ${result.updated} updated, ${result.skipped} dropped.`)
  await load()
  if (questionDrawer.value && currentExamId.value) {
    questions.value = await questionApi.list(currentExamId.value)
  }
}

async function uploadQuestionScores(option: { file: File }) {
  const result = await importApi.questionScores(option.file)
  ElMessage.success(`Score matrix integrated: ${result.inserted} added, ${result.updated} updated, ${result.skipped} ignored.`)
}

onMounted(load)
</script>

<style scoped>
.panel-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 1.5rem;
}

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

.upload-inline {
  display: inline-block;
}

.modern-btn-group {
  display: flex;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  border-radius: var(--radius-sm);
  background: #fff;
}

.action-btn {
  border-radius: 0;
  border: 1px solid var(--border-strong);
  margin: 0 !important;
  font-family: var(--font-body);
}

.upload-inline:first-child .action-btn {
  border-top-left-radius: var(--radius-sm);
  border-bottom-left-radius: var(--radius-sm);
  border-right: none;
}
.upload-inline:last-child .action-btn {
  border-top-right-radius: var(--radius-sm);
  border-bottom-right-radius: var(--radius-sm);
}

.primary-action-btn {
  padding: 0 1.25rem;
}

.table-container {
  margin: 0 -0.5rem;
}

.premium-table {
  --el-table-bg-color: transparent;
}

.mono-id {
  font-family: var(--font-display);
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  color: var(--ink-muted);
  font-size: 0.95rem;
}

.fw-bold {
  font-weight: 600;
  color: var(--ink-title);
}

.class-tag {
  font-family: var(--font-display);
  font-weight: 500;
  border-radius: 6px;
  background-color: transparent;
}
.type-tag {
  border: none;
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.05em;
  background-color: rgba(var(--el-color-info-rgb), 0.1);
}

.indigo-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 600;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  opacity: 0.6;
  transition: var(--trans-fast);
}

.always-visible {
  opacity: 0.9;
}

.premium-table:deep(.el-table__row:hover) .row-actions {
  opacity: 1;
}

/* Dialog & Drawer Overrides */
.premium-form .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1rem;
}

.premium-form .full-width {
  grid-column: 1 / -1;
}

.premium-form :deep(.el-form-item__label) {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--ink-title);
  padding-bottom: 4px;
}

.premium-form :deep(.el-input__wrapper),
.premium-form :deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px var(--border-strong) !important;
  border-radius: var(--radius-sm);
}
.premium-form :deep(.el-input__wrapper.is-focus),
.premium-form :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px var(--brand-primary) !important;
}

.drawer-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0 1.5rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 1rem;
}

.drawer-header-actions .subtitle {
  color: var(--ink-muted);
  margin: 0;
  font-size: 0.95rem;
}

.borderless-drawer {
  --el-table-border: none;
}
.borderless-drawer::before { display: none; }
</style>
