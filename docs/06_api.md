# API接口文档

## 1. API概述

### 1.1 基础信息
- **API根地址**：`http://localhost:8000/api/v1`
- **API文档**：`http://localhost:8000/docs` (Swagger UI)
- **API格式**：RESTful JSON
- **认证方式**：JWT Token (待实现)

### 1.2 响应格式
所有API响应遵循统一格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 1.3 错误码
- `200`：成功
- `400`：请求参数错误
- `401`：未授权
- `403`：权限不足
- `404`：资源不存在
- `500`：服务器内部错误

## 2. 学生管理API

### 2.1 获取学生列表
```http
GET /analysis/students
```

**参数**
- `skip`：跳过数量（默认0）
- `limit`：返回数量（默认100，最大1000）
- `class_name`：班级筛选（可选）
- `major`：专业筛选（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "students": [
      {
        "id": 1,
        "student_no": "2021001",
        "name": "张三",
        "class_name": "计算机2101",
        "major": "计算机科学与技术",
        "grade_year": "2021"
      }
    ],
    "total": 30,
    "skip": 0,
    "limit": 100
  }
}
```

### 2.2 创建学生
```http
POST /analysis/students
```

**请求体**
```json
{
  "student_no": "2021001",
  "name": "张三",
  "class_name": "计算机2101",
  "major": "计算机科学与技术",
  "grade_year": "2021"
}
```

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "student_no": "2021001",
    "name": "张三",
    "class_name": "计算机2101",
    "major": "计算机科学与技术",
    "grade_year": "2021"
  }
}
```

### 2.3 更新学生信息
```http
PUT /analysis/students/{student_id}
```

**请求体**
```json
{
  "name": "张三丰",
  "class_name": "计算机2101"
}
```

### 2.4 删除学生
```http
DELETE /analysis/students/{student_id}
```

## 3. 课程管理API

### 3.1 获取课程列表
```http
GET /analysis/courses
```

**参数**
- `term`：学期筛选（可选）
- `major`：专业筛选（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "course_code": "CS101",
      "course_name": "数据结构",
      "term": "2024-2025-1",
      "department": "计算机学院",
      "major": "计算机科学与技术",
      "credit": 3.0,
      "description": "研究数据组织与处理的基本方法"
    }
  ]
}
```

### 3.2 创建课程
```http
POST /analysis/courses
```

**请求体**
```json
{
  "course_code": "CS101",
  "course_name": "数据结构",
  "term": "2024-2025-1",
  "department": "计算机学院",
  "major": "计算机科学与技术",
  "credit": 3.0,
  "description": "研究数据组织与处理的基本方法"
}
```

### 3.3 更新课程信息
```http
PUT /analysis/courses/{course_id}
```

### 3.4 删除课程
```http
DELETE /analysis/courses/{course_id}
```

## 4. 考试管理API

### 4.1 获取考试列表
```http
GET /analysis/exams
```

**参数**
- `course_id`：课程ID筛选（可选）
- `exam_type`：考试类型筛选（usual/mid/final）（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "course_id": 1,
      "course_name": "数据结构",
      "exam_type": "final",
      "name": "数据结构期末考试",
      "date": "2025-01-10",
      "total_score": 100
    }
  ]
}
```

### 4.2 创建考试
```http
POST /analysis/exams
```

**请求体**
```json
{
  "course_id": 1,
  "exam_type": "final",
  "name": "数据结构期末考试",
  "date": "2025-01-10",
  "total_score": 100
}
```

### 4.3 更新考试信息
```http
PUT /analysis/exams/{exam_id}
```

### 4.4 删除考试
```http
DELETE /analysis/exams/{exam_id}
```

## 5. 题目管理API

### 5.1 获取题目列表
```http
GET /analysis/questions
```

