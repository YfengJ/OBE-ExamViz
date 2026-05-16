<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header">
        <div class="header-titles">
          <h3>课程参数中心</h3>
          <p class="subtitle">管理课程、考试和题目参数，为成绩分析提供基础数据。</p>
        </div>
        <div class="action-bar gap">
          <el-button type="primary" class="primary-action-btn" @click="openCreateCourse">
            + 新增课程
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="visibleCourses" class="premium-table" row-key="id" @row-click="selectCourse">
          <el-table-column prop="course_code" label="课程代码" width="150">
            <template #default="{ row }">
              <span class="mono-id fw-bold">{{ row.course_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="course_name" label="课程名称" min-width="220">
            <template #default="{ row }">
              <div class="title-cell">
                <span class="fw-bold">{{ row.course_name }}</span>
                <span v-if="row.id === selectedCourseId" class="current-pill">当前课程</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="term" label="开设学期" width="140">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" class="class-tag">{{ row.term }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="开设学院" width="180" />
          <el-table-column prop="major" label="适用专业" width="180" show-overflow-tooltip />
          <el-table-column prop="owner" label="课程负责人" width="140">
            <template #default="{ row }">{{ row.owner || '未填写' }}</template>
          </el-table-column>
          <el-table-column prop="credit" label="学分" width="90" align="center" />
          <el-table-column label="操作" width="260" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button size="small" class="table-action table-action-primary" @click.stop="openEditCourse(row)">编辑课程</el-button>
                <el-button size="small" class="table-action table-action-neutral" @click.stop="selectCourse(row)">设为当前</el-button>
                <el-button size="small" class="table-action table-action-danger" @click.stop="removeCourse(row.id)">删除课程</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>

    <div class="grid-2-col">
      <article class="card panel">
        <div class="panel-header compact">
          <div>
            <h3>期末考试</h3>
            <p class="subtitle">选择课程后，可维护对应的期末考试。</p>
          </div>
          <div class="action-bar gap">
            <el-select v-model="selectedCourseId" style="width: 260px" placeholder="选择课程">
              <el-option
                v-for="item in courses"
                :key="item.id"
                :label="`${item.course_name} (${item.course_code})`"
                :value="item.id"
              />
            </el-select>
            <el-button type="primary" class="primary-action-btn" @click="openCreateExam" :disabled="!selectedCourseId">
              + 新增考试
            </el-button>
          </div>
        </div>

        <el-empty v-if="!selectedCourseId" description="请先选择一门课程" />
        <el-empty v-else-if="!courseExams.length" description="当前课程还没有考试，请先新增一个期末考试" />
        <el-table v-else :data="courseExams" class="premium-table" row-key="id" @row-click="selectExam">
          <el-table-column prop="name" label="考试名称" min-width="220">
            <template #default="{ row }">
              <div class="title-cell">
                <span class="fw-bold">{{ row.name }}</span>
                <span v-if="row.id === selectedExamId" class="current-pill">当前考试</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="exam_type" label="类型" width="120" />
          <el-table-column prop="date" label="日期" width="130" />
          <el-table-column prop="total_score" label="总分" width="90" align="center" />
          <el-table-column label="操作" width="260" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button size="small" class="table-action table-action-primary" @click.stop="openEditExam(row)">编辑考试</el-button>
                <el-button size="small" class="table-action table-action-neutral" @click.stop="selectExam(row)">设为当前</el-button>
                <el-button size="small" class="table-action table-action-danger" @click.stop="removeExam(row.id)">删除考试</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </article>

      <article class="card panel">
        <div class="panel-header compact">
          <div>
            <h3>试卷题目</h3>
            <p class="subtitle">题目分值和课程目标对应关系会用于后续分析。</p>
          </div>
          <div class="action-bar gap">
            <el-select v-model="selectedExamId" style="width: 260px" placeholder="选择考试" :disabled="!courseExams.length">
              <el-option
                v-for="item in courseExams"
                :key="item.id"
                :label="`${item.name} (${item.date})`"
                :value="item.id"
              />
            </el-select>
            <el-button type="primary" class="primary-action-btn" @click="openCreateQuestion" :disabled="!selectedExamId">
              + 新增题目
            </el-button>
          </div>
        </div>

        <el-empty v-if="!selectedCourseId" description="请先选择课程" />
        <el-empty v-else-if="!selectedExamId" description="请先为当前课程选择一个考试" />
        <el-empty v-else-if="!questions.length" description="当前考试还没有题目，请先新增题目" />
        <el-table v-else :data="questions" class="premium-table" row-key="id">
          <el-table-column prop="qno" label="题号" width="90" />
          <el-table-column prop="qtype" label="题型" width="120" />
          <el-table-column prop="qgroup_name" label="题组 / 分组" width="140" />
          <el-table-column prop="score" label="分值" width="90" align="center" />
          <el-table-column prop="co_code" label="课程目标" width="120" />
          <el-table-column prop="indicator_code" label="指标点" width="120" />
          <el-table-column label="操作" width="190" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button size="small" class="table-action table-action-primary" @click.stop="openEditQuestion(row)">编辑题目</el-button>
                <el-button size="small" class="table-action table-action-danger" @click.stop="removeQuestion(row.id)">删除题目</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </article>
    </div>

    <el-dialog v-model="courseDialogVisible" :title="editingCourseId ? '编辑课程' : '新增课程'" width="560px" class="premium-dialog" destroy-on-close>
      <div v-if="!editingCourseId" class="syllabus-import-card">
        <div>
          <strong>通过教学大纲自动新建</strong>
          <p>上传 docx 或 Excel 教学大纲后，系统会读取课程代码、名称、学分、负责人和课程目标。</p>
        </div>
        <el-upload :show-file-list="false" :http-request="(option) => createCourseBySyllabus(option.file as File)" accept=".docx,.xlsx,.xls,.xlsm,.txt">
          <el-button plain :loading="syllabusUploading">上传教学大纲</el-button>
        </el-upload>
      </div>
      <el-form :model="courseForm" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="课程代码"><el-input v-model="courseForm.course_code" placeholder="如 CS-101" /></el-form-item>
          <el-form-item label="开设学期"><el-input v-model="courseForm.term" placeholder="2025-2026-1" /></el-form-item>
          <el-form-item label="课程名称" class="full-width"><el-input v-model="courseForm.course_name" placeholder="计算机科学导论" /></el-form-item>
          <el-form-item label="开设学院"><el-input v-model="courseForm.department" placeholder="信息学院" /></el-form-item>
          <el-form-item label="适用专业"><el-input v-model="courseForm.major" placeholder="计算机科学" /></el-form-item>
          <el-form-item label="课程负责人"><el-input v-model="courseForm.owner" placeholder="如 张老师" /></el-form-item>
          <el-form-item label="学分"><el-input-number v-model="courseForm.credit" :min="0" :step="0.5" style="width: 100%" /></el-form-item>
        </div>
        <el-form-item label="课程描述">
          <el-input v-model="courseForm.description" type="textarea" :rows="3" placeholder="简要描述该课程..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="courseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCourse">保存课程</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="examDialogVisible" :title="editingExamId ? '编辑考试' : '新增考试'" width="520px" class="premium-dialog" destroy-on-close>
      <el-form :model="examForm" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="所属课程">
            <el-select v-model="examForm.course_id" style="width: 100%">
              <el-option
                v-for="item in courses"
                :key="item.id"
                :label="`${item.course_name} (${item.course_code})`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试类型">
            <el-select v-model="examForm.exam_type" style="width: 100%">
              <el-option label="final" value="final" />
              <el-option label="midterm" value="midterm" />
              <el-option label="quiz" value="quiz" />
            </el-select>
          </el-form-item>
          <el-form-item label="考试名称" class="full-width">
            <el-input v-model="examForm.name" placeholder="如 示例课程期末考试" />
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker v-model="examForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="卷面总分">
            <el-input-number v-model="examForm.total_score" :min="0" :step="5" style="width: 100%" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button plain @click="examDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveExam">保存考试</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="questionDialogVisible" :title="editingQuestionId ? '编辑题目' : '新增题目'" width="620px" class="premium-dialog" destroy-on-close>
      <el-form :model="questionForm" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="所属考试">
            <el-select v-model="questionForm.exam_id" style="width: 100%">
              <el-option
                v-for="item in courseExams"
                :key="item.id"
                :label="`${item.name} (${item.date})`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="题号">
            <el-input v-model="questionForm.qno" placeholder="如 1 或 2-1" />
          </el-form-item>
          <el-form-item label="题型">
            <el-input v-model="questionForm.qtype" placeholder="选择题 / 简答题 / 综合题" />
          </el-form-item>
          <el-form-item label="题组 / 分组">
            <el-input v-model="questionForm.qgroup_name" placeholder="如 选择题" />
          </el-form-item>
          <el-form-item label="小题号">
            <el-input v-model="questionForm.sub_qno" placeholder="可选" />
          </el-form-item>
          <el-form-item label="分值">
            <el-input-number v-model="questionForm.score" :min="0" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="课程目标">
            <el-input v-model="questionForm.co_code" placeholder="如 CO1" />
          </el-form-item>
          <el-form-item label="指标点">
            <el-input v-model="questionForm.indicator_code" placeholder="如 IND1" />
          </el-form-item>
          <el-form-item label="课程目标权重">
            <el-input-number v-model="questionForm.co_weight" :min="0" :max="1" :step="0.1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="达成阈值">
            <el-input-number v-model="questionForm.expected_threshold" :min="0" :max="1" :step="0.05" style="width: 100%" />
          </el-form-item>
          <el-form-item label="章节">
            <el-input v-model="questionForm.section" placeholder="如 第 3 章" />
          </el-form-item>
          <el-form-item label="知识点">
            <el-input v-model="questionForm.knowledge_point" placeholder="如 二叉树遍历" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button plain @click="questionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveQuestion">保存题目</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { courseApi, examApi, questionApi, type Course, type Exam, type Question } from '../api/modules/analysis'

const route = useRoute()
const router = useRouter()
const courses = ref<Course[]>([])
const exams = ref<Exam[]>([])
const questions = ref<Question[]>([])

const selectedCourseId = ref<number | null>(null)
const selectedExamId = ref<number | null>(null)
const syllabusUploading = ref(false)

const courseDialogVisible = ref(false)
const examDialogVisible = ref(false)
const questionDialogVisible = ref(false)

const editingCourseId = ref<number | null>(null)
const editingExamId = ref<number | null>(null)
const editingQuestionId = ref<number | null>(null)

const visibleCourses = computed(() => courses.value)
const courseExams = computed(() => exams.value.filter((item) => item.course_id === selectedCourseId.value))

const courseForm = reactive<Omit<Course, 'id'>>({
  course_code: '',
  course_name: '',
  term: '2025-2026-1',
  department: '',
  major: '',
  credit: 0,
  owner: '',
  description: '',
})

const examForm = reactive<Omit<Exam, 'id'>>({
  course_id: 0,
  exam_type: 'final',
  name: '',
  date: '2026-01-15',
  total_score: 100,
})

const questionForm = reactive<Omit<Question, 'id'>>({
  exam_id: 0,
  qno: '',
  qtype: '',
  qgroup_name: '',
  sub_qno: '',
  score: 10,
  section: '',
  knowledge_point: '',
  co_code: '',
  indicator_code: '',
  co_weight: 1,
  expected_threshold: 0.65,
})

watch(selectedCourseId, () => {
  const availableExamIds = courseExams.value.map((item) => item.id)
  if (!availableExamIds.length) {
    selectedExamId.value = null
    questions.value = []
    return
  }
  if (!selectedExamId.value || !availableExamIds.includes(selectedExamId.value)) {
    selectedExamId.value = availableExamIds[0]
  }
})

watch(selectedExamId, () => {
  loadQuestions()
})

function resetCourseForm() {
  courseForm.course_code = ''
  courseForm.course_name = ''
  courseForm.term = '2025-2026-1'
  courseForm.department = ''
  courseForm.major = ''
  courseForm.credit = 0
  courseForm.owner = ''
  courseForm.description = ''
}

function resetExamForm() {
  examForm.course_id = selectedCourseId.value || courses.value[0]?.id || 0
  examForm.exam_type = 'final'
  examForm.name = ''
  examForm.date = '2026-01-15'
  examForm.total_score = 100
}

function resetQuestionForm() {
  questionForm.exam_id = selectedExamId.value || 0
  questionForm.qno = ''
  questionForm.qtype = ''
  questionForm.qgroup_name = ''
  questionForm.sub_qno = ''
  questionForm.score = 10
  questionForm.section = ''
  questionForm.knowledge_point = ''
  questionForm.co_code = ''
  questionForm.indicator_code = ''
  questionForm.co_weight = 1
  questionForm.expected_threshold = 0.65
}

async function loadBase() {
  const [courseRows, examRows] = await Promise.all([courseApi.list(), examApi.list()])
  courses.value = courseRows
  exams.value = examRows
  if (!selectedCourseId.value && courses.value.length) {
    selectedCourseId.value = courses.value[0].id
  } else if (selectedCourseId.value && !courses.value.some((item) => item.id === selectedCourseId.value)) {
    selectedCourseId.value = courses.value[0]?.id || null
  }
  if (selectedExamId.value && !exams.value.some((item) => item.id === selectedExamId.value)) {
    selectedExamId.value = null
  }
  await loadQuestions()
}

async function loadQuestions() {
  if (!selectedExamId.value) {
    questions.value = []
    return
  }
  questions.value = await questionApi.list(selectedExamId.value)
}

function selectCourse(row: Course) {
  selectedCourseId.value = row.id
}

function selectExam(row: Exam) {
  selectedExamId.value = row.id
}

function openCreateCourse() {
  editingCourseId.value = null
  resetCourseForm()
  courseDialogVisible.value = true
}

function openEditCourse(row: Course) {
  editingCourseId.value = row.id
  Object.assign(courseForm, { ...row, owner: row.owner || '', description: row.description || '' })
  courseDialogVisible.value = true
}

async function saveCourse() {
  if (!courseForm.course_code || !courseForm.course_name || !courseForm.term) {
    ElMessage.warning('请填写课程代码、课程名称和学期。')
    return
  }
  if (editingCourseId.value) {
    await courseApi.update(editingCourseId.value, courseForm)
    ElMessage.success('课程信息已更新。')
  } else {
    const created = await courseApi.create(courseForm)
    selectedCourseId.value = created.id
    ElMessage.success('课程已创建，可以继续新增考试。')
  }
  courseDialogVisible.value = false
  await loadBase()
}

async function createCourseBySyllabus(file: File) {
  syllabusUploading.value = true
  try {
    const result = await courseApi.createFromSyllabus(file)
    selectedCourseId.value = result.course.id
    courseDialogVisible.value = false
    await loadBase()
    ElMessage.success(`已从教学大纲创建课程：${result.course.course_name}，并识别 ${result.outcomes.length} 个课程目标。`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '教学大纲识别失败，请检查文件内容。')
  } finally {
    syllabusUploading.value = false
  }
}

async function removeCourse(id: number) {
  await ElMessageBox.confirm('确定删除该课程吗？系统会同时删除该课程下的考试、题目、成绩、分析任务和已生成建议。', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await courseApi.remove(id)
  ElMessage.success('课程已删除。')
  await loadBase()
}

function openCreateExam() {
  if (!selectedCourseId.value) {
    ElMessage.warning('请先选择课程。')
    return
  }
  editingExamId.value = null
  resetExamForm()
  examDialogVisible.value = true
}

function openEditExam(row: Exam) {
  editingExamId.value = row.id
  Object.assign(examForm, row)
  examDialogVisible.value = true
}

async function saveExam() {
  if (!examForm.course_id || !examForm.name || !examForm.date) {
    ElMessage.warning('请填写所属课程、考试名称和日期。')
    return
  }
  if (editingExamId.value) {
    await examApi.update(editingExamId.value, examForm)
    ElMessage.success('考试信息已更新。')
  } else {
    const created = await examApi.create(examForm)
    selectedCourseId.value = created.course_id
    selectedExamId.value = created.id
    ElMessage.success('考试已创建，可以继续新增题目。')
  }
  examDialogVisible.value = false
  await loadBase()
}

async function removeExam(id: number) {
  await ElMessageBox.confirm('确定删除该考试吗？已录入题目的考试不能直接删除。', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await examApi.remove(id)
  ElMessage.success('考试已删除。')
  await loadBase()
}

function openCreateQuestion() {
  if (!selectedExamId.value) {
    ElMessage.warning('请先选择考试。')
    return
  }
  editingQuestionId.value = null
  resetQuestionForm()
  questionDialogVisible.value = true
}

function openEditQuestion(row: Question) {
  editingQuestionId.value = row.id
  Object.assign(questionForm, {
    ...row,
    qgroup_name: row.qgroup_name || '',
    sub_qno: row.sub_qno || '',
    section: row.section || '',
    knowledge_point: row.knowledge_point || '',
    co_code: row.co_code || '',
    indicator_code: row.indicator_code || '',
    co_weight: row.co_weight ?? 1,
    expected_threshold: row.expected_threshold ?? 0.65,
  })
  questionDialogVisible.value = true
}

async function saveQuestion() {
  if (!questionForm.exam_id || !questionForm.qno || !questionForm.qtype) {
    ElMessage.warning('请填写所属考试、题号和题型。')
    return
  }
  const payload = {
    ...questionForm,
    qgroup_name: questionForm.qgroup_name || null,
    sub_qno: questionForm.sub_qno || null,
    section: questionForm.section || null,
    knowledge_point: questionForm.knowledge_point || null,
    co_code: questionForm.co_code || null,
    indicator_code: questionForm.indicator_code || null,
    co_weight: questionForm.co_weight ?? null,
    expected_threshold: questionForm.expected_threshold ?? null,
  }
  if (editingQuestionId.value) {
    await questionApi.update(editingQuestionId.value, payload)
    ElMessage.success('题目已更新。')
  } else {
    await questionApi.create(payload)
    ElMessage.success('题目已创建。')
  }
  questionDialogVisible.value = false
  await loadQuestions()
  await loadBase()
}

async function removeQuestion(id: number) {
  await ElMessageBox.confirm('确定删除该题目吗？已有逐题得分的题目不能直接删除。', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await questionApi.remove(id)
  ElMessage.success('题目已删除。')
  await loadQuestions()
}

onMounted(async () => {
  await loadBase()
  if (route.query.create === '1') {
    openCreateCourse()
    router.replace({ path: '/courses' })
  }
})
</script>

<style scoped>
.panel-header {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.panel-header.compact {
  margin-bottom: 1rem;
}

.header-titles .subtitle,
.subtitle {
  margin: 0.25rem 0 0;
  color: var(--ink-muted);
  font-size: 0.9rem;
}

.action-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.premium-switch {
  background: #f8fafc;
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
}

.primary-action-btn {
  padding: 0 1.25rem;
}

.syllabus-import-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.95rem;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(37, 99, 235, 0.16);
  background:
    linear-gradient(135deg, rgba(239, 246, 255, 0.9), rgba(255, 255, 255, 0.95)),
    white;
}

.syllabus-import-card strong {
  color: var(--ink-title);
}

.syllabus-import-card p {
  margin: 0.35rem 0 0;
  color: var(--ink-muted);
  line-height: 1.6;
  font-size: 0.88rem;
}

.table-container {
  margin: 0 -0.5rem;
}

.premium-table {
  --el-table-bg-color: transparent;
}

.grid-2-col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 1rem;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.current-pill {
  padding: 0.12rem 0.55rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: var(--brand-primary);
  font-size: 0.78rem;
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.mono-id {
  font-family: var(--font-display);
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  font-size: 0.95rem;
}

.fw-bold {
  font-weight: 600;
  color: var(--ink-title);
}

.class-tag {
  font-family: var(--font-display);
  border-color: var(--border-subtle);
  color: var(--ink-body);
  border-radius: 6px;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  opacity: 1;
  flex-wrap: wrap;
}

.table-action {
  min-width: 68px;
  height: 30px;
  padding: 0 0.65rem;
  border-radius: 999px;
  font-weight: 700;
  box-shadow: none;
  letter-spacing: 0;
}

.table-action-primary {
  color: #1d4ed8;
  background: #eff6ff;
  border: 1px solid #93c5fd;
}

.table-action-primary:hover {
  color: #ffffff;
  background: #2563eb;
  border-color: #2563eb;
}

.table-action-neutral {
  color: #334155;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
}

.table-action-neutral:hover {
  color: #0f172a;
  background: #e2e8f0;
  border-color: #94a3b8;
}

.table-action-danger {
  color: #b91c1c;
  background: #fff1f2;
  border: 1px solid #fda4af;
}

.table-action-danger:hover {
  color: #ffffff;
  background: #dc2626;
  border-color: #dc2626;
}

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
.premium-form :deep(.el-textarea__inner),
.premium-form :deep(.el-select__wrapper) {
  box-shadow: 0 0 0 1px var(--border-strong) !important;
  border-radius: var(--radius-sm);
}

.premium-form :deep(.el-input__wrapper.is-focus),
.premium-form :deep(.el-textarea__inner:focus),
.premium-form :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px var(--brand-primary) !important;
}

@media (max-width: 960px) {
  .grid-2-col {
    grid-template-columns: 1fr;
  }

  .syllabus-import-card {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
