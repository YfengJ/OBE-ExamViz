import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    selectedRunId: 0,
    selectedCourseId: 1,
    selectedExamId: 1,
    selectedClassName: '',
  }),
})
