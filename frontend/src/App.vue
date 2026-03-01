<template>
  <div class="app-shell">
    <header class="topbar-container">
      <div class="topbar">
        <div class="brand">
          <div class="brand-mark">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="brand-text">
            <h1>OBE 教学分析</h1>
            <p>数据可视化平台</p>
          </div>
        </div>
        
        <nav class="menu">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="menu-item"
            :class="{ active: route.path === item.path }"
          >
            {{ item.label }}
            <span v-if="route.path === item.path" class="active-indicator"></span>
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="content-container">
      <div class="content">
        <RouterView v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', label: '总览看板' },
  { path: '/students', label: '学生管理' },
  { path: '/courses', label: '课程管理' },
  { path: '/exams', label: '考试管理' },
  { path: '/analysis', label: '分析中心' },
  { path: '/warnings', label: '预警中心' },
]
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* The Topbar Container handles outer spacing and sticky positioning */
.topbar-container {
  position: sticky;
  top: 0;
  z-index: 50;
  padding: 1rem 1.5rem 0;
  background: linear-gradient(180deg, var(--bg-app) 40%, transparent); /* Gentle fade preventing text clash behind */
}

/* The actual navbar is a floating glass pill */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.75rem 1rem 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-xl);
  box-shadow: 0 4px 24px -6px rgba(15, 23, 42, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  transition: var(--trans-smooth);
}

.topbar:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 8px 32px -8px rgba(15, 23, 42, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.8);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  user-select: none;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-content: center;
  background: var(--brand-gradient);
  box-shadow: var(--shadow-glow);
  transform: rotate(-5deg);
  transition: var(--trans-smooth);
}

.brand:hover .brand-mark {
  transform: rotate(0deg) scale(1.05);
}

.brand-text h1 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--ink-title);
  line-height: 1.2;
}

.brand-text p {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.menu {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(241, 245, 249, 0.7);
  padding: 0.35rem;
  border-radius: 99px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.menu-item {
  position: relative;
  text-decoration: none;
  color: var(--ink-muted);
  padding: 0.5rem 1rem;
  border-radius: 99px;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: var(--font-body);
  transition: var(--trans-fast);
  z-index: 1;
}

.menu-item:hover {
  color: var(--ink-title);
  background: rgba(255, 255, 255, 0.5);
}

.menu-item.active {
  color: var(--brand-primary);
  background: white;
  box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.06);
}

.active-indicator {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 3px;
  border-radius: 3px;
  background: var(--brand-gradient);
  opacity: 0.8;
}

.content-container {
  flex: 1;
  padding: 2rem 1.5rem;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Transition Effects */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 960px) {
  .topbar-container {
    padding: 0.5rem;
  }
  
  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border-radius: var(--radius-lg);
  }
  
  .menu {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    border-radius: var(--radius-sm);
  }
  
  .content-container {
    padding: 1.5rem 0.5rem;
  }
}
</style>
