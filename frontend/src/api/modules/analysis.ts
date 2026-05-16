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
  owner: string | null
  description: string | null
}

export interface CourseFromSyllabusResult {
  course: Course
  outcomes: CourseOutcomeRow[]
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
  qgroup_name: string | null
  sub_qno: string | null
  score: number
  section: string | null
  knowledge_point: string | null
  co_code: string | null
  indicator_code: string | null
  co_weight: number | null
  expected_threshold: number | null
}

export interface ImportResult {
  total: number
  inserted: number
  updated: number
  skipped: number
  errors_preview: string[]
}

export interface AnalysisRunInput {
  course_id: number
  exam_id: number
  class_name: string
  academic_year: string
  term_label: string
  teacher_name?: string | null
  department?: string | null
  major?: string | null
  exam_date?: string | null
  student_count_expected?: number | null
  student_count_actual?: number | null
  outcome_threshold?: number
  usual_weight?: number
  midterm_weight?: number
  final_weight?: number
}

export interface AnalysisRun {
  id: number
  course_id: number
  exam_id: number
  class_name: string
  academic_year: string
  term_label: string
  teacher_name: string | null
  department: string | null
  major: string | null
  exam_date: string | null
  student_count_expected: number
  student_count_actual: number
  outcome_threshold: number
  usual_weight: number
  midterm_weight: number
  final_weight: number
  status: string
  created_at: string
  updated_at: string
}

export interface AnalysisRunOverview {
  run: AnalysisRun
  course_name: string
  exam_name: string
  progress: {
    has_students: boolean
    has_final_scores: boolean
    has_questions: boolean
    has_component_scores: boolean
  }
}

export interface SegmentRow {
  label: string
  count: number
  rate: number
}

export interface QuestionGroupRow {
  qgroup_name: string
  full_score: number
  avg_score: number
  achievement: number
}

export interface QuestionItem {
  question_id: number
  qno: string
  qtype: string
  qgroup_name: string
  full_score: number
  avg_score: number
  difficulty: number
  discrimination: number
  pass_rate: number
}

export interface ComponentSummaryRow {
  component: string
  weight: number
  average_score: number
}

export interface CourseOutcomeRow {
  co_code: string
  co_name: string
  indicator?: string
  description?: string
  full_score: number
  avg_score: number
  achievement: number
  threshold: number
  weight: number
  result: number
  supporting_groups?: string[]
}

export interface StudentOutcomeRow {
  student_id: number
  student_no: string
  student_name: string
  co_code: string
  co_score: number
  full_score: number
  achievement: number
  threshold: number
  is_attained: boolean
}

export interface WarningPreview {
  student_no: string
  student_name: string
  final_score: number
  course_total_score: number
  level: 'warning' | 'critical'
  reasons: string[]
}

export interface RunNarrative {
  score_summary: string
  support_analysis: string
  attainment_analysis: string
  improvement_actions: string
}

export type AiSuggestionTemplate = 'per_outcome' | 'free'

export interface NarrativePayload {
  run: AnalysisRun
  narrative: RunNarrative | null
  ai_enabled: boolean
  cached: boolean
}

export interface PaperSummaryPayload {
  run: AnalysisRun
  score_stats: DashboardPayload['score_stats']
  difficulty_label: string
  warnings: WarningPreview[]
  narrative: RunNarrative | null
  ai_enabled: boolean
  cached: boolean
  suggestion_template?: AiSuggestionTemplate
}

export type SourceMethod = 'direct_read' | 'computed' | 'ai_generated' | 'rendered_chart'

export interface InputRequirement {
  name: string
  required: boolean
  source: string
  fields: string[]
  used_for: string[]
  current_status?: 'ready' | 'pending'
}

export interface DataSourceItem {
  title: string
  source_method: SourceMethod
  source_label: string
  source: string
  fields: string[]
  evidence?: string
}

export interface ReportSectionLineage {
  section_key: string
  title: string
  source_method: SourceMethod
  source_label: string
  description: string
}

export interface CourseObjectiveLineage {
  co_code: string
  co_name: string
  full_score: number
  avg_score: number
  achievement: number
  threshold: number
  supporting_groups: string[]
  support_source: 'question_mapping'
  source_method: 'computed'
  source_label: string
  source_detail: string
}

export interface DataLineagePayload {
  run: AnalysisRun
  meta: Record<string, string | number>
  input_requirements: InputRequirement[]
  data_sources: DataSourceItem[]
  report_sections: ReportSectionLineage[]
  course_objectives: CourseObjectiveLineage[]
  transfer_checklist: string[]
}

export interface TeacherWorkbookPreview {
  input_mode: 'teacher_workbook'
  source_filename: string
  recognized_sheets: string[]
  meta: {
    academic_year: string
    department: string
    course_name: string
    teacher_name: string
    class_name: string
    student_count_expected: number
    student_count_actual: number
    exam_date: string
  }
  score_stats: {
    total_students: number
    average_score: number
    max_score: number
    min_score: number
    pass_rate: number
  }
  difficulty_label: string
  question_group_count: number
  question_item_count: number
  course_outcome_count: number
  warning_count: number
  ai_enabled: boolean
  narrative_engine: 'deepseek' | 'rule_based'
  supported_outputs: { key: string; label: string; description: string }[]
  input_requirements: InputRequirement[]
  data_sources: DataSourceItem[]
  pipeline: string[]
}

