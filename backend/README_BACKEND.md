# Backend 说明

## 1. 环境准备（必须使用 venv）
```bash
python -m venv .venv
```

### 激活虚拟环境
- Windows（PowerShell）
```bash
.venv\Scripts\activate
```
- macOS/Linux
```bash
source .venv/bin/activate
```

## 2. 安装依赖
```bash
pip install -r backend/requirements.txt
```

## 3. 配置环境变量
```bash
copy .env.example .env
```
填写 `DEEPSEEK_API_KEY`（可选，不填则 AI 返回降级文案）。

## 4. 启动服务
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- 健康检查：`http://127.0.0.1:8000/health`
- API文档：`http://127.0.0.1:8000/docs`

## 5. 常见问题排查
1. `ModuleNotFoundError: No module named app`
- 请从仓库根目录启动：`uvicorn backend.app.main:app ...`

2. SQLite 权限或路径问题
- 检查 `DATABASE_URL`，默认是 `sqlite:///./obe_analysis.db`。

3. CORS 报错
- 检查 `.env` 的 `ALLOWED_ORIGINS` 是否包含前端地址（5173/5174）。

4. DeepSeek 调用失败
- 若 key 未配置，系统会自动返回本地降级说明，不影响主流程演示。
