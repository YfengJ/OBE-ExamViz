# 数据库设计

## 1. 数据库选型

系统默认使用SQLite数据库，支持切换到PostgreSQL。SQLite轻量级、无需安装，适合快速开发和小型应用；PostgreSQL功能更强大，适合大型应用。

## 2. ER图设计

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Student   │      │   Course    │      │    Exam     │
│─────────────│      │─────────────│      │─────────────│
│ id          │      │ id          │      │ id          │
│ student_no  │      │ course_code │      │ course_id   │
│ name        │      │ course_name │      │ exam_type   │
│ class_name  │      │ term        │      │ name        │
│ major       │      │ department  │      │ date        │
│ grade_year  │      │ major       │      │ total_score │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │                    │                    │
       └──────┬──────┬──────┘                    │
              │      │                           │
              │      │                           │
       ┌──────▼──────▼──────┐            ┌──────▼──────┐
       │  StudentExamScore  │            │   Question  │
       │────────────────────│            │─────────────│
       │ id                 │            │ id          │
       │ student_id         │            │ exam_id     │
       │ exam_id            │            │ qno         │
       │ total_score        │            │ qtype       │
       └────────────────────┘            │ score       │
                                         │ section     │
                                         │ knowledge_  │
                                         │ point       │
                                         │ co_code     │
                                         │ indicator_  │
                                         │ code        │
                                         └──────┬──────┘
                                                │
                                                │
                                                │
                                         ┌──────▼──────┐
                                         │  Student    │
                                         │ Question    │
                                         │ Score       │
                                         │─────────────│
                                         │ id          │
                                         │ student_id  │
                                         │ question_id │
                                         │ score       │
                                         └─────────────┘
