<template>
  <div id="app">
    <el-container style="height: 100vh">
      <el-header>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="$route.path"
          style="height: 100%; display: flex; align-items: center"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/students">学生管理</el-menu-item>
          <el-menu-item index="/courses">课程管理</el-menu-item>
          <el-menu-item index="/exams">考试管理</el-menu-item>
          <el-menu-item index="/analysis">成绩分析</el-menu-item>
          <el-menu-item index="/warnings">学情预警</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background-color: #409eff;
  color: white;
  padding: 0;
}
</style>