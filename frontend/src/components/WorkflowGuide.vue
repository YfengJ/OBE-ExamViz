<template>
  <article class="card workflow-card">
    <div class="workflow-header">
      <div>
        <p class="workflow-kicker">分析流程</p>
        <h3>从成绩到报告，一步步完成</h3>
        <p class="workflow-text">
          先确认课程，再导入成绩、完成计算并核对报告，数据来源会更清楚。
        </p>
      </div>
      <div class="workflow-badge">第 {{ activeStep }} 步</div>
    </div>

    <div class="workflow-grid">
      <article
        v-for="item in items"
        :key="item.step"
        class="workflow-item"
        :class="{ active: item.step === activeStep }"
      >
        <span class="workflow-index">0{{ item.step }}</span>
        <h4>{{ item.title }}</h4>
        <p>{{ item.description }}</p>
      </article>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  activeStep: number
}>()

const items = [
  { step: 1, title: '创建或选择已有课程', description: '先确认课程参数；没有课程时可手动新建或从教学大纲导入。' },
  { step: 2, title: '导入成绩', description: '上传成绩工作簿，读取学生成绩、题型和课程目标。' },
  { step: 3, title: '完成计算', description: '查看成绩分布、题型表现和课程目标达成情况。' },
  { step: 4, title: '生成报告', description: '生成报告正文与改进建议，核对后导出文档。' },
]
</script>

<style scoped>
.workflow-card {
  padding: 1.5rem;
  background:
    radial-gradient(circle at right top, rgba(14, 165, 233, 0.12), transparent 30%),
    radial-gradient(circle at left bottom, rgba(16, 185, 129, 0.12), transparent 28%),
    rgba(255, 255, 255, 0.92);
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.workflow-kicker {
  margin: 0 0 0.45rem;
  color: var(--brand-primary);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
}

.workflow-text {
  margin: 0.65rem 0 0;
  color: var(--ink-muted);
}

.workflow-badge {
  white-space: nowrap;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(37, 99, 235, 0.14);
  color: var(--brand-primary);
  font-weight: 700;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.9rem;
}

.workflow-item {
  padding: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.78);
}

.workflow-item.active {
  border-color: rgba(37, 99, 235, 0.22);
  box-shadow: 0 14px 30px -22px rgba(37, 99, 235, 0.65);
}

.workflow-index {
  display: inline-grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: var(--brand-gradient);
  color: #fff;
  font-family: var(--font-display);
  font-weight: 700;
}

.workflow-item h4 {
  margin: 0.8rem 0 0;
}

.workflow-item p {
  margin: 0.5rem 0 0;
  color: var(--ink-muted);
  line-height: 1.7;
}

@media (max-width: 720px) {
  .workflow-header {
    flex-direction: column;
  }
}
</style>
