<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header">
        <div class="header-titles">
          <h3>学生名单</h3>
          <p class="subtitle">管理班级学生及成绩导入</p>
        </div>
        <div class="action-bar gap">
          <el-input 
            v-model="classFilter" 
            placeholder="按班级筛选" 
            class="premium-input"
            clearable 
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-button-group class="modern-btn-group">
            <el-upload :show-file-list="false" :http-request="uploadStudents" accept=".csv,.xlsx,.xls" class="upload-inline">
              <el-button plain class="action-btn">导入名单</el-button>
            </el-upload>
            <el-upload :show-file-list="false" :http-request="uploadExamScores" accept=".csv,.xlsx,.xls" class="upload-inline">
              <el-button plain type="success" class="action-btn">导入成绩</el-button>
            </el-upload>
          </el-button-group>

          <el-button type="primary" class="primary-action-btn" @click="openCreate">
            + 新增学生
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="students" class="premium-table" row-key="id">
          <el-table-column prop="student_no" label="学号" width="160">
            <template #default="{ row }">
              <span class="mono-id">{{ row.student_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="姓名" width="160">
            <template #default="{ row }">
              <span class="fw-bold">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="class_name" label="班级" width="140">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" class="class-tag">{{ row.class_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="major" label="专业" />
          <el-table-column prop="grade_year" label="年级" width="100" align="center" />
          <el-table-column label="操作" width="150" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
                <el-divider direction="vertical" />
                <el-button link type="danger" @click="remove(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑学生' : '新增学生'" width="480px" class="premium-dialog" destroy-on-close>
      <el-form :model="form" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="学号"><el-input v-model="form.student_no" placeholder="例如 20230001"/></el-form-item>
          <el-form-item label="姓名"><el-input v-model="form.name" placeholder="张三" /></el-form-item>
          <el-form-item label="班级"><el-input v-model="form.class_name" placeholder="计科2301"/></el-form-item>
          <el-form-item label="年级"><el-input v-model="form.grade_year" placeholder="2023" /></el-form-item>
        </div>
        <el-form-item label="专业"><el-input v-model="form.major" placeholder="计算机科学与技术..."/></el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存学生</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { importApi, type Student, studentApi } from '../api/modules/analysis'

const students = ref<Student[]>([])
const classFilter = ref('')
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive<Omit<Student, 'id'>>({
  student_no: '',
  name: null,
  class_name: '',
  major: '',
  grade_year: '',
})

const query = computed(() => ({ class_name: classFilter.value || undefined, limit: 1000 }))
watch(query, () => load(), { deep: true })

function resetForm() {
  form.student_no = ''
  form.name = null
  form.class_name = ''
  form.major = ''
  form.grade_year = ''
}

async function load() {
  students.value = await studentApi.list(query.value)
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Student) {
  editingId.value = row.id
  form.student_no = row.student_no
  form.name = row.name
  form.class_name = row.class_name
  form.major = row.major
  form.grade_year = row.grade_year
  dialogVisible.value = true
}

async function save() {
  if (!form.student_no || !form.class_name || !form.major || !form.grade_year) {
    ElMessage.warning('所有内容必填。')
    return
  }
  if (editingId.value) {
    await studentApi.update(editingId.value, form)
    ElMessage.success('学生记录已更新。')
  } else {
    await studentApi.create(form)
    ElMessage.success('新学生已注册。')
  }
  dialogVisible.value = false
  await load()
}

async function remove(id: number) {
  await ElMessageBox.confirm('确定要永久删除该名学生吗？', '确认删除', { 
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await studentApi.remove(id)
  ElMessage.success('学生已删除。')
  await load()
}

async function uploadStudents(option: { file: File }) {
  const result = await importApi.students(option.file)
  ElMessage.success(`导入完成: 新增 ${result.inserted} 条, 更新 ${result.updated} 条, 跳过 ${result.skipped} 条。`)
  await load()
}

async function uploadExamScores(option: { file: File }) {
  const result = await importApi.examScores(option.file)
  ElMessage.success(`导入成绩: 新增 ${result.inserted} 条, 更新 ${result.updated} 条, 跳过 ${result.skipped} 条。`)
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

.premium-input {
  width: 240px !important;
  --el-input-border-radius: var(--radius-sm);
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
  border-color: var(--border-subtle);
  color: var(--ink-body);
  border-radius: 6px;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  opacity: 0.6;
  transition: var(--trans-fast);
}

.premium-table:deep(.el-table__row:hover) .row-actions {
  opacity: 1;
}

/* Dialog Styles */
.premium-form .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1rem;
}

.premium-form :deep(.el-form-item__label) {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--ink-title);
  padding-bottom: 4px;
}

.premium-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--border-strong) !important;
  border-radius: var(--radius-sm);
}
.premium-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--brand-primary) !important;
}
</style>
