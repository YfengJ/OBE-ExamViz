# 基于 OBE 的期末试卷分析与成绩可视化系统

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/YfengJ/OBE-ExamViz/actions/workflows/ci.yml/badge.svg)](https://github.com/YfengJ/OBE-ExamViz/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](backend/requirements.txt)
[![Vue](https://img.shields.io/badge/Vue-3-42b883.svg)](frontend/package.json)

OBE-ExamViz 是面向高校教师的 OBE 期末试卷分析系统，核心目标是把“简洁成绩输入 -> 课程目标达成度计算 -> AI 辅助改进建议 -> Word 试卷分析表导出”串成一条完整工作流。

当前版本强调本地部署、隐私保护和可交付性：系统源码可以公开维护，但 API Key、数据库、真实成绩文件、真实教学大纲和历史导出报告不应进入仓库。

## 主要能力

- **简洁成绩输入模板**：只保留系统生成报告必需的原始数据，不再要求教师手工填写平均分、达成度、图表等系统可计算内容。
- **教学大纲建课**：支持通过教学大纲提取课程代码、课程名称、开课学期、学院、专业、学分、课程负责人、课程描述和课程目标。
- **兼容成绩导入**：支持系统简洁模板，也兼容开发期间使用过的真实成绩文件结构。
- **OBE 达成度分析**：自动计算分数段、题型表现、逐题得分率、课程目标达成度和报告就绪度。
- **AI 改进建议**：可根据成绩统计和课程目标生成教学建议，并尽量只向外部模型发送聚合或匿名化信息。
- **Word 报告导出**：将系统计算结果和已生成建议写入正式试卷分析文档。
- **交付友好**：默认排除本地数据库、真实数据、输出文件、依赖目录和环境变量文件。

## 界面截图

以下截图来自临时演示数据库，只包含示例课程、示例班级、示例教师等公开占位数据，不包含真实学生、真实成绩、真实大纲或 API Key。

| 分析工作台 | 课程参数 |
| --- | --- |
| ![分析工作台](docs/assets/screenshots/home-workbench.png) | ![课程参数](docs/assets/screenshots/course-parameters.png) |

| 数据导入 | 结构分析 |
| --- | --- |
| ![数据导入中心](docs/assets/screenshots/data-import.png) | ![结构分析](docs/assets/screenshots/structure-analysis.png) |

| 报告预览 |
| --- |
| ![报告预览](docs/assets/screenshots/report-preview.png) |

## 使用流程

1. 创建或选择已有课程。
2. 可选：上传教学大纲直接创建课程。
3. 上传成绩文件。
4. 先预览识别结果，再确认导入。
5. 点击开始计算。
6. 查看成绩分布、题型表现、课程目标达成度和数据完整性提示。
7. 需要时生成 AI 建议。
8. 导出 Word 版试卷分析文档。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Element Plus、ECharts |
| 后端 | Python 3.10+、FastAPI、SQLAlchemy、Pandas、NumPy |
| 数据库 | 默认 SQLite，可扩展 PostgreSQL |
| AI | DeepSeek API，OpenAI 兼容调用方式 |
| 报告 | openpyxl、python-docx、XLSX / DOCX 生成 |

## 目录结构

```text
repo/
  backend/
    app/
      api/
      ai/
      core/
      db/
      models/
      reports/
      schemas/
      services/
      utils/
      main.py
    templates/
    tests/
    requirements.txt
  frontend/
    src/
      api/
      components/
      stores/
      views/
      main.ts
    package.json
    vite.config.ts
  docs/
  sample_data/
  scripts/
  CHECKLIST.md
  README.md
  README.zh-CN.md
```

## 快速启动

后端必须在项目根目录启动。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

支持 Python 3.12。后端依赖文件会在 Python 3.12 下自动选择兼容的 NumPy 安装包。

Windows 激活虚拟环境：

```powershell
.venv\Scripts\activate
```

另开一个终端启动前端：

```bash
cd frontend
npm install
npm run dev
```

访问地址：

- 前端工作台：[http://localhost:5173](http://localhost:5173)
- 后端接口文档：[http://localhost:8000/docs](http://localhost:8000/docs)

如果后端端口不是 `8000`，可在 `frontend/.env` 中配置：

```env
VITE_API_PROXY_TARGET=http://127.0.0.1:8001
VITE_API_TIMEOUT_MS=60000
```

## 环境变量

复制 `.env.example` 或 `backend/.env.example` 为 `.env`，然后填写本机需要的配置。

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
AUTO_SEED_DEMO_DATA=false
```

未配置 API Key 时，导入、计算、可视化和报告导出仍可使用；AI 文本会退回本地规则生成内容。

## 隐私与仓库维护

不要提交隐私数据和本地运行文件。

- 不提交 `.env`、`.env.*`、API Key、Token 或本地凭据。
- 不提交 SQLite 数据库、生成报告、临时导出文件或交付压缩包。
- 不提交真实成绩工作簿、真实教学大纲、学生姓名学号或教师提供的私有文件。
- AI 请求应尽量使用聚合统计或匿名化上下文，而不是学生姓名和学号。
- 给老师的交付包应基于清理后的源码生成，并在分享前运行验证。

常见排除目录包括 `data/`、`output/`、`tmp/`、本地数据库、依赖目录和环境变量文件。

## 模板与文档

- 成绩输入模板：`backend/templates/teacher_input_template.xlsx`
- Word 报告模板：`backend/templates/teacher_report_template.docx`
- 给老师部署说明：[docs/部署与使用说明.md](docs/部署与使用说明.md)
- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全说明：[SECURITY.md](SECURITY.md)
- 维护路线图：[ROADMAP.md](ROADMAP.md)
- 更新日志：[CHANGELOG.md](CHANGELOG.md)
- 交付检查清单：[CHECKLIST.md](CHECKLIST.md)
- 英文 README：[README.md](README.md)

## 交付前验证

提交、打包或发布前建议运行：

```bash
./scripts/verify_delivery.sh
```

该脚本会检查补丁空白、AI 隐私高风险写法、后端测试和前端生产构建。

也可以手动运行：

```bash
python -m pytest backend/tests -q
cd frontend && npm run build
```

## 公开维护说明

- README 和公开文档尽量使用通用描述，不写真实班级、教师、学生或课程文件名。
- 交付压缩包、导出报告和运行数据库应放在被忽略目录中。
- 如果后续要上传 GitHub，先检查 `git status` 和 `git diff --stat`，只提交安全公开的源码、模板、示例数据和文档。
