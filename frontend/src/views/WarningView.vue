<template>
  <section class="page-grid">
    <article class="card panel">
      <div class="panel-header" style="margin-bottom: 1.5rem;">
        <div class="header-titles">
          <h3>预警中心</h3>
          <p class="subtitle">AI驱动的学生学业预报与自动干预平台</p>
        </div>
        <div class="action-bar gap">
          <el-select v-model="courseId" class="premium-select" style="width: 220px" placeholder="选择课程...">
            <el-option v-for="course in courses" :key="course.id" :label="course.course_name" :value="course.id" />
          </el-select>
          <el-select v-model="level" class="premium-select" style="width: 140px" clearable placeholder="预警级别">
            <el-option label="一般" value="warning" />
            <el-option label="严重" value="critical" />
          </el-select>
          <el-select v-model="status" class="premium-select" style="width: 150px" clearable placeholder="状态筛选">
            <el-option label="待处理" value="pending" />
            <el-option label="已复核" value="reviewed" />
            <el-option label="已解决" value="resolved" />
          </el-select>
          
          <el-button plain class="action-btn" @click="loadWarnings">
             <el-icon><Refresh /></el-icon>
          </el-button>

          <el-divider direction="vertical" style="height: 24px; margin: 0 4px;" />

          <el-button type="primary" class="primary-action-btn" @click="generateWarnings">
             生成预警
          </el-button>
          <el-button plain type="success" class="action-btn" @click="batchAi">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right:6px">
               <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            批量AI分析
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="warnings" class="premium-table" row-key="id" @selection-change="onSelectionChange">
          <el-table-column type="selection" width="50" align="center" />
          
          <el-table-column prop="student_no" label="学号" width="130">
            <template #default="{ row }">
              <span class="mono-id fw-bold">{{ row.student_no }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="class_name" label="班级" width="140" />
          
          <el-table-column prop="course_name" label="课程" min-width="180">
             <template #default="{ row }">
               <span class="fw-bold">{{ row.course_name }}</span>
             </template>
          </el-table-column>
          
          <el-table-column prop="level" label="级别" width="110" align="center">
            <template #default="{ row }">
              <span class="urgency-badge" :class="row.level === 'critical' ? 'critical' : 'warning'">
                <span class="dot"></span>
                {{ row.level === 'critical' ? '严重' : '一般' }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="statusTag(row.status)" effect="light" class="type-tag round-tag">
                {{ statusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="预警原因" min-width="240" show-overflow-tooltip>
             <template #default="{ row }">
               <div class="reasons-list">
                 <span v-for="(reason, idx) in row.reasons" :key="idx" class="reason-chip">
                   {{ reason }}
                 </span>
               </div>
             </template>
          </el-table-column>

          <el-table-column label="AI智能说明" min-width="280">
            <template #default="{ row }">
               <div class="ai-summary" :class="{'empty': !row.ai_summary}">
                 <svg v-if="row.ai_summary" width="14" height="14" viewBox="0 0 24 24" fill="none" class="ai-icon">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                 </svg>
                 {{ row.ai_summary || '-- 未生成 --' }}
               </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="230" align="center" fixed="right">
            <template #default="{ row }">
              <div class="row-actions always-visible">
                <el-button link type="primary" @click="genAi(row.id)">诊断分析</el-button>
                <el-divider direction="vertical" />
                <el-dropdown @command="(cmd) => updateStatus(row.id, cmd)">
                  <el-button link type="primary">
                     更新状态 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu class="premium-dropdown">
                      <el-dropdown-item command="pending">标记为待处理</el-dropdown-item>
                      <el-dropdown-item command="reviewed">标记为已复核</el-dropdown-item>
                      <el-dropdown-item command="resolved" class="text-success">标记为已解决</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, ArrowDown } from '@element-plus/icons-vue'

import { courseApi, type Course, warningApi, type WarningItem } from '../api/modules/analysis'

const courses = ref<Course[]>([])
const warnings = ref<WarningItem[]>([])
const selectedIds = ref<number[]>([])
const courseId = ref<number>(1)
const level = ref<string>('')
const status = ref<string>('')

async function loadBase() {
  courses.value = await courseApi.list()
  courseId.value = courses.value[0]?.id || 1
}

async function loadWarnings() {
  warnings.value = await warningApi.list(courseId.value || undefined, level.value || undefined, status.value || undefined)
}

async function generateWarnings() {
  if (!courseId.value) {
    ElMessage.warning('请先选择目标课程。')
    return
  }
  warnings.value = await warningApi.generate(courseId.value, '2025-2026-1')
  ElMessage.success('已自动扫描关联记录，并标记异常成绩。')
}

async function genAi(id: number) {
  await warningApi.aiSummary(id)
  await loadWarnings()
  ElMessage.success('AI干预诊断详情已生成。')
}

async function batchAi() {
  if (!selectedIds.value.length) {
    ElMessage.warning('请至少选择一条预警记录。')
    return
  }
  const res = await warningApi.aiSummaryBatch(selectedIds.value)
  await loadWarnings()
  ElMessage.success(`批量AI诊断生成完毕，共作用于 ${res.updated} 条记录。`)
}

async function updateStatus(id: number, value: string) {
  await warningApi.updateStatus(id, value)
  await loadWarnings()
  ElMessage.success('预警状态已成功更新。')
}

function onSelectionChange(rows: WarningItem[]) {
  selectedIds.value = rows.map((item) => item.id)
}

function statusText(value: string) {
  if (value === 'reviewed') return '已复核'
  if (value === 'resolved') return '已解决'
  return '待处理'
}

function statusTag(value: string) {
  if (value === 'reviewed') return 'warning'
  if (value === 'resolved') return 'success'
  return 'info'
}

onMounted(async () => {
  await loadBase()
  await loadWarnings()
})
</script>

<style scoped>
.panel-header {
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

.primary-action-btn {
  padding: 0 1.25rem;
}

.action-btn {
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  padding: 8px 16px;
}

.premium-select {
  --el-border-radius-base: var(--radius-sm);
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

.type-tag {
  border: none;
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.05em;
}

.round-tag {
  border-radius: 99px;
  padding: 0 12px;
}

.urgency-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}
.urgency-badge .dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(255,255,255, 0.5);
}
.urgency-badge.warning {
  background: #fffbeb;
  color: #d97706;
}
.urgency-badge.warning .dot {
  background: #f59e0b;
}
.urgency-badge.critical {
  background: #fef2f2;
  color: #dc2626;
}
.urgency-badge.critical .dot {
  background: #ef4444;
  animation: pulse 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.reasons-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.reason-chip {
  font-size: 0.8rem;
  background: rgba(15, 23, 42, 0.04);
  color: var(--ink-title);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.ai-summary {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.85rem;
  line-height: 1.4;
  color: var(--ink-body);
  background: linear-gradient(135deg, rgba(37,99,235,0.03), transparent);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 2px solid var(--brand-primary);
}
.ai-summary.empty {
  background: transparent;
  border-left-color: var(--border-subtle);
  color: var(--ink-muted);
  font-style: italic;
  justify-content: center;
  align-items: center;
}
.ai-icon {
  color: var(--brand-primary);
  flex-shrink: 0;
  margin-top: 2px;
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
  opacity: 1;
}

.premium-table:deep(.el-table__row:hover) .row-actions {
  opacity: 1;
}

.premium-dropdown .text-success {
  color: var(--status-good);
}
</style>
