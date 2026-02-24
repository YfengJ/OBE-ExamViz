<template>
  <div class="student-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生管理</span>
          <el-button type="primary" @click="handleAdd">添加学生</el-button>
        </div>
      </template>

      <div class="operation-bar">
        <el-upload
          action="/api/analysis/upload-csv"
          accept=".csv"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          style="display: inline-block; margin-right: 10px"
        >
          <el-button type="success">导入CSV</el-button>
        </el-upload>
        <el-button type="warning" @click="handleExport">导出</el-button>
      </div>

      <el-table :data="students" style="width: 100%; margin-top: 20px" border>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="120" />
        <el-table-column prop="major" label="专业" width="150" />
        <el-table-column prop="grade_year" label="年级" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 20px; text-align: center"
        v-model:currentPage="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="studentForm" label-width="80px">
        <el-form-item label="学号">
          <el-input v-model="studentForm.student_no" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="studentForm.name" />
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="studentForm.class_name" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="studentForm.major" />
        </el-form-item>
        <el-form-item label="年级">
          <el-input v-model="studentForm.grade_year" />
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

interface Student {
  id: number
  student_no: string
  name: string
  class_name: string
  major: string
  grade_year: string
}

const students = ref<Student[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('添加学生')
const studentForm = ref({
  student_no: '',
  name: '',
  class_name: '',
  major: '',
  grade_year: ''
})

const fetchStudents = async () => {
  try {
    const response = await axios.get('/api/analysis/students', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    students.value = response.data
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加学生'
  studentForm.value = {
    student_no: '',
    name: '',
    class_name: '',
    major: '',
    grade_year: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: Student) => {
  dialogTitle.value = '编辑学生'
  studentForm.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row: Student) => {
  try {
    await ElMessageBox.confirm('确认删除该学生？')
    await axios.delete(`/api/analysis/students/${row.id}`)
    ElMessage.success('删除成功')
    fetchStudents()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSave = async () => {
  try {
    if (dialogTitle.value === '添加学生') {
      await axios.post('/api/analysis/students', studentForm.value)
    } else {
      await axios.put(`/api/analysis/students/${studentForm.value.id}`, studentForm.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchStudents()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleUploadSuccess = () => {
  ElMessage.success('导入成功')
  fetchStudents()
}

const handleExport = () => {
  ElMessage.info('导出功能待实现')
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchStudents()
}

onMounted(() => {
  fetchStudents()
})
</script>

<style scoped>
.student-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.operation-bar {
  margin-bottom: 20px;
}
</style>