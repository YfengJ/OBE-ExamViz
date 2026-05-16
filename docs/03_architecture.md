# 系统架构设计

## 1. 架构目标

本系统不是泛化 BI 看板，而是围绕“某学期、某课程、某班级、某次期末考试”的教师分析工作流设计。系统的核心对象是 `AnalysisRun`，即一份可追踪、可导入、可分析、可导出的试卷分析任务。

## 2. 总体架构

```text
┌──────────────────────────────────────────────────────────────┐
│                        Vue 3 前端工作台                     │
│  分析任务页  导入向导  分析结果页  改进建议页  导出操作      │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼──────────────────────────────────┐
│                      FastAPI 应用服务层                      │
│  API Router  参数校验  统一响应  统一异常  配置读取          │
├──────────────────────────────────────────────────────────────┤
│                      业务服务 / 分析服务                     │
│  AnalysisRun Service   Import Service   Warning Service      │
│  Analysis Service      DeepSeek Client  Excel Report Builder │
├──────────────────────────────────────────────────────────────┤
│                      SQLAlchemy 数据访问层                   │
│  Student  Course  Exam  Question  AnalysisRun  OBEOutcome   │
│  StudentExamScore  StudentQuestionScore  StudentComponent    │
└───────────────────────────┬──────────────────────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │ SQLite / PostgreSQL │
                 └─────────────────────┘
```

## 3. 业务分层

### 3.1 前端层

- `views/`：按教师工作流组织页面，而不是按技术对象堆叠页面
- `api/`：封装所有后端请求，统一处理 `ApiEnvelope`
- `stores/`：保存当前选中的 `AnalysisRun`
- `components/`：图表、卡片、表格等复用组件

### 3.2 API 层

- 路由入口位于 `/backend/app/api/`
- 负责：
  - 参数接收与基础校验
  - 调用 Service
  - 返回统一 JSON 响应
  - 文件流导出

### 3.3 Service 层

- `analysis_run_service.py`
  - 组织分析任务
  - 维护任务快照（应考/实考、状态）
  - 汇总教师页面所需数据
- `import_service.py`
  - 解析 CSV / XLSX
  - 中文字段映射
  - 导入结果统计与错误预览
- `analysis_service.py`
  - 通用成绩统计与题目分析
- `warning_service.py`
  - 规则预警与状态管理
- `deepseek_client.py`
  - 生成分析说明与持续改进建议

### 3.4 Report 层

- `excel_report.py`
  - 负责生成老师模板风格的 Excel 分析表
  - 按 sheet 输出期末成绩单、班级分析、课程目标平均分和达成度、分析图、文字分析
- `docx_report.py`
  - 负责生成老师模板风格的 Word 版试卷分析文档
  - 输出成绩统计、课程目标分析、逐题分析、预警与持续改进建议

## 4. 关键设计决策

### 4.1 以 AnalysisRun 为业务中心

旧版本接口以 `course_id + exam_id` 为中心，适合做零散查询，不适合做老师最终交付的分析表。
当前版本新增 `AnalysisRun`，把以下信息绑定在一起：

- 学年学期
- 课程
- 班级
- 任课教师
- 考试日期
- 应考 / 实考人数
- 平时 / 期中 / 期末权重
- OBE 阈值

这样前端可以围绕“一个任务”完成导入、分析、导出闭环。

### 4.2 导入流程面向教师文件，而不是数据库字段

导入接口支持中文别名，如：

- `学号 -> student_no`
- `平时成绩 / 期中成绩 / 期末成绩 / 总分 -> score / total_score`
- `课程目标 -> co_code`
- `题型分组 -> qgroup_name`

这样老师可以按模板文件填数据，不必理解后端字段名。

### 4.3 OBE 与试卷分析一体化

系统将题目结构中的 `co_code`、`co_weight`、`expected_threshold` 与学生逐题得分联动，生成：

- 单题分析
- 题型分析
- 学生层课程目标达成度
- 班级层课程目标达成度
- 课程目标总达成结果

## 5. 前端信息架构

### 5.1 分析任务页

- 创建新的试卷分析任务
- 查看任务准备状态
- 跳转到导入、分析、改进建议页面

### 5.2 导入向导页

- 步骤 1：平时成绩
- 步骤 2：期中成绩
- 步骤 3：期末成绩
- 步骤 4：试卷结构
- 步骤 5：逐题得分

### 5.3 分析结果页

- KPI 卡片
- 分数段图
- 题型平均得分率
- 课程总评构成
- 课程目标平均分和达成度
- 逐题分析
- 模板化 Excel 导出

### 5.4 改进建议页

- 规则预警名单
- 成绩统计摘要
- 课程目标支撑度分析
- 达成度分析
- AI 持续改进建议

## 6. 后端模块映射

| 模块 | 说明 |
|------|------|
| `backend/app/api/analysis_runs.py` | 分析任务相关接口 |
| `backend/app/api/imports.py` | 教师导入接口 |
| `backend/app/services/analysis_run_service.py` | 分析任务编排与聚合 |
| `backend/app/services/import_service.py` | 导入解析与入库 |
| `backend/app/reports/excel_report.py` | 模板化 Excel 导出 |
| `backend/app/ai/deepseek_client.py` | DeepSeek 文本生成 |

## 7. 可扩展性

当前版本为了保证毕设可演示，优先实现了 Excel 模板导出与文字稿生成。
后续可以继续扩展：

1. 直接解析教师原始宽表 Excel
2. 基于模板导出 `.docx`
3. 引入 Alembic 正式迁移
4. 支持多学院、多课程组、多学期历史对比
