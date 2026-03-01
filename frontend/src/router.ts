import { createRouter, createWebHistory } from 'vue-router'

import AnalysisView from './views/AnalysisView.vue'
import CourseView from './views/CourseView.vue'
import ExamView from './views/ExamView.vue'
import HomeView from './views/HomeView.vue'
import StudentView from './views/StudentView.vue'
import WarningView from './views/WarningView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/students', name: 'students', component: StudentView },
    { path: '/courses', name: 'courses', component: CourseView },
    { path: '/exams', name: 'exams', component: ExamView },
    { path: '/analysis', name: 'analysis', component: AnalysisView },
    { path: '/warnings', name: 'warnings', component: WarningView },
  ],
})

export default router
