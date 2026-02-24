<template>
  <div class="home">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>基于OBE的期末试卷分析与成绩可视化系统</span>
        </div>
      </template>
      <div class="card-content">
        <p>欢迎使用本系统！请选择上方的功能模块开始操作。</p>
        <el-descriptions :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="系统版本">v0.1.0</el-descriptions-item>
          <el-descriptions-item label="技术栈">
            <el-tag>Vue 3 + Vite</el-tag>
            <el-tag style="margin-left: 5px">FastAPI</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="功能特性">
            <el-tag type="success">成绩分析</el-tag>
            <el-tag type="success" style="margin-left: 5px">OBE达成度</el-tag>
            <el-tag type="success" style="margin-left: 5px">学情预警</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home {
  padding: 20px;
}

.box-card {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}

.card-content {
  text-align: center;
  line-height: 1.8;
}
</style>