```

## 3. 数据表结构

### 3.1 学生表 (students)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| student_no | String | Unique, Index, Not Null | 学号 |
| name | String | Nullable | 姓名（脱敏，可为空） |
| class_name | String | Not Null | 班级 |
| major | String | Not Null | 专业 |
| grade_year | String | Not Null | 年级 |

### 3.2 课程表 (courses)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| course_code | String | Unique, Not Null | 课程代码 |
| course_name | String | Not Null | 课程名称 |
| term | String | Not Null | 学期 |
| department | String | Not Null | 院系 |
| major | String | Not Null | 专业 |
| credit | Float | Default: 0.0 | 学分 |
| description | Text | Nullable | 课程描述 |

### 3.3 考试表 (exams)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| course_id | Integer | FK, Not Null | 课程ID |
| exam_type | String | Not Null | 考试类型 (usual/mid/final) |
| name | String | Not Null | 考试名称 |
| date | Date | Not Null | 考试日期 |
| total_score | Float | Default: 100.0 | 满分 |

### 3.4 题目表 (questions)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| exam_id | Integer | FK, Not Null | 考试ID |
| qno | String | Not Null | 题号 |
| qtype | String | Not Null | 题型 |
| score | Float | Default: 0.0 | 该题满分 |
| section | String | Nullable | 所属章节 |
| knowledge_point | String | Nullable | 知识点 |
| co_code | String | Nullable | 课程目标代码 |
| indicator_code | String | Nullable | 指标点代码 |

### 3.5 学生考试分数表 (student_exam_scores)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| student_id | Integer | FK, Not Null | 学生ID |
| exam_id | Integer | FK, Not Null | 考试ID |
| total_score | Float | Default: 0.0 | 考试总分 |

### 3.6 平时成绩表 (assessment_components)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| course_id | Integer | FK, Not Null | 课程ID |
| name | String | Not Null | 成绩项名称 |
| weight | Float | Default: 0.0 | 权重 |

### 3.7 学生平时成绩表 (student_component_scores)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| student_id | Integer | FK, Not Null | 学生ID |
| component_id | Integer | FK, Not Null | 成绩项ID |
| score | Float | Default: 0.0 | 得分 |

### 3.8 学生题目分数表 (student_question_scores)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| student_id | Integer | FK, Not Null | 学生ID |
| question_id | Integer | FK, Not Null | 题目ID |
| score | Float | Default: 0.0 | 得分 |

### 3.9 OBE课程目标表 (obe_outcomes)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| course_id | Integer | FK, Not Null | 课程ID |
| co_code | String | Not Null | 课程目标代码 |
| co_name | String | Not Null | 课程目标名称 |
| threshold | Float | Default: 0.6 | 达成度阈值 |

### 3.10 预警规则表 (warning_rules)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| course_id | Integer | FK, Nullable | 课程ID（为空表示全局） |
| name | String | Not Null | 规则名称 |
| level | String | Not Null | 预警级别 (warning/critical) |
| config_json | JSON | Not Null | 规则配置 |

### 3.11 预警结果表 (warning_results)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | Integer | PK, Index | 主键 |
| student_id | Integer | FK, Not Null | 学生ID |
| course_id | Integer | FK, Not Null | 课程ID |
| term | String | Not Null | 学期 |
| level | String | Not Null | 预警级别 |
| reasons_json | JSON | Not Null | 预警原因 |
| ai_summary | String | Nullable | AI分析摘要 |
| created_at | DateTime | Default: Now | 创建时间 |

## 4. 索引设计

### 4.1 主键索引
- 所有表的主键自动创建索引

### 4.2 唯一索引
- `students.student_no` - 学号唯一
- `courses.course_code` - 课程代码唯一

### 4.3 外键索引
- 所有外键字段创建索引，提高关联查询性能

### 4.4 复合索引
- 根据查询需求，考虑创建复合索引：
  - `(student_id, exam_id)` 在 student_exam_scores 表
  - `(exam_id, qno)` 在 questions 表
  - `(course_id, term)` 在 warning_results 表

## 5. 数据完整性约束

### 5.1 外键约束
- 启用SQLite外键支持
- 设置级联删除规则

### 5.2 检查约束
- `exam_type` 只允许 'usual', 'mid', 'final'
- `level` 只允许 'warning', 'critical'
- 分数范围检查 (0-100)

### 5.3 非空约束
- 关键字段设置为非空
- 设置合理的默认值

## 6. 数据库操作规范

### 6.1 查询优化
- 使用索引避免全表扫描
- 合理使用JOIN
- 避免SELECT *
- 使用LIMIT限制结果集

### 6.2 事务管理
- 批量操作使用事务
- 设置合适的事务隔离级别
- 异常处理确保事务完整性

### 6.3 备份策略
- 定期备份数据库
- 支持数据导出/导入
- 记录数据操作日志

## 7. 数据库迁移

### 7.1 版本控制
- 使用Alembic进行数据库版本管理
- 每个版本对应代码版本

### 7.2 升级脚本
- 提供升级和降级脚本
- 测试脚本的正确性
- 备份数据后再执行迁移

### 7.3 数据验证
- 迁移后验证数据完整性
- 检查约束和索引
- 测试关键查询性能

## 8. 性能优化建议

### 8.1 查询优化
- 分析慢查询日志
- 优化SQL语句
- 合理使用缓存

### 8.2 连接池
- 配置数据库连接池
- 设置最大连接数
- 监控连接状态

### 8.3 分库分表
- 大数据量时考虑分库分表
- 按学期或课程分表
- 历史数据归档

## 9. 安全考虑

### 9.1 权限控制
- 最小权限原则
- 区分读写权限
- 敏感数据加密

### 9.2 SQL注入防护
- 使用参数化查询
- 输入验证和过滤
- ORM防止注入

### 9.3 审计日志
- 记录数据修改操作
- 追踪异常访问
- 定期审计分析

## 10. 监控指标

### 10.1 数据库状态
- 连接数监控
- 查询性能
- 锁等待情况

### 10.2 存储空间
- 数据库文件大小
- 增长率监控
- 空间预警

### 10.3 备份状态
- 备份完整性
- 备份时间
- 恢复测试