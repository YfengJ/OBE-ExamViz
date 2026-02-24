# 基于OBE的期末试卷分析与成绩可视化系统

## 项目简介
基于成果的教育（OBE）理念下的期末试卷分析与成绩可视化系统，支持成绩统计分析、题目质量评估、OBE达成度计算和学情预警功能。

## 技术栈
- **后端**: Python 3.10+, FastAPI, SQLAlchemy, Pandas, SQLite/PostgreSQL
- **前端**: Vue 3, Vite, Element Plus, ECharts
- **AI集成**: DeepSeek API

## 核心功能
- 成绩数据导入（CSV/Excel）
- 成绩统计与分析
- 题目难度/区分度分析
- OBE达成度计算
- 学情预警
- 可视化图表展示
- Excel报表导出

## 快速开始

### 后端启动
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 文档结构
- `docs/01_background_research.md` - 背景研究
- `docs/02_requirements.md` - 需求分析
- `docs/03_architecture.md` - 架构设计
- `docs/04_database.md` - 数据库设计
- `docs/05_metrics_methods.md` - 指标计算方法
- `docs/06_api.md` - API文档
- `docs/07_testing.md` - 测试文档
- `docs/08_deployment.md` - 部署文档
- `docs/09_github_workflow.md` - GitHub工作流
- `docs/assumptions.md` - 假设记录

## 演示数据
`sample_data/` 目录包含示例数据，可直接导入系统演示完整功能。

## 项目截图
（待添加）

## 版本历史
- v0.1.0 - 初始版本（M1里程碑）