**参数**
- `exam_id`：考试ID（必需）
- `qtype`：题型筛选（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "exam_id": 1,
      "qno": "1",
      "qtype": "单选题",
      "score": 10,
      "section": "第1章",
      "knowledge_point": "数据结构基本概念",
      "co_code": "CO1",
      "indicator_code": "IND1"
    }
  ]
}
```

### 5.2 创建题目
```http
POST /analysis/questions
```

**请求体**
```json
{
  "exam_id": 1,
  "qno": "1",
  "qtype": "单选题",
  "score": 10,
  "section": "第1章",
  "knowledge_point": "数据结构基本概念",
  "co_code": "CO1",
  "indicator_code": "IND1"
}
```

### 5.3 更新题目信息
```http
PUT /analysis/questions/{question_id}
```

### 5.4 删除题目
```http
DELETE /analysis/questions/{question_id}
```

## 6. 成绩管理API

### 6.1 获取学生考试成绩
```http
GET /analysis/student-exam-scores
```

**参数**
- `student_id`：学生ID（可选）
- `exam_id`：考试ID（可选）
- `course_id`：课程ID（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "student_id": 1,
      "student_no": "2021001",
      "exam_id": 1,
      "total_score": 85
    }
  ]
}
```

### 6.2 录入考试成绩
```http
POST /analysis/student-exam-scores
```

**请求体**
```json
{
  "student_id": 1,
  "exam_id": 1,
  "total_score": 85
}
```

### 6.3 批量录入成绩
```http
POST /analysis/student-exam-scores/batch
```

**请求体**
```json
{
  "scores": [
    {
      "student_id": 1,
      "exam_id": 1,
      "total_score": 85
    },
    {
      "student_id": 2,
      "exam_id": 1,
      "total_score": 92
    }
  ]
}
```

## 7. 文件上传API

### 7.1 上传CSV文件
```http
POST /analysis/upload-csv
```

**Content-Type**: `multipart/form-data`

**参数**
- `file`: CSV文件

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "filename": "students.csv",
    "data": [
      {
        "student_no": "2021001",
        "name": "张三",
        "class_name": "计算机2101",
        "major": "计算机科学与技术",
        "grade_year": "2021"
      }
    ]
  }
}
```

### 7.2 上传Excel文件
```http
POST /analysis/upload-excel
```

**Content-Type**: `multipart/form-data`

**参数**
- `file`: Excel文件

## 8. 分析计算API

### 8.1 成绩统计分析
```http
GET /analysis/score-statistics
```

**参数**
- `course_id`：课程ID（必需）
- `exam_id`：考试ID（可选）
- `class_name`：班级（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "basic_stats": {
      "total_students": 30,
      "average_score": 78.5,
      "median_score": 80,
      "max_score": 98,
      "min_score": 42,
      "std_dev": 12.5,
      "variance": 156.25
    },
    "distribution": {
      "excellent": { "count": 6, "percentage": 20 },
      "good": { "count": 10, "percentage": 33.33 },
      "medium": { "count": 8, "percentage": 26.67 },
      "pass": { "count": 4, "percentage": 13.33 },
      "fail": { "count": 2, "percentage": 6.67 }
    }
  }
}
```

### 8.2 题目分析
```http
GET /analysis/question-analysis
```

**参数**
- `exam_id`：考试ID（必需）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "question_id": 1,
      "qno": "1",
      "qtype": "单选题",
      "avg_score": 8.5,
      "difficulty": 0.15,
      "discrimination": 0.45,
      "pass_rate": 0.85
    }
  ]
}
```

### 8.3 OBE达成度分析
```http
GET /analysis/obe-achievement
```

**参数**
- `course_id`：课程ID（必需）
- `exam_id`：考试ID（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "course_id": 1,
    "course_name": "数据结构",
    "outcomes": [
      {
        "co_code": "CO1",
        "co_name": "掌握基本概念",
        "achievement": 0.82,
        "threshold": 0.6,
        "status": "achieved"
      }
    ]
  }
}
```

### 8.4 学情预警
```http
GET /analysis/warnings
```

