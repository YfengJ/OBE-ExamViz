<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header">
        <div class="header-titles">
          <h3>课程总览</h3>
          <p class="subtitle">管理学科课程信息</p>
        </div>
        <div class="action-bar gap">
          <div class="premium-switch">
             <el-switch v-model="showAll" active-text="全部显示" inactive-text="仅看示例" inline-prompt style="--el-switch-on-color: var(--brand-primary); --el-switch-off-color: var(--ink-muted);" />
          </div>
          <el-button type="primary" class="primary-action-btn" @click="openCreate">
            + 新增课程
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="visibleCourses" class="premium-table" row-key="id">
          <el-table-column prop="course_code" label="课程代码" width="130">
            <template #default="{ row }">
              <span class="mono-id fw-bold">{{ row.course_code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="course_name" label="课程名称" min-width="220">
            <template #default="{ row }">
              <span class="fw-bold">{{ row.course_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="term" label="开设学期" width="140">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" class="class-tag">{{ row.term }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="开设学院" width="180" />
          <el-table-column prop="major" label="适用专业" width="180" show-overflow-tooltip/>
          <el-table-column prop="credit" label="学分" width="90" align="center" />
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑课程' : '新增课程'" width="540px" class="premium-dialog" destroy-on-close>
      <el-form :model="form" label-position="top" class="premium-form">
        <div class="form-grid">
          <el-form-item label="课程代码"><el-input v-model="form.course_code" placeholder="如 CS-101" /></el-form-item>
          <el-form-item label="开设学期"><el-input v-model="form.term" placeholder="2025-2026-1" /></el-form-item>
          <el-form-item label="课程名称" class="full-width"><el-input v-model="form.course_name" placeholder="计算机科学导论" /></el-form-item>
          <el-form-item label="开设学院"><el-input v-model="form.department" placeholder="信息学院" /></el-form-item>
          <el-form-item label="适用专业"><el-input v-model="form.major" placeholder="计算机科学" /></el-form-item>
          <el-form-item label="学分"><el-input-number v-model="form.credit" :min="0" :step="0.5" style="width: 100%" /></el-form-item>
        </div>
        <el-form-item label="课程描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="简要描述该课程..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存课程</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { type Course, courseApi } from '../api/modules/analysis'

const courses = ref<Course[]>([])
const showAll = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const visibleCourses = computed(() => {
  if (showAll.value) return courses.value
  return courses.value.slice(0, 6)
})

const form = reactive<Omit<Course, 'id'>>({
  course_code: '',
  course_name: '',
  term: '2025-2026-1',
  department: '',
  major: '',
  credit: 0,
  description: '',
})

function resetForm() {
  form.course_code = ''
  form.course_name = ''
  form.term = '2025-2026-1'
  form.department = ''
  form.major = ''
  form.credit = 0
  form.description = ''
}

async function load() {
  courses.value = await courseApi.list()
}

function openCreate() {
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Course) {
  editingId.value = row.id
  Object.assign(form, row)
  dialogVisible.value = true
}

async function save() {
  if (!form.course_code || !form.course_name || !form.term) {
    ElMessage.warning('请填写所有必填信息。')
    return
  }
  if (editingId.value) {
    await courseApi.update(editingId.value, form)
    ElMessage.success('课程信息已更新。')
  } else {
    await courseApi.create(form)
    ElMessage.success('课程已创建。')
  }

  dialogVisible.value = false
  await load()
}

async function remove(id: number) {
  await ElMessageBox.confirm('确定要永久删除该课程吗？', '确认删除', { 
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
  await courseApi.remove(id)
  ElMessage.success('课程已删除。')
  await load()
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
</style>
