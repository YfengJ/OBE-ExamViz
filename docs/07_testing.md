# 07 测试文档

## 1. 测试策略
- 目标：保证系统可运行、可联调、可演示、可重复调用。
- 范围：后端 API、前端构建、关键业务链路（分析/预警/导出）。

## 2. 本轮已执行验证

### 2.1 后端基础
- `GET /health` 返回 200
- 后端服务可启动（端口被占用时改用现有运行实例进行烟测）

### 2.2 核心接口烟测
- `GET /api/v1/analysis/courses` 返回 200
- `GET /api/v1/analysis/score-statistics?course_id=1` 返回 200
- `GET /api/v1/analysis/question-analysis?exam_id=1` 返回 200
- `GET /api/v1/analysis/obe-achievement?course_id=1&exam_id=1` 返回 200
- `POST /api/v1/analysis/warnings/generate` 返回 200
- `GET /api/v1/analysis/export-score-report?course_id=1&exam_id=1` 返回 200，`Content-Type` 为 xlsx

### 2.3 幂等回归（本次新增）
- 场景：连续 3 次调用 `score-statistics`。
- 预期：全部 200，且不出现 `UNIQUE constraint failed: courses.course_code`。
- 结果：通过。

### 2.4 前端工程
- `npm run build` 通过。
- 页面不再白屏，核心路由可访问。

## 3. 缺陷与修复
- 缺陷：`ensure_seed_data_for_demo` 非幂等，导致重复插入课程触发唯一索引冲突。
- 修复：改为按唯一键存在即跳过（学生、课程、考试、题目、学生考试成绩均行级去重）。

## 4. 后续建议
1. 增加 pytest API 自动化用例，覆盖幂等种子逻辑。
2. 增加前端 E2E（Playwright）最小冒烟：进入分析页并触发导出。
3. 在 CI 中加入后端 smoke 测试脚本，防止回归。
