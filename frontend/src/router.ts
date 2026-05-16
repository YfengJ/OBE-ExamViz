import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('./views/HomeView.vue') },
    { path: '/students', redirect: '/exams' },
    { path: '/courses', name: 'courses', component: () => import('./views/CourseView.vue') },
    { path: '/exams', name: 'exams', component: () => import('./views/ExamView.vue') },
    { path: '/analysis', name: 'analysis', component: () => import('./views/AnalysisView.vue') },
    { path: '/report-preview', name: 'report-preview', component: () => import('./views/ReportPreviewView.vue') },
    { path: '/warnings', name: 'warnings', component: () => import('./views/WarningView.vue') },
  ],
})

export default router
