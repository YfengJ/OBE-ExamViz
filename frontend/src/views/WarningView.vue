<template>
  <div class="warning-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学情预警</span>
          <el-button type="primary" @click="handleGenerateWarnings">生成预警</el-button>
          <el-button type="success" @click="handleExportWarnings">导出预警</el-button>
        </div>
      </template>

      <!-- 预警统计 -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="8">
          <el-statistic title="预警总数" :value="warningStats.total" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="一般预警" :value="warningStats.warning">
            <template #suffix>
              <el-tag type="warning" size="small">一般</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="严重预警" :value="warningStats.critical">
            <template #suffix>
              <el-tag type="danger" size="small">严重</el-tag>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="课程">
          <el-select v-model="filterForm.course_id" placeholder="全部" style="width: 180px">
            <el-option label="全部" value="0" />
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.course_name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预警级别">
          <el-select v-model="filterForm.level" placeholder="全部" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="一般预警" value="warning" />
            <el-option label="严重预警" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="filterForm.status" placeholder="全部" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="未处理" value="pending" />
            <el-option label="已处理" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="handleResetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 预警列表 -->
      <el-table :data="warningList" style="width: 100%; margin-top: 20px" border>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="120" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="level" label="预警级别" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.level === 'critical' ? 'danger' : 'warning'">
              {{ scope.row.level === 'critical' ? '严重' : '一般' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="预警原因" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ai_summary" label="AI分析" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="预警时间" width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleViewDetails(scope.row)">详情</el-button>
            <el-button size="small" type="success" @click="handleResolve(scope.row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        style="margin-top: 20px; text-align: center"
        v-model:currentPage="pagination.current"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />

      <!-- 预警详情对话框 -->
      <el-dialog v-model="detailDialogVisible" title="预警详情" width="700px">
        <el-descriptions :column="2" border v-if="currentWarning">
          <el-descriptions-item label="学生">{{ currentWarning.student_name }}({{ currentWarning.student_no }}) }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ currentWarning.class_name }}</el-descriptions-item>
          <el-descriptions-item label="课程">{{ currentWarning.course_name }}</el-descriptions-item>
          <el-descriptions-item label="预警级别">
            <el-tag :type="currentWarning.level === 'critical' ? 'danger' : 'warning'">
              {{ currentWarning.level === 'critical' ? '严重预警' : '一般预警' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警原因" :span="2">
            <el-alert :title="currentWarning.reason" type="warning" :closable="false" />
          </el-descriptions-item>
          <el-descriptions-item label="AI分析" :span="2">
            <el-alert :title="currentWarning.ai_summary || '暂无AI分析'" type="info" :closable="false" />
          </el-descriptions-item>
          <el-descriptions-item label="预警时间">{{ currentWarning.created_at }}</el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="currentWarning.status === 'resolved' ? 'success' : 'warning'">
              {{ currentWarning.status === 'resolved' ? '已处理' : '未处理' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">详细分析</el-divider>

        <el-table :data="warningDetails" style="width: 100%" border>
          <el-table-column prop="indicator" label="预警指标" width="150" />
          <el-table-column prop="value" label="当前值" width="100" />
          <el-table-column prop="threshold" label="预警阈值" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag type="danger" v-if="scope.row.value > scope.row.threshold">超标</el-tag>
              <el-tag type="success" v-else>正常</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <template #footer>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="handleAIGenerate">AI分析</el-button>
          <el-button type="success" v-if="currentWarning && currentWarning.status !== 'resolved'" @click="handleMarkResolved">标记已处理</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Course {
  id: number
  course_name: string
}

interface WarningItem {
  id: number
  student_no: string
  student_name: string
  class_name: string
  course_name: string
  level: 'warning' | 'critical'
  reason: string
  ai_summary: string
  created_at: string
  status: 'pending' | 'resolved'
}

interface WarningDetail {
  indicator: string
  value: number
  threshold: number
}

const courses = ref<Course[]>([])
const warningStats = ref({
  total: 8,
  warning: 5,
  critical: 3
})
const filterForm = ref({
  course_id: '0',
  level: '',
  status: ''
})
const warningList = ref<WarningItem[]>([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})
const detailDialogVisible = ref(false)
const currentWarning = ref<WarningItem | null>(null)
const warningDetails = ref<WarningDetail[]>([])

const fetchCourses = async () => {
  try {
    const response = await axios.get('/api/analysis/courses')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const fetchWarnings = async () => {
  // 模拟数据
  warningList.value = [
    {
      id: 1,
      student_no: '2021001',
      student_name: '张三',
      class_name: '计算机2101',
      course_name: '数据结构',
      level: 'critical',
      reason: '期末成绩低于60分，平时成绩低于50分',
      ai_summary: '该生基础薄弱，建议加强课后辅导',
      created_at: '2025-01-15 10:30:00',
      status: 'pending'
    },
    {
      id: 2,
      student_no: '2021002',
      student_name: '李四',
      class_name: '计算机2101',
      course_name: '数据结构',
      level: 'warning',
      reason: '作业完成率低于70%',
      ai_summary: '学习态度需要改善，建议加强监督',
      created_at: '2025-01-15 10:30:00',
      status: 'pending'
    }
  ]
  pagination.value.total = warningList.value.length
}

const handleFilter = () => {
  ElMessage.info('筛选功能待实现')
  fetchWarnings()
}

const handleResetFilter = () => {
  filterForm.value = {
    course_id: '0',
    level: '',
    status: ''
  }
  fetchWarnings()
}

const handleGenerateWarnings = () => {
  ElMessage.info('预警生成功能待实现')
}

const handleExportWarnings = () => {
  ElMessage.info('导出预警功能待实现')
}

const handleViewDetails = (row: WarningItem) => {
  currentWarning.value = row
  detailDialogVisible.value = true
  // 模拟详细数据
  warningDetails.value = [
    { indicator: '期末成绩', value: 55, threshold: 60 },
    { indicator: '平时成绩', value: 45, threshold: 50 },
    { indicator: '作业完成率', value: 0.65, threshold: 0.7 },
    { indicator: '课堂参与度', value: 0.5, threshold: 0.6 }
  ]
}

const handleResolve = async (row: WarningItem) => {
  try {
    await ElMessageBox.confirm('确认标记该预警为已处理？')
    ElMessage.success('处理成功')
    fetchWarnings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('处理失败')
    }
  }
}

const handleAIGenerate = () => {
  ElMessage.info('AI分析功能待实现')
}

const handleMarkResolved = async () => {
  if (!currentWarning.value) return
  try {
    await ElMessageBox.confirm('确认标记为已处理？')
    ElMessage.success('标记成功')
    detailDialogVisible.value = false
    fetchWarnings()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('标记失败')
    }
  }
}

const handlePageChange = (page: number) => {
  pagination.value.current = page
  fetchWarnings()
}

onMounted(() => {
  fetchCourses()
  fetchWarnings()
})
</script>

<style scoped>
.warning-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>