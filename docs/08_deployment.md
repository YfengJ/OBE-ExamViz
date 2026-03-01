# 08 部署文档

## 1. 本地环境要求
- Python 3.10+
- Node.js 18+（推荐 LTS）
- npm 9+

## 2. 创建并使用 venv（强制）
```bash
python -m venv .venv
```

### 激活
- macOS/Linux
```bash
source .venv/bin/activate
```
- Windows
```bash
.venv\Scripts\activate
```

## 3. 安装依赖
```bash
pip install -r backend/requirements.txt
cd frontend && npm install
```

## 4. 环境变量
```bash
copy .env.example .env
```
关键变量：
- `DATABASE_URL`：默认 SQLite
- `DEEPSEEK_API_KEY`：可选
- `ALLOWED_ORIGINS`：前端地址

## 5. 启动
### 后端
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端（新终端）
```bash
cd frontend
npm run dev
```

## 6. 验证
- `http://127.0.0.1:8000/docs` 打开 Swagger
- `http://127.0.0.1:5173` 打开前端
- 分析页可导出 `xlsx`

## 7. 常见错误
1. `vite` 空白页：检查 `frontend/index.html` 是否存在 `#app`。
2. 路由编译报错：检查 `router.ts` 导入文件名是否与 `views` 一致。
3. AI 接口失败：可不填 key，系统会降级返回本地建议文本。
