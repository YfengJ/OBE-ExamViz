<template>
  <div class="course-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleAdd">添加课程</el-button>
        </div>
      </template>

      <el-table :data="courses" style="width: 100%" border>
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="course_name" label="课程名称" width="200" />
        <el-table-column prop="term" label="学期" width="100" />
        <el-table-column prop="department" label="院系" width="150" />
        <el-table-column prop="major" label="专业" width="150" />
        <el-table-column prop="credit" label="学分" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="courseForm" label-width="100px">
        <el-form-item label="课程代码">
          <el-input v-model="courseForm.course_code" />
        </el-form-item>
        <el-form-item label="课程名称">
          <el-input v-model="courseForm.course_name" />
        </el-form-item>
        <el-form-item label="学期">
          <el-input v-model="courseForm.term" placeholder="如：2024-2025-1" />
        </el-form-item>
        <el-form-item label="院系">
          <el-input v-model="courseForm.department" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="courseForm.major" />
        </el-form-item>
        <el-form-item label="学分">
          <el-input-number v-model="courseForm.credit" :min="0" :precision="1" />
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="courseForm.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Course {
  id: number
  course_code: string
  course_name: string
  term: string
  department: string
  major: string
  credit: number
  description: string
}

const courses = ref<Course[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加课程')
const courseForm = ref({
  course_code: '',
  course_name: '',
  term: '',
  department: '',
  major: '',
  credit: 0.0,
  description: ''
})

const fetchCourses = async () => {
  try {
    const response = await axios.get('/api/analysis/courses')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加课程'
  courseForm.value = {
    course_code: '',
    course_name: '',
    term: '',
    department: '',
    major: '',
    credit: 0.0,
    description: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: Course) => {
  dialogTitle.value = '编辑课程'
  courseForm.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: Course) => {
  try {
    await ElMessageBox.confirm('确认删除该课程？')
    await axios.delete(`/api/analysis/courses/${row.id}`)
    ElMessage.success('删除成功')
    fetchCourses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSave = async () => {
  try {
    if (dialogTitle.value === '添加课程') {
      await axios.post('/api/analysis/courses', courseForm.value)
    } else {
      await axios.put(`/api/analysis/courses/${courseForm.value.id}`, courseForm.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchCourses()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
.course-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>