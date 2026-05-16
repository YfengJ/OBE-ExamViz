# 数据库设计

## 1. 设计目标

数据库需要同时满足三类需求：

1. 维护基础主数据：学生、课程、考试、题目
2. 支撑教师导入的过程性成绩、期末总分、逐题得分
3. 支撑老师模板导出的班级分析、课程目标达成度、预警与文字分析

因此，本次重构新增了 `analysis_runs` 表，并扩展了 `questions` 表。

## 2. 核心 ER 关系

```text
Student ─────┐
             ├── StudentExamScore ── Exam ── Course
             ├── StudentComponentScore ── AssessmentComponent ── Course
             └── StudentQuestionScore ── Question ── Exam

Course ── OBEOutcome
Course ── AnalysisRun ── Exam
AnalysisRun 绑定 class_name / term / teacher / threshold / weights
```

## 3. 核心实体说明

### 3.1 students

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `student_no` | String | 学号，唯一 |
| `name` | String, Nullable | 姓名，可为空，默认匿名 |
| `class_name` | String | 班级 |
| `major` | String | 专业 |
| `grade_year` | String | 年级 |

### 3.2 courses

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `course_code` | String | 课程代码 |
| `course_name` | String | 课程名称 |
| `term` | String | 学期 |
| `department` | String | 开课院系 |
| `major` | String | 专业 |
| `credit` | Float | 学分 |
| `description` | Text / String | 课程说明 |

### 3.3 exams

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `course_id` | Integer | 所属课程 |
| `exam_type` | String | `usual / mid / final` |
| `name` | String | 考试名称 |
| `date` | Date | 考试日期 |
| `total_score` | Float | 卷面总分 |

### 3.4 questions

扩展后字段如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `exam_id` | Integer | 所属考试 |
| `qno` | String | 题号 |
| `qtype` | String | 题型 |
| `qgroup_name` | String, Nullable | 题型分组，如单选题、综合题 |
| `sub_qno` | String, Nullable | 小题号，如 `5-1` |
| `score` | Float | 该题满分 |
| `section` | String, Nullable | 所属章节 |
| `knowledge_point` | String, Nullable | 知识点 |
| `co_code` | String, Nullable | 课程目标代码 |
| `indicator_code` | String, Nullable | 指标点 |
| `co_weight` | Float | 题目对课程目标权重 |
| `expected_threshold` | Float | 该题关联课程目标阈值 |

### 3.5 student_exam_scores

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `student_id` | Integer | 学生 |
| `exam_id` | Integer | 考试 |
| `total_score` | Float | 期末总分或某次考试总分 |

### 3.6 assessment_components

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `course_id` | Integer | 课程 |
| `name` | String | 成绩项，如 `usual` / `midterm` |
| `weight` | Float | 权重 |

### 3.7 student_component_scores

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `student_id` | Integer | 学生 |
| `component_id` | Integer | 成绩项 |
| `score` | Float | 得分 |

### 3.8 student_question_scores

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `student_id` | Integer | 学生 |
| `question_id` | Integer | 题目 |
| `score` | Float | 逐题得分 |

### 3.9 obe_outcomes

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `course_id` | Integer | 课程 |
| `co_code` | String | 课程目标代码 |
| `co_name` | String | 课程目标名称 |
| `threshold` | Float | 达成阈值，默认 `0.65` |

### 3.10 analysis_runs

这是本次模板化重构新增的核心表。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `course_id` | Integer | 关联课程 |
| `exam_id` | Integer | 关联考试 |
| `class_name` | String | 班级 |
| `academic_year` | String | 学年 |
| `term_label` | String | 学期标签 |
| `teacher_name` | String, Nullable | 任课教师 |
| `department` | String, Nullable | 院系 |
| `major` | String, Nullable | 专业 |
| `exam_date` | Date, Nullable | 考试日期 |
| `student_count_expected` | Integer | 应考人数 |
| `student_count_actual` | Integer | 实考人数 |
| `outcome_threshold` | Float | 课程目标阈值 |
| `usual_weight` | Float | 平时权重 |
| `midterm_weight` | Float | 期中权重 |
| `final_weight` | Float | 期末权重 |
| `status` | String | `draft / partial / ready` |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### 3.11 warning_rules / warning_results

保留预警规则与预警结果表，用于：

- 规则预警
- AI 说明生成
- 教师后续处理状态记录

## 4. 索引策略

### 4.1 基础索引

- `students.student_no`
- `courses.course_code`
- `analysis_runs.id`

### 4.2 组合索引建议

- `student_exam_scores(student_id, exam_id)`
- `questions(exam_id, qno)`
- `student_question_scores(student_id, question_id)`
- `analysis_runs(course_id, exam_id, class_name)`

### 4.3 查询热点

系统当前最常见的查询路径是：

1. `AnalysisRun -> Exam -> Question`
2. `AnalysisRun.class_name -> Student`
3. `Student + Exam -> StudentExamScore`
4. `Student + Question -> StudentQuestionScore`

因此索引优先围绕“班级 + 考试 + 学生 + 题目”的组合建立。

## 5. 数据一致性

### 5.1 任务快照同步

为了避免首页和导出表中的“应考 / 实考人数”与真实导入数据不一致，系统在以下时机会刷新 `analysis_runs` 快照：

- 列出分析任务时
- 查看单个分析任务时
- 导入平时、期中、期末、试卷结构、逐题得分后

### 5.2 数据匿名化

- `name` 可为空
- AI 分析默认只使用学号与匿名 ID
- `sample_data/` 只保留可公开模拟数据

## 6. SQLite 与 PostgreSQL 兼容

当前开发默认使用 SQLite。
代码层通过 SQLAlchemy 保持对 PostgreSQL 的兼容，切换时只需要修改 `DATABASE_URL`。
当前版本针对 SQLite 增加了轻量级启动补列逻辑，用于保证新增字段在老库上也能运行。
