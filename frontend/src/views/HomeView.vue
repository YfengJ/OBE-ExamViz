<template>
  <section class="page-grid">
    <div class="dashboard-header">
      <article class="card panel hero">
        <div class="hero-content">
          <h2>欢迎访问 OBE 教学分析系统</h2>
          <p>从成绩录入、达成度评估到自动化预警的端到端数据可视化赋能平台。</p>
          <div class="hero-tags">
            <span class="premium-tag tag-primary"><i class="tag-dot"></i> 数据可视化</span>
            <span class="premium-tag tag-success"><i class="tag-dot"></i> 目标达成度</span>
            <span class="premium-tag tag-warning"><i class="tag-dot"></i> AI智能辅导</span>
          </div>
        </div>
        <div class="hero-decoration">
          <!-- Abstract decoration matching brand -->
          <div class="deco-circle circle-1"></div>
          <div class="deco-circle circle-2"></div>
        </div>
      </article>
    </div>

    <div class="kpi-grid">
      <div class="kpi-wrapper">
        <article class="kpi">
          <p>学生总数</p>
          <h2>{{ kpi.students }}</h2>
          <div class="kpi-trend positive">较上学期 +12%</div>
        </article>
      </div>
      <div class="kpi-wrapper">
        <article class="kpi">
          <p>开设课程</p>
          <h2>{{ kpi.courses }}</h2>
          <div class="kpi-trend neutral">运行平稳</div>
        </article>
      </div>
      <div class="kpi-wrapper">
        <article class="kpi">
          <p>分析考试场次</p>
          <h2>{{ kpi.exams }}</h2>
          <div class="kpi-trend positive">本周新增 3 场</div>
        </article>
      </div>
      <div class="kpi-wrapper">
        <article class="kpi alert-kpi">
          <p>待处理预警</p>
          <h2 :class="{'text-danger': kpi.warnings > 0}">{{ kpi.warnings }}</h2>
          <div class="kpi-trend negative" v-if="kpi.warnings > 0">需立刻处理</div>
          <div class="kpi-trend positive" v-else>全部正常</div>
        </article>
      </div>
    </div>

    <div class="content-section">
      <article class="card panel path-guide">
        <div class="panel-header">
          <h3>快速上手指南</h3>
        </div>
        <div class="steps-container">
          <div class="step-card">
            <div class="step-num">01</div>
            <h4>导入学生名单</h4>
            <p>前往 <strong>学生管理</strong>，导入基础的 `sample_data/students.csv` 数据配置您的学生库。</p>
          </div>
          <div class="step-card">
            <div class="step-num">02</div>
            <h4>导入考试成绩</h4>
            <p>访问 <strong>考试管理</strong>，创建试题结构、导入考核明细及对应学生的期末分数。</p>
          </div>
          <div class="step-card">
            <div class="step-num">03</div>
            <h4>查看分析报告</h4>
            <p>打开 <strong>分析中心</strong>，一键查阅班级分数结构分布图及 OBE 毕业要求达成度数据。</p>
          </div>
          <div class="step-card">
            <div class="step-num">04</div>
            <h4>处理异常预警</h4>
            <p>使用 <strong>预警中心</strong> 提供的高危自动扫描功能，并利用 DeepSeek 分析获取干预建议。</p>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { courseApi, examApi, studentApi, warningApi } from '../api/modules/analysis'

const kpi = reactive({
  students: 0,
  courses: 0,
  exams: 0,
  warnings: 0,
})

onMounted(async () => {
  const [students, courses, exams, warnings] = await Promise.all([
    studentApi.list({ limit: 1000 }),
    courseApi.list(),
    examApi.list(),
    warningApi.list(),
  ])
  kpi.students = students.length
  kpi.courses = courses.length
  kpi.exams = exams.length
  kpi.warnings = warnings.length
})
</script>

<style scoped>
/* Hero Section */
.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3rem 4rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: var(--brand-gradient);
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 600px;
}

.hero h2 {
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 1rem 0;
  background: linear-gradient(135deg, var(--ink-title) 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero p {
  font-size: 1.1rem;
  color: var(--ink-muted);
  line-height: 1.6;
  margin: 0 0 2rem 0;
}

/* Premium Custom Tags */
.hero-tags {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.premium-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  font-family: var(--font-body);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.tag-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
}

.tag-primary {
  background: #eff6ff;
  color: var(--brand-primary);
}
.tag-primary .tag-dot { background: var(--brand-primary); box-shadow: 0 0 8px var(--brand-primary); }

.tag-success {
  background: #ecfdf5;
  color: var(--brand-accent);
}
.tag-success .tag-dot { background: var(--brand-accent); box-shadow: 0 0 8px var(--brand-accent); }

.tag-warning {
  background: #fffbeb;
  color: var(--status-warning);
}
.tag-warning .tag-dot { background: var(--status-warning); box-shadow: 0 0 8px var(--status-warning); }


/* Hero Decorations */
.hero-decoration {
  position: absolute;
  right: 0;
  top: 0;
  width: 400px;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  z-index: 0;
  opacity: 0.5;
}

.circle-1 {
  width: 300px; height: 300px;
  background: rgba(37, 99, 235, 0.15);
  top: -100px; right: -50px;
}

.circle-2 {
  width: 250px; height: 250px;
  background: rgba(16, 185, 129, 0.1);
  bottom: -100px; right: 150px;
}

/* Enhancing KPI Cards visually via nesting wrapper for glow effects */
.kpi-wrapper {
  position: relative;
  transition: var(--trans-smooth);
}

.kpi-wrapper:hover {
  transform: translateY(-4px);
}

.kpi-wrapper::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px -15px rgba(37, 99, 235, 0.15);
  opacity: 0;
  transition: var(--trans-smooth);
  z-index: 0;
}

.kpi-wrapper:hover::after {
  opacity: 1;
}

.kpi-trend {
  margin-top: 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  display: inline-table;
}

.positive { background: #ecfdf5; color: var(--status-good); }
.negative { background: #fef2f2; color: var(--status-danger); }
.neutral { background: #f1f5f9; color: var(--ink-muted); }

.alert-kpi .text-danger {
  background: linear-gradient(135deg, #ef4444, #f97316);
  -webkit-background-clip: text;
  background-clip: text;
}


/* Path Guide (Steps) */
.steps-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.step-card {
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: var(--trans-fast);
}

.step-card:hover {
  background: white;
  border-color: var(--border-subtle);
  box-shadow: var(--shadow-sm);
}

.step-num {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: rgba(37, 99, 235, 0.1);
  margin-bottom: 0.5rem;
  line-height: 1;
}

.step-card h4 {
  font-size: 1.1rem;
  margin: 0 0 0.5rem 0;
}

.step-card p {
  font-size: 0.9rem;
  color: var(--ink-muted);
  line-height: 1.5;
  margin: 0;
}

@media (max-width: 980px) {
  .hero {
    padding: 2rem;
  }
}
@media (max-width: 640px) {
  .hero h2 {
    font-size: 2rem;
  }
  .hero-decoration {
    display: none;
  }
}
</style>
