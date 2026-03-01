import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    selectedCourseId: 1,
    selectedExamId: 1,
    selectedClassName: '',
  }),
})