export interface TeacherWorkbookTaskResult {
  preview: TeacherWorkbookPreview
  run_overview: AnalysisRunOverview
  template_binding: {
    input_template: string
    output_template: string
  }
}

export interface DashboardPayload {
  run: AnalysisRun
  meta: Record<string, string | number>
  score_stats: {
    total_students: number
    average_score: number
    max_score: number
    min_score: number
    pass_rate: number
  }
  score_segments: SegmentRow[]
  difficulty_label: string
  question_groups: QuestionGroupRow[]
  question_items: QuestionItem[]
  component_summary: ComponentSummaryRow[]
  course_outcomes: CourseOutcomeRow[]
  course_outcome_chart: { co_code: string; threshold: number; achievement: number }[]
  student_outcomes: StudentOutcomeRow[]
  warnings: WarningPreview[]
  narrative_preview: RunNarrative
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
  createFromSyllabus: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return unwrap<CourseFromSyllabusResult>(
      http.post('/analysis/courses/from-syllabus', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    )
  },
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

export const analysisRunApi = {
  list: () => unwrap<AnalysisRunOverview[]>(http.get('/analysis-runs')),
  create: (payload: AnalysisRunInput) => unwrap<AnalysisRunOverview>(http.post('/analysis-runs', payload)),
  dashboard: (runId: number) => unwrap<DashboardPayload>(http.get(`/analysis-runs/${runId}/dashboard`)),
  dataLineage: (runId: number) =>
    unwrap<DataLineagePayload>(http.get(`/analysis-runs/${runId}/data-lineage`)),
  courseOutcomes: (runId: number) =>
    unwrap<{ run: AnalysisRun; summary: CourseOutcomeRow[]; students: StudentOutcomeRow[]; chart: { co_code: string; threshold: number; achievement: number }[] }>(
      http.get(`/analysis-runs/${runId}/course-outcomes`)
    ),
  paperSummary: (runId: number, options?: { template?: AiSuggestionTemplate; force?: boolean }) =>
    unwrap<PaperSummaryPayload>(
      http.get(`/analysis-runs/${runId}/paper-summary`, {
        params: {
          template: options?.template,
          force: options?.force,
        },
        timeout: 60000,
      })
    ),
  paperSummaryCache: (runId: number) =>
    unwrap<PaperSummaryPayload>(http.get(`/analysis-runs/${runId}/paper-summary/cache`)),
  exportExcel: async (runId: number) => {
    const response = await http.get(`/analysis-runs/${runId}/export/excel`, { responseType: 'blob' })
    return response as Blob
  },
  exportDocx: async (runId: number) => {
    const response = await http.get(`/analysis-runs/${runId}/export/docx`, { responseType: 'blob', timeout: 60000 })
    return response as Blob
  },
  narrative: (runId: number) =>
    unwrap<NarrativePayload>(http.get(`/analysis-runs/${runId}/export/narrative`, { timeout: 60000 })),
  narrativeCache: (runId: number) =>
    unwrap<NarrativePayload>(http.get(`/analysis-runs/${runId}/export/narrative/cache`)),
}

async function uploadWithRun(url: string, file: File, runId?: number, extra?: Record<string, string | number>) {
  const formData = new FormData()
  formData.append('file', file)
  if (runId) formData.append('run_id', String(runId))
  Object.entries(extra || {}).forEach(([key, value]) => formData.append(key, String(value)))
  return unwrap<ImportResult>(
    http.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  )
}

export const importApi = {
  students: async (file: File) => uploadWithRun('/import/students', file),
  usualScores: async (file: File, runId?: number) => uploadWithRun('/import/usual-scores', file, runId),
  midtermScores: async (file: File, runId?: number) => uploadWithRun('/import/midterm-scores', file, runId),
  finalScores: async (file: File, runId?: number) => uploadWithRun('/import/final-scores', file, runId),
  paperStructure: async (file: File, runId?: number) => uploadWithRun('/import/paper-structure', file, runId),
  questionScores: async (file: File, runId?: number) => uploadWithRun('/import/question-scores', file, runId),
  examScores: async (file: File) => uploadWithRun('/analysis/import/exam-scores', file),
  questions: async (file: File) => uploadWithRun('/analysis/import/questions', file),
  teacherWorkbookPreview: async (file: File, examDate?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (examDate?.trim()) {
      formData.append('exam_date', examDate.trim())
    }
    return unwrap<TeacherWorkbookPreview>(
      http.post('/import/teacher-workbook-preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    )
  },
  teacherWorkbookReport: async (file: File, examDate?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (examDate?.trim()) {
      formData.append('exam_date', examDate.trim())
    }
    const response = await http.post('/import/teacher-workbook-report', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'blob',
      timeout: 60000,
    })
    return response as Blob
  },
  teacherWorkbookTask: async (file: File, examDate?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (examDate?.trim()) {
      formData.append('exam_date', examDate.trim())
    }
    return unwrap<TeacherWorkbookTaskResult>(
      http.post('/import/teacher-workbook-task', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    )
  },
}