**参数**
- `course_id`：课程ID（可选）
- `level`：预警级别（warning/critical）（可选）
- `status`：处理状态（pending/resolved）（可选）

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "student_id": 1,
      "student_no": "2021001",
      "student_name": "张三",
      "course_id": 1,
      "course_name": "数据结构",
      "level": "critical",
      "reason": "期末成绩低于60分",
      "ai_summary": "该生基础薄弱，建议加强课后辅导",
      "created_at": "2025-01-15T10:30:00Z",
      "status": "pending"
    }
  ]
}
```

## 9. 报表导出API

### 9.1 导出成绩分析报表
```http
GET /analysis/export-score-report
```

**参数**
- `course_id`：课程ID（必需）
- `exam_id`：考试ID（必需）
- `format`：格式（excel/csv）（默认excel）

**响应**
- Excel文件下载

### 9.2 导出OBE分析报告
```http
GET /analysis/export-obe-report
```

**参数**
- `course_id`：课程ID（必需）
- `format`：格式（excel/pdf）（默认excel）

### 9.3 导出预警汇总
```http
GET /analysis/export-warnings
```

**参数**
- `course_id`：课程ID（可选）
- `format`：格式（excel/csv）（默认excel）

## 10. AI分析API

### 10.1 生成AI分析
```http
POST /analysis/ai-analyze
```

**请求体**
```json
{
  "student_id": 1,
  "course_id": 1,
  "analysis_type": "warning"
}
```

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "analysis": "该生在学习过程中表现出以下特点：\n1. 基础知识掌握不够扎实\n2. 作业完成质量有待提高\n3. 建议加强课后练习和辅导"
  }
}
```

### 10.2 批量AI分析
```http
POST /analysis/ai-analyze/batch
```

**请求体**
```json
{
  "student_ids": [1, 2, 3],
  "course_id": 1
}
```

## 11. 系统管理API

### 11.1 健康检查
```http
GET /health
```

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### 11.2 系统信息
```http
GET /system/info
```

**响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "version": "0.1.0",
    "database": "SQLite 3.40.0",
    "python_version": "3.10.12",
    "fastapi_version": "0.104.1"
  }
}
```

## 12. 使用示例

### 12.1 完整的数据导入和分析流程

#### 步骤1：导入学生数据
```bash
curl -X POST http://localhost:8000/api/v1/analysis/upload-csv \
  -F "file=@students.csv"
```

#### 步骤2：创建课程和考试
```bash
curl -X POST http://localhost:8000/api/v1/analysis/courses \
  -H "Content-Type: application/json" \
  -d '{"course_code":"CS101","course_name":"数据结构","term":"2024-2025-1","department":"计算机学院","major":"计算机科学与技术","credit":3.0}'
```

#### 步骤3：导入成绩数据
```bash
curl -X POST http://localhost:8000/api/v1/analysis/student-exam-scores/batch \
  -H "Content-Type: application/json" \
  -d '{"scores":[{"student_id":1,"exam_id":1,"total_score":85}]}'
```

#### 步骤4：获取分析结果
```bash
curl http://localhost:8000/api/v1/analysis/score-statistics?course_id=1
```

#### 步骤5：导出报表
```bash
curl http://localhost:8000/api/v1/analysis/export-score-report?course_id=1&exam_id=1 \
  -o score_report.xlsx
```

### 12.2 错误处理示例

#### 验证错误
```json
{
  "code": 400,
  "message": "请求参数验证失败",
  "data": {
    "errors": [
      {
        "field": "student_no",
        "message": "学号不能为空"
      }
    ]
  }
}
```

#### 资源不存在
```json
{
  "code": 404,
  "message": "学生不存在",
  "data": null
}
```

#### 服务器错误
```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": null
}
```

## 13. 开发建议

### 13.1 请求频率限制
建议对API请求进行频率限制，防止滥用。

### 13.2 缓存策略
对于不经常变化的数据，建议使用缓存提高性能。

### 13.3 日志记录
记录所有API请求和响应，便于调试和审计。

### 13.4 版本管理
API版本应该明确标识，便于后续升级和维护。