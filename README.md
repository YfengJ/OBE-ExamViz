# 基于 OBE 的期末试卷分析与成绩可视化系统

面向高校教师的毕设项目，核心目标是把“简洁成绩输入模板 -> 试卷结构映射 -> OBE 达成度分析 -> 期末试卷分析表导出”串成一条完整工作流。当前版本以“分析任务（Analysis Run）”为中心，输入端只保留系统生成报告必需的原始数据，输出端对齐正式 Word 试卷分析表。

## 当前完成度

- 已支持以“课程 + 班级 + 一次期末考试”为单位创建分析任务
- 已支持导入简洁成绩输入模板，包含基本信息、试卷结构、课程目标和学生逐题得分
- 已实现成绩统计、分数段分布、题型平均得分、逐题得分率、课程目标达成度、规则预警
- 已支持 DeepSeek 生成“持续改进建议”文本
- 已支持导出 Word 版试卷分析文档，内容结构参考老师提供的“试卷分析表”模板
- 已支持上传简洁输入模板，一键创建分析任务、计算达成度并生成正式报告

## 核心工作流

1. 下载并填写 `teacher_input_template.xlsx`
2. 在“数据导入”页上传成绩输入模板
3. 点击“开始计算”，查看：
   - 平均分 / 及格率 / 难度标签
   - 分数段图表
   - 题型平均得分率
   - 课程目标平均分和达成度
   - 逐题分析
4. 在“报告预览”页生成报告正文
5. 在“AI 建议”页生成：
   - 成绩统计摘要
   - 课程目标支撑度分析
   - 课程目标达成度分析
   - 教学持续改进建议
6. 导出 Word 版试卷分析文档

## 系统输入输出设计

### 输入：简洁成绩输入模板

- 输入：
  - `基本信息`
  - `试卷结构`
  - `课程目标`
  - `学生成绩`
- 中间处理：
  - 统一落入 `AnalysisRun`
  - 形成规范化的学生、考试、题目、课程目标和逐题得分数据
  - 自动计算总分、平均分、分数段、题型表现和课程目标达成度
- 输出：
  - 分析页图表
  - 课程目标达成度表
  - 预警建议
  - Word 分析文档

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy / Pandas / NumPy |
| 数据库 | SQLite（默认）/ PostgreSQL（可切换） |
| AI | DeepSeek API（OpenAI 兼容风格） |
| 报表 | openpyxl / CSV / XLSX |

## 目录结构

```text
repo/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      analysis/
      ai/
      reports/
      utils/
      main.py
    tests/
    scripts/
    requirements.txt
    .env.example
    README_BACKEND.md
  frontend/
    src/
      api/
      router/
      views/
      components/
      stores/
      utils/
      main.ts
    index.html
    vite.config.ts
    package.json
    README_FRONTEND.md
  docs/
  sample_data/
  .gitignore
  README.md
```

## 一键启动

必须在项目根目录运行后端。

### 1. 启动后端

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 打开地址

- 前端工作台: [http://localhost:5173](http://localhost:5173)
- 后端 Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

## DeepSeek API 配置

复制根目录或 `backend/` 下的 `.env.example` 为 `.env`，然后填写：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
AUTO_SEED_DEMO_DATA=false
```

未配置 API Key 时，系统会退回规则生成的默认建议文本，不影响主要演示流程。
也就是说，“AI 建议”按钮始终可用，但只有配置了真实 key 才会得到 DeepSeek 增强结果。

## 演示数据

`sample_data/` 已提供 2 个班级、60 名学生、6 门课程的可公开模拟数据；正式输入模板位于 `backend/templates/teacher_input_template.xlsx`。

- `students.csv`
- `courses.csv`
- `exams.csv`
- `exam_scores.csv`
- `questions.csv`
- `question_scores.csv`
- `usual_scores_template.csv`
- `midterm_scores_template.csv`
- `final_scores_template.csv`
- `paper_structure_template.csv`
- `question_scores_template.csv`
- `backend/templates/teacher_input_template.xlsx`

## 主要页面说明

- `分析任务`：创建并切换老师视角的分析批次
- `课程参数`：维护课程、考试、题目等基础对象
- `数据导入`：下载简洁输入模板，上传基本信息、试卷结构、课程目标和学生逐题得分
- `结构分析`：查看统计图表、题目分析和课程目标达成度
- `报告预览`：生成报告正文并导出 Word 文档
- `改进建议`：查看规则预警与 AI 生成的分析文字

## 文档索引

- `/docs/02_requirements.md`
- `/docs/03_architecture.md`
- `/docs/04_database.md`
- `/docs/05_metrics_methods.md`
- `/docs/06_api.md`
- `/docs/08_deployment.md`：包含“压缩拷贝到另一台电脑后如何运行”的完整部署教程
- `/docs/09_github_workflow.md`
- `/docs/10_user_manual.md`
- `/docs/assumptions.md`

## 注意事项

- 后端启动命令必须在项目根目录执行，否则会出现 `ModuleNotFoundError: No module named 'backend'`
- 示例数据默认匿名，`name` 字段允许为空
- AI 分析默认只使用学号或匿名 ID，不向大模型发送姓名

## 下一阶段可扩展项

1. 直接解析教师现有“宽表”Excel 成绩单
2. 导出 `.docx` 格式试卷分析表
3. 增加 Alembic 正式迁移
4. 增加 GitHub Actions CI
