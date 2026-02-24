<template>
  <div class="exam-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考试管理</span>
          <el-button type="primary" @click="handleAdd">添加考试</el-button>
        </div>
      </template>

      <el-table :data="exams" style="width: 100%" border>
        <el-table-column prop="name" label="考试名称" width="150" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="exam_type" label="考试类型" width="100">
          <template #default="scope">
            <el-tag :type="getExamTypeTag(scope.row.exam_type)">
              {{ getExamTypeLabel(scope.row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="考试日期" width="120" />
        <el-table-column prop="total_score" label="满分" width="80" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleQuestions(scope.row)">题目</el-button>
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form :model="examForm" label-width="100px">
          <el-form-item label="课程">
            <el-select v-model="examForm.course_id" style="width: 100%">
              <el-option
                v-for="course in courses"
                :key="course.id"
                :label="course.course_name"
                :value="course.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试名称">
            <el-input v-model="examForm.name" />
          </el-form-item>
          <el-form-item label="考试类型">
            <el-select v-model="examForm.exam_type" style="width: 100%">
              <el-option label="平时" value="usual" />
              <el-option label="期中" value="mid" />
              <el-option label="期末" value="final" />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker v-model="examForm.date" type="date" style="width: 100%" />
          </el-form-item>
          <el-form-item label="满分">
            <el-input-number v-model="examForm.total_score" :min="0" :max="1000" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>

      <!-- 题目管理对话框 -->
      <el-dialog v-model="questionDialogVisible" title="题目管理" width="800px">
        <el-button type="success" @click="handleAddQuestion" style="margin-bottom: 20px">添加题目</el-button>
        <el-table :data="questions" style="width: 100%" border>
          <el-table-column prop="qno" label="题号" width="80" />
          <el-table-column prop="qtype" label="题型" width="100" />
          <el-table-column prop="score" label="分值" width="80" />
          <el-table-column prop="section" label="章节" width="120" />
          <el-table-column prop="knowledge_point" label="知识点" width="150" />
          <el-table-column prop="co_code" label="CO代码" width="100" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEditQuestion(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDeleteQuestion(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Exam {
  id: number
  course_id: number
  course_name: string
  exam_type: string
  name: string
  date: string
  total_score: number
}

interface Course {
  id: number
  course_name: string
}

interface Question {
  id: number
  exam_id: number
  qno: string
  qtype: string
  score: number
  section: string
  knowledge_point: string
  co_code: string
}

const exams = ref<Exam[]>([])
const courses = ref<Course[]>([])
const questions = ref<Question[]>([])
const dialogVisible = ref(false)
const questionDialogVisible = ref(false)
const dialogTitle = ref('添加考试')
const currentExamId = ref(0)

const examForm = ref({
  course_id: 0,
  exam_type: 'final',
  name: '',
  date: '',
  total_score: 100
})

const getExamTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    usual: 'success',
    mid: 'warning',
    final: 'danger'
  }
  return tags[type] || 'info'
}

const getExamTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    usual: '平时',
    mid: '期中',
    final: '期末'
  }
  return labels[type] || type
}

const fetchExams = async () => {
  try {
    const response = await axios.get('/api/analysis/exams')
    exams.value = response.data
  } catch (error) {
    ElMessage.error('获取考试列表失败')
  }
}

const fetchCourses = async () => {
  try {
    const response = await axios.get('/api/analysis/courses')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加考试'
  examForm.value = {
    course_id: 0,
    exam_type: 'final',
    name: '',
    date: '',
    total_score: 100
  }
  dialogVisible.value = true
}

const handleEdit = (row: Exam) => {
  dialogTitle.value = '编辑考试'
  examForm.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: Exam) => {
  try {
    await ElMessageBox.confirm('确认删除该考试？')
    await axios.delete(`/api/analysis/exams/${row.id}`)
    ElMessage.success('删除成功')
    fetchExams()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSave = async () => {
  try {
    if (dialogTitle.value === '添加考试') {
      await axios.post('/api/analysis/exams', examForm.value)
    } else {
      await axios.put(`/api/analysis/exams/${examForm.value.id}`, examForm.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchExams()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleQuestions = async (row: Exam) => {
  currentExamId.value = row.id
  questionDialogVisible.value = true
  fetchQuestions()
}

const fetchQuestions = async () => {
  try {
    const response = await axios.get(`/api/analysis/questions?exam_id=${currentExamId.value}`)
    questions.value = response.data
  } catch (error) {
    ElMessage.error('获取题目列表失败')
  }
}

const handleAddQuestion = () => {
  ElMessage.info('添加题目功能待实现')
}

const handleEditQuestion = (row: Question) => {
  ElMessage.info('编辑题目功能待实现')
}

const handleDeleteQuestion = async (row: Question) => {
  try {
    await ElMessageBox.confirm('确认删除该题目？')
    await axios.delete(`/api/analysis/questions/${row.id}`)
    ElMessage.success('删除成功')
    fetchQuestions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchExams()
  fetchCourses()
})
</script>

<style scoped>
.exam-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>