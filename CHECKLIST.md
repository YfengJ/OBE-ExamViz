# 项目验收清单

这份清单用于本项目的日常自检、迁移后验证、答辩前回归和改动后的快速验收。

## 1. 环境检查

- 项目根目录已打开：`/Users/yfengj/PyCharmMiscProject/repo/repo`
- Python 虚拟环境可用：`.venv`
- 前端依赖已安装：`frontend/node_modules`
- 不复用跨平台搬运过来的 `.venv` 或 `node_modules`
- `.env` 已存在，至少确认：

```env
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./obe_analysis.db
AUTO_SEED_DEMO_DATA=false
```

前端如需切换后端端口，可在 `frontend/.env` 中确认：

```env
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
VITE_API_TIMEOUT_MS=60000
```

## 2. 启动检查

后端：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo/frontend
npm run dev
```

应能打开：

- 前端：[http://localhost:5173](http://localhost:5173)
- 后端健康检查：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- API 交付状态：[http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)，应包含 `checks.database=ok` 和 `privacy.raw_student_identifiers_to_ai=false`
- Swagger：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 3. 基础功能检查

### 首页 `/`

- 能加载“分析任务”列表
- 能创建分析任务
- 创建后能跳转到“导入向导 / 分析结果 / 预警建议”

### 课程参数页 `/courses`

- 能查看课程列表
- 能新增课程
- 能编辑课程
- 能新增考试
- 能编辑考试
- 能新增题目
- 能编辑题目

### 导入向导页 `/exams`

- 能选择分析任务
- 能下载简洁成绩输入模板
- 模板只包含填写说明、基本信息、试卷结构、课程目标、学生成绩
- 模板不包含平均分、达成度、课程目标图表、学生目标达成分布等系统计算结果
- 能上传成绩输入模板并完成结构识别
- 能点击“开始计算”后展示成绩统计、题型表现和课程目标达成度
- 能导入并创建分析任务
- 能直接生成 Word 报告

### 分析页 `/analysis`

- 能切换分析任务
- 能看到 KPI
- 能看到报告生成检查或数据缺失提示
- 能看到成绩分布图
- 能看到课程目标达成表
- 能看到逐题分析表
- 数据不完整时不能生成可信报告，并提示下一步补齐位置

### 预警页 `/warnings`

- 能切换分析任务
- 能看到规则建议文本
- 能看到重点学生预警表
- 能点击“生成 AI 增强建议”

## 4. 数据链路检查

- 新建课程后，能在课程参数页继续新增考试和题目
- 新建考试和题目后，首页创建分析任务时能选到它们
- 逐题得分在已选分析任务时支持 `student_no,qno,score`
- 删除已被引用的课程、考试、学生、题目时，系统应阻止删除

## 5. 自动化回归检查

后端测试：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo
source .venv/bin/activate
python -m pytest backend/tests -q
```

前端构建：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo/frontend
npm run lint
npm run build
```

一键交付验证：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo
./scripts/verify_delivery.sh
```

生成安全交付包：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo
./scripts/package_release.sh
```

期望结果：

- `pytest` 全部通过
- `npm run lint` 通过
- `vite build` 成功
- `git diff --check` 无输出
- AI 隐私高风险搜索无命中
- `output/release/OBE-ExamViz-teacher.zip` 生成成功，且不包含 `.env`、数据库、真实数据目录、输出目录或依赖目录

## 6. 演示数据检查

如果你需要手动灌演示数据：

```bash
cd /Users/yfengj/PyCharmMiscProject/repo/repo
source .venv/bin/activate
python backend/scripts/seed_demo_data.py
```

如果你不想自动污染真实数据环境，保持：

```env
AUTO_SEED_DEMO_DATA=false
```

## 7. 常见异常排查

- 页面能打开但接口 404/500：确认后端是否启动在 `8000`
- 报 `No module named backend`：说明不是在项目根目录启动后端
- `vite: Permission denied`：说明仍在使用跨平台搬来的旧 `node_modules`
- 导入逐题得分失败：确认题号已存在于当前考试的试卷结构中
- 创建课程后首页不能创建任务：先去 `/courses` 补齐考试和题目
- 生成报告按钮不可用：先查看“报告生成检查”，补齐课程信息、试卷结构或逐题得分

## 8. 验收完成标准

满足以下条件即可认为项目“可正常使用”：

- 前后端都能正常启动
- 5 个主页面都能打开
- 课程 -> 考试 -> 题目 -> 分析任务 -> 导入 -> 分析 -> 导出 这条主链路可走通
- `pytest` 通过
- `npm run lint` 通过
- `npm run build` 通过
- `./scripts/verify_delivery.sh` 通过
- 浏览器控制台没有新的项目级错误
