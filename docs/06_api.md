# API 接口说明

## 1. 基础信息

- Base URL: `http://localhost:8000/api/v1`
- Swagger: `http://localhost:8000/docs`
- 响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 2. 分析任务接口

### 2.1 获取分析任务列表

```http
GET /analysis-runs
```

返回内容包含：

- 任务基础信息 `run`
- 课程名、考试名
- 当前准备状态：
  - `has_students`
  - `has_component_scores`
  - `has_final_scores`
  - `has_questions`

### 2.2 创建分析任务

```http
POST /analysis-runs
Content-Type: application/json
```

请求体示例：

```json
{
  "course_id": 1,
  "exam_id": 1,
  "class_name": "计算机2101",
  "academic_year": "2025-2026",
  "term_label": "2025-2026-1",
  "teacher_name": "张老师",
  "department": "计算机学院",
  "major": "计算机科学与技术",
  "outcome_threshold": 0.65,
  "usual_weight": 0.2,
  "midterm_weight": 0.2,
  "final_weight": 0.6
}
```

### 2.3 获取分析看板数据

```http
GET /analysis-runs/{run_id}/dashboard
```

返回内容包含：

- `score_stats`
- `score_segments`
- `difficulty_label`
- `question_groups`
- `question_items`
- `component_summary`
- `course_outcomes`
- `student_outcomes`
- `warnings`
- `narrative_preview`

### 2.4 获取课程目标分析

```http
GET /analysis-runs/{run_id}/course-outcomes
```

### 2.5 获取试卷分析文字摘要

```http
GET /analysis-runs/{run_id}/paper-summary
```

### 2.6 导出模板化 Excel

```http
GET /analysis-runs/{run_id}/export/excel
```

返回 `xlsx` 文件流。

### 2.7 导出 Word 版试卷分析文档

```http
GET /analysis-runs/{run_id}/export/docx
```

返回 `docx` 文件流。

### 2.8 生成文字分析

```http
GET /analysis-runs/{run_id}/export/narrative
```

返回四段结构化文本：

- `score_summary`
- `support_analysis`
- `attainment_analysis`
- `improvement_actions`

同时返回：

- `ai_enabled`：当前是否已配置 DeepSeek API Key

## 3. 导入接口

导入接口统一采用 `multipart/form-data`。

### 3.1 导入学生名单

```http
POST /import/students
```

文件字段：

- `file`

推荐字段：

- `student_no`
- `name`
- `class_name`
- `major`
- `grade_year`

### 3.1.1 下载导入模板

```http
GET /import/templates/{template_name}
```

支持的模板：

- `teacher_input_template.xlsx`
- `teacher_report_template.docx`

### 3.2 导入平时成绩

```http
POST /import/usual-scores
```

表单字段：

- `file`
- `run_id` 或 `course_id`

兼容列名：

- `student_no`
- `score`
- `学号`
- `平时成绩`

### 3.3 导入期中成绩

```http
POST /import/midterm-scores
```

表单字段：

- `file`
- `run_id` 或 `course_id`

### 3.4 导入期末总分

```http
POST /import/final-scores
```

表单字段：

- `file`
- `run_id` 或 `exam_id` 或 `course_id`

兼容列名：

- `student_no`
- `total_score`
- `学号`
- `期末成绩`
- `总分`

### 3.5 导入试卷结构

```http
POST /import/paper-structure
```

表单字段：

- `file`
- `run_id` 或 `exam_id`

推荐列：

- `qno`
- `qtype`
- `qgroup_name`
- `sub_qno`
- `score`
- `section`
- `knowledge_point`
- `co_code`
- `indicator_code`
- `co_weight`
- `expected_threshold`

### 3.6 导入逐题得分

```http
POST /import/question-scores
```

表单字段：

- `file`
- `run_id`（推荐）

支持三种格式：

格式 A：

- `student_no`
- `question_id`
- `score`

格式 B：

- `student_no`
- `exam_id`
- `qno`
- `score`

格式 C：

- `student_no`
- `qno`
- `score`
- 同时通过表单传入 `run_id` 或 `exam_id`

### 3.7 预览成绩工作簿

```http
POST /import/teacher-workbook-preview
```

表单字段：

- `file`
- `exam_date`（可选）

用于读取成绩文件并返回课程、班级、学生人数、题型、课程目标、输入要求和生成依据。

### 3.8 导入成绩工作簿并创建分析任务

```http
POST /import/teacher-workbook-task
```

表单字段：

- `file`
- `exam_date`（可选）
- `preview_confirmed=true`

后端要求先完成预览确认，再创建或更新课程、考试、题目、学生成绩、逐题得分、课程目标和分析任务。

### 3.9 直接从成绩工作簿导出 Word 报告

```http
POST /import/teacher-workbook-report
```

表单字段：

- `file`
- `exam_date`（可选）

该接口用于兼容“上传工作簿后直接得到 Word 报告”的场景；系统主流程优先使用 `teacher-workbook-preview` 和 `teacher-workbook-task`。

## 4. 基础对象接口

这些接口保留用于维护主数据与补录数据。

### 4.1 学生

- `GET /analysis/students`
- `POST /analysis/students`
- `PUT /analysis/students/{id}`
- `DELETE /analysis/students/{id}`

### 4.2 课程

- `GET /analysis/courses`
- `POST /analysis/courses`
- `PUT /analysis/courses/{id}`
- `DELETE /analysis/courses/{id}`

### 4.3 考试

- `GET /analysis/exams`
- `POST /analysis/exams`
- `PUT /analysis/exams/{id}`
- `DELETE /analysis/exams/{id}`

### 4.4 题目

- `GET /analysis/questions?exam_id=1`
- `POST /analysis/questions`
- `PUT /analysis/questions/{id}`
- `DELETE /analysis/questions/{id}`

题目对象已支持以下扩展字段：

- `qgroup_name`
- `sub_qno`
- `co_weight`
- `expected_threshold`

## 5. 旧分析接口

为兼容现有页面和已有数据流，保留旧接口：

- `GET /analysis/score-statistics`
- `GET /analysis/score-trend`
- `GET /analysis/question-analysis`
- `GET /analysis/obe-achievement`
- `GET /analysis/warnings`
- `POST /analysis/warnings/generate`
- `GET /analysis/export-score-report`

这些接口更适合做单点查询；新的教师工作流优先使用 `analysis-runs` 相关接口。

## 6. 错误响应

### 6.1 参数错误

```json
{
  "detail": "Missing required columns: ['student_no', 'score']"
}
```

### 6.2 资源不存在

```json
{
  "detail": "analysis_run not found: 999"
}
```

## 7. 演示调用示例

### 7.1 获取任务列表

```bash
curl http://localhost:8000/api/v1/analysis-runs
```

### 7.2 创建分析任务

```bash
curl -X POST http://localhost:8000/api/v1/analysis-runs ^
  -H "Content-Type: application/json" ^
  -d "{\"course_id\":1,\"exam_id\":1,\"class_name\":\"计算机2101\",\"academic_year\":\"2025-2026\",\"term_label\":\"2025-2026-1\"}"
```

### 7.3 导入期末成绩

```bash
curl -X POST http://localhost:8000/api/v1/import/final-scores ^
  -F "file=@sample_data/final_scores_template.csv" ^
  -F "run_id=1"
```

### 7.4 导出试卷分析表

```bash
curl http://localhost:8000/api/v1/analysis-runs/1/export/excel -o analysis_run_1.xlsx
```
