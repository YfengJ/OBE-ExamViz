import http, { unwrap } from '../http'

export interface Student {
  id: number
  student_no: string
  name: string | null
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
  description: string | null
}

export interface Exam {
  id: number
  course_id: number
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
  section: string | null
  knowledge_point: string | null
  co_code: string | null
  indicator_code: string | null
}

export interface ScoreStats {
  total_students: number
  average_score: number
  max_score: number
  min_score: number
  pass_rate: number
  score_segments: Record<string, number>
}

export interface QuestionAnalysisItem {
  question_id: number
  qno: string
  qtype: string
  full_score: number
  avg_score: number
  difficulty: number
  discrimination: number
  pass_rate: number
}

export interface ObeAchievement {
  co_code: string
  co_name: string
  achievement: number
  threshold: number
}

export interface WarningItem {
  id: number
  student_id: number
  student_no: string
  class_name: string
  course_id: number
  course_name: string
  term: string
  level: 'warning' | 'critical'
  reasons: string[]
  ai_summary: string | null
  created_at: string
}

export interface ScoreTrendPoint {
  exam_id: number
  exam_name: string
  exam_date: string
  avg_score: number
}

export interface ImportResult {
  total: number
  inserted: number
  updated: number
  skipped: number
  errors_preview: string[]
}

export const studentApi = {
  list: (params?: { skip?: number; limit?: number; class_name?: string }) =>
    unwrap<Student[]>(http.get('/analysis/students', { params })),
  create: (payload: Omit<Student, 'id'>) => unwrap<Student>(http.post('/analysis/students', payload)),
  update: (id: number, payload: Partial<Student>) => unwrap<Student>(http.put(`/analysis/students/${id}`, payload)),
  remove: (id: number) => unwrap<boolean>(http.delete(`/analysis/students/${id}`)),
}

export const courseApi = {
  list: () => unwrap<Course[]>(http.get('/analysis/courses')),
  create: (payload: Omit<Course, 'id'>) => unwrap<Course>(http.post('/analysis/courses', payload)),
  update: (id: number, payload: Partial<Course>) => unwrap<Course>(http.put(`/analysis/courses/${id}`, payload)),
  remove: (id: number) => unwrap<boolean>(http.delete(`/analysis/courses/${id}`)),
}

export const examApi = {
  list: () => unwrap<Exam[]>(http.get('/analysis/exams')),
  create: (payload: Omit<Exam, 'id'>) => unwrap<Exam>(http.post('/analysis/exams', payload)),
  update: (id: number, payload: Partial<Exam>) => unwrap<Exam>(http.put(`/analysis/exams/${id}`, payload)),
  remove: (id: number) => unwrap<boolean>(http.delete(`/analysis/exams/${id}`)),
}

export const questionApi = {
  list: (exam_id: number) => unwrap<Question[]>(http.get('/analysis/questions', { params: { exam_id } })),
  create: (payload: Omit<Question, 'id'>) => unwrap<Question>(http.post('/analysis/questions', payload)),
  update: (id: number, payload: Partial<Question>) => unwrap<Question>(http.put(`/analysis/questions/${id}`, payload)),
  remove: (id: number) => unwrap<boolean>(http.delete(`/analysis/questions/${id}`)),
}

export const analysisApi = {
  scoreStats: (course_id: number, class_name?: string) =>
    unwrap<ScoreStats>(http.get('/analysis/score-statistics', { params: { course_id, class_name } })),
  questionAnalysis: (exam_id: number) =>
    unwrap<QuestionAnalysisItem[]>(http.get('/analysis/question-analysis', { params: { exam_id } })),
  obeAchievement: (course_id: number, exam_id?: number) =>
    unwrap<ObeAchievement[]>(http.get('/analysis/obe-achievement', { params: { course_id, exam_id } })),
  scoreTrend: (course_id: number) =>
    unwrap<ScoreTrendPoint[]>(http.get('/analysis/score-trend', { params: { course_id } })),
  exportScoreReport: async (course_id: number, exam_id: number, class_name?: string) => {
    const response = await http.get('/analysis/export-score-report', {
      params: { course_id, exam_id, class_name },
      responseType: 'blob',
    })
    return response as Blob
  },
}

export const warningApi = {
  list: (course_id?: number, level?: string, status?: string) =>
    unwrap<WarningItem[]>(http.get('/analysis/warnings', { params: { course_id, level, status } })),
  generate: (course_id: number, term: string) =>
    unwrap<WarningItem[]>(http.post('/analysis/warnings/generate', { course_id, term })),
  updateStatus: (warning_id: number, status: string) =>
    unwrap<{ id: number; status: string }>(http.patch(`/analysis/warnings/${warning_id}`, null, { params: { status } })),
  aiSummary: (warning_id: number) =>
    unwrap<{ id: number; ai_summary: string }>(http.post(`/analysis/warnings/${warning_id}/ai-summary`)),
  aiSummaryBatch: (warning_ids: number[]) =>
    unwrap<{ updated: number }>(http.post('/analysis/warnings/ai-summary/batch', warning_ids)),
}

export const importApi = {
  students: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return unwrap<ImportResult>(
      http.post('/analysis/import/students', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    )
  },
  examScores: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return unwrap<ImportResult>(
      http.post('/analysis/import/exam-scores', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    )
  },
  questions: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return unwrap<ImportResult>(
      http.post('/analysis/import/questions', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    )
  },
  questionScores: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return unwrap<ImportResult>(
      http.post('/analysis/import/question-scores', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    )
  },
}
