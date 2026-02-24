import client from './client'

export interface Student {
  id: number
  student_no: string
  name: string
  class_name: string
  major: string
  grade_year: string
}

export interface Course {
  id: number
  course_code: string
  course_name: string
  term: string
  department: string
  major: string
  credit: number
  description: string
}

export interface Exam {
  id: number
  course_id: number
  course_name: string
  exam_type: string
  name: string
  date: string
  total_score: number
}

export interface Question {
  id: number
  exam_id: number
  qno: string
  qtype: string
  score: number
  section: string
  knowledge_point: string
  co_code: string
}

// 学生API
export const studentApi = {
  getList: (params: { skip?: number; limit?: number }) =>
    client.get('/analysis/students', { params }),
  create: (data: Omit<Student, 'id'>) =>
    client.post('/analysis/students', data),
  update: (id: number, data: Partial<Student>) =>
    client.put(`/analysis/students/${id}`, data),
  delete: (id: number) =>
    client.delete(`/analysis/students/${id}`)
}

// 课程API
export const courseApi = {
  getList: () =>
    client.get('/analysis/courses'),
  create: (data: Omit<Course, 'id'>) =>
    client.post('/analysis/courses', data),
  update: (id: number, data: Partial<Course>) =>
    client.put(`/analysis/courses/${id}`, data),
  delete: (id: number) =>
    client.delete(`/analysis/courses/${id}`)
}

// 考试API
export const examApi = {
  getList: () =>
    client.get('/analysis/exams'),
  create: (data: Omit<Exam, 'id'>) =>
    client.post('/analysis/exams', data),
  update: (id: number, data: Partial<Exam>) =>
    client.put(`/analysis/exams/${id}`, data),
  delete: (id: number) =>
    client.delete(`/analysis/exams/${id}`)
}

// 题目API
export const questionApi = {
  getList: (params: { exam_id: number }) =>
    client.get('/analysis/questions', { params }),
  create: (data: Omit<Question, 'id'>) =>
    client.post('/analysis/questions', data),
  update: (id: number, data: Partial<Question>) =>
    client.put(`/analysis/questions/${id}`, data),
  delete: (id: number) =>
    client.delete(`/analysis/questions/${id}`)
}

// 文件上传API
export const uploadApi = {
  uploadCSV: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/analysis/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/analysis/upload-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}