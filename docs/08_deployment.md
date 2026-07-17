# 08 部署文档

## 1. 适用场景

本文档面向这种部署方式：

- 不使用 Git
- 直接把整个项目目录压缩后拷贝到另一台电脑
- 在目标电脑上解压后，本地启动前后端

这也是本项目最适合答辩演示、教师本地试用、实验室电脑临时部署的方式。

## 2. 部署前准备

建议把项目放在一个路径简单的目录下，例如：

- `D:\obe-paper-analysis`
- `E:\graduation-project\obe-system`

不建议放在过深、带很多特殊字符的路径里。中文路径通常也能运行，但为了减少 Python、Node、Excel 读写的兼容问题，优先使用短路径。

目标电脑需要提前安装：

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm 9 或更高版本

可用以下命令检查：

```bash
python --version
node -v
npm -v
```

如果 `python` 不可用，Windows 可以尝试：

```bash
py --version
```

## 3. 需要拷贝哪些文件

最稳妥的做法是把整个 `repo` 目录压缩后拷贝到目标电脑，再解压。

建议至少包含这些内容：

- `backend/`
- `frontend/`
- `docs/`
- `sample_data/`
- `README.md`
- `.gitignore`

### 3.1 是否要一起拷贝 `.venv`

不建议默认拷贝 `.venv`，原因是：

- 不同电脑的 Python 路径不同
- 不同系统或不同架构下虚拟环境通常不能直接复用
- 复制后的 `.venv` 很容易出现依赖损坏、路径失效、解释器找不到的问题

推荐做法是：

- 复制项目源码
- 到目标电脑后重新创建 `.venv`
- 重新安装依赖

### 3.2 是否要一起拷贝 `node_modules`

同样不建议默认拷贝 `frontend/node_modules`，推荐到目标电脑重新执行 `npm install`。

## 4. 目标电脑上的完整部署步骤

以下命令以 Windows PowerShell 为例，且假设项目被解压到了 `D:\obe-paper-analysis`。

### 第 1 步：进入项目根目录

```powershell
cd D:\obe-paper-analysis
```

后端必须在项目根目录启动，而不是在 `backend` 目录里启动。

如果你在 `backend` 目录执行下面的命令：

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

会出现：

```text
ModuleNotFoundError: No module named 'backend'
```

这是因为启动目录不对。

### 第 2 步：创建 Python 虚拟环境

```powershell
python -m venv .venv
```

如果本机需要用 `py` 启动：

```powershell
py -3.10 -m venv .venv
```

### 第 3 步：激活虚拟环境

Windows：

```powershell
.\.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

激活成功后，终端前面通常会出现 `(.venv)`。

### 第 4 步：安装后端依赖

```powershell
pip install -r backend/requirements.txt
```

如果安装很慢，可以先升级 `pip`：

```powershell
python -m pip install --upgrade pip
```

### 第 5 步：配置环境变量

本项目后端会从项目根目录读取 `.env` 文件。

也就是说，最终应当存在这个文件：

- `D:\obe-paper-analysis\.env`

推荐做法是：

1. 在目标电脑项目根目录手动新建 `.env`
2. 参考 `backend/.env.example` 填写内容

最小可用示例：

```env
PROJECT_NAME=OBE Paper Analysis System
VERSION=0.1.0
API_V1_STR=/api/v1
HOST=0.0.0.0
PORT=8000
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=sqlite:///./obe_analysis.db

DEEPSEEK_API_KEY=
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

SECRET_KEY=replace-with-random-secret
ALGORITHM=HS256
```

说明：

- `DATABASE_URL=sqlite:///./obe_analysis.db` 表示默认使用 SQLite，本地演示最方便
- `DEEPSEEK_API_KEY` 如果不填，系统仍可运行，只是 AI 文本会退回规则生成版本
- 如果你已经在当前电脑配置好了 `.env`，并且目标电脑也是你自己使用，可以把根目录 `.env` 一起复制过去
- 如果目标电脑是答辩机、公共电脑或需要交给别人，建议手动新建 `.env`，不要直接传播你的私钥

### 第 6 步：安装前端依赖

```powershell
cd frontend
npm install
cd ..
```

### 第 7 步：启动后端

确保当前目录仍然是项目根目录，例如：

- `D:\obe-paper-analysis`

然后执行：

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后应看到类似输出：

```text
Uvicorn running on http://0.0.0.0:8000
```

### 第 8 步：启动前端

打开第二个终端窗口，进入前端目录：

```powershell
cd D:\obe-paper-analysis\frontend
npm run dev
```

启动成功后应看到类似输出：

```text
Local:   http://localhost:5173/
```

### 第 9 步：访问系统

浏览器打开：

- 前端页面：`http://localhost:5173`
- 后端接口文档：`http://localhost:8000/docs`

## 5. 首次运行后的正确验证方式

建议按下面顺序检查：

### 5.1 检查后端是否正常

打开：

- `http://localhost:8000/docs`

如果 Swagger 页面能打开，说明 FastAPI 已正常启动。

### 5.2 检查前端是否正常

打开：

- `http://localhost:5173`

如果首页能显示“分析任务工作台”或类似教师工作流界面，说明前端已正常启动。

### 5.3 检查前后端联通是否正常

进入系统后：

1. 打开“分析任务”
2. 查看是否能拉取任务列表
3. 进入“分析结果”
4. 查看是否能显示统计卡片和图表

如果前端页面能打开，但接口请求失败，通常是：

- 后端没有启动
- 后端端口不是 `8000`
- `.env` 里的 `ALLOWED_ORIGINS` 没包含前端地址

## 6. DeepSeek API 在新电脑上的处理方式

### 6.1 不填 Key 能不能运行

可以。

系统在没有 `DEEPSEEK_API_KEY` 时仍然可以正常运行，区别只是：

- 可以做成绩分析
- 可以做 Excel / Word 导出
- 可以做规则预警
- 但“AI 分析说明”会退回规则文本，不会真正调用 DeepSeek

### 6.2 如果要启用真实 AI 分析

在根目录 `.env` 中填写：

```env
DEEPSEEK_API_KEY=你的真实Key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

填写后重启后端即可。

### 6.3 安全建议

- 不要把真实 Key 写进 `README.md`
- 不要把真实 Key 写进 `backend/.env.example`
- 不要把真实 Key 放进压缩包发给别人
- 如果 Key 已经在聊天记录、截图或共享文件里暴露过，建议到 DeepSeek 后台轮换

## 7. 数据文件和数据库说明

### 7.1 SQLite 数据库文件

默认情况下，系统会在项目根目录生成数据库文件，例如：

- `D:\obe-paper-analysis\obe_analysis.db`

这意味着：

- 只要复制整个项目目录和这个数据库文件，就能保留原有数据
- 如果不复制数据库文件，系统会在新电脑上重新创建一份空库或重新生成示例数据

### 7.2 示例数据

项目内的 `sample_data/` 可以用于演示和初始化导入，包括：

- 学生名单
- 平时成绩模板
- 期中成绩模板
- 期末成绩模板
- 试卷结构模板
- 逐题得分模板

如果你要去答辩，建议提前在目标电脑导入一套固定的演示数据，并确认：

- 课程目标达成对比可显示
- 题型平均得分率可显示
- 课程目标平均分和达成度可显示
- 逐题分析可显示
- Excel 和 Word 导出都能正常下载

## 8. 推荐的“打包迁移”方式

### 方案 A：最稳妥，推荐

打包这些内容：

- 项目源码
- `sample_data/`
- `docs/`

不要打包：

- `.venv/`
- `frontend/node_modules/`

到目标电脑后重新执行：

1. 创建 `.venv`
2. 安装 `pip` 依赖
3. 安装 `npm` 依赖
4. 配置 `.env`
5. 启动前后端

这是最稳定、最不容易出兼容问题的方式。

### 方案 B：带数据库一起迁移

如果你希望新电脑保留当前电脑已经录入好的分析任务和成绩数据，可以额外打包：

- 根目录 `.env`
- 根目录 `obe_analysis.db`

这样在目标电脑解压后，系统会直接看到原有数据。

注意：

- `.env` 里可能包含真实 API Key
- 如果压缩包要发给别人，建议不要直接带 `.env`

## 9. 目标电脑不能联网时怎么办

如果目标电脑无法联网，那么下面两个步骤会失败：

- `pip install -r backend/requirements.txt`
- `npm install`

这时有两种办法：

### 办法 1：提前在可联网电脑准备完整运行目录

在当前电脑先安装好：

- `.venv`
- `frontend/node_modules`

然后整目录一起复制到目标电脑。

这个办法只在下面条件下更稳：

- 两台电脑都是 Windows
- Python 主版本一致
- Node 主版本一致
- 架构一致

否则仍可能出现兼容问题。

### 办法 2：提前准备离线依赖包

如果你需要更正式的离线部署，可以提前下载：

- Python wheel 包
- npm 离线缓存

但这套流程较复杂，通常答辩场景不必优先做。

## 10. 常见问题排查

### 10.1 `ModuleNotFoundError: No module named 'backend'`

原因：

- 你在 `backend` 目录里启动了 `uvicorn`

解决：

- 回到项目根目录再启动

正确命令：

```powershell
cd D:\obe-paper-analysis
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 10.2 前端能打开，但页面是空白

先检查：

1. 浏览器控制台是否报 Vue 编译错误
2. 后端是否正常启动
3. 接口是否请求到了 `http://localhost:8000`

最常见原因：

- 前端热更新后某个 Vue 文件模板写坏
- 后端没启动
- 旧接口缓存或代理地址不对

### 10.3 `npm install` 或 `npm run dev` 失败

建议检查：

- `node -v` 是否为 18+
- 是否存在公司网络、校园网代理限制
- 是否删过 `package-lock.json`

可以尝试：

```powershell
cd D:\obe-paper-analysis\frontend
npm cache clean --force
npm install
```

### 10.4 `pip install` 失败

建议检查：

- Python 版本是否为 3.10+
- 是否激活了 `.venv`
- `pip` 是否过旧

可尝试：

```powershell
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 10.5 AI 分析按钮可以点，但内容不像真正的大模型输出

原因通常是：

- `.env` 中未配置 `DEEPSEEK_API_KEY`
- 或者 Key 填了但后端没有重启

解决：

1. 检查根目录 `.env`
2. 确认 `DEEPSEEK_API_KEY` 已填写
3. 重启后端

### 10.6 端口被占用

如果 `8000` 或 `5173` 被占用，可以改端口。

后端改为 `8001`：

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
```

如果你改了后端端口，记得同步调整前端请求地址或代理配置。

前端开发服务器默认只监听本机地址 `127.0.0.1`。如果确实需要局域网访问，可以在 `frontend/.env` 中临时配置：

```env
VITE_DEV_HOST=0.0.0.0
```

公共网络、答辩机或共享电脑上不建议长期使用 `0.0.0.0`。

## 11. 建议的答辩演示部署流程

建议你在答辩前一天按下面流程完整演练一遍：

1. 在另一台电脑上新建空目录
2. 解压项目
3. 创建 `.venv`
4. 安装后端依赖
5. 安装前端依赖
6. 配置根目录 `.env`
7. 启动后端
8. 启动前端
9. 打开系统并检查图表
10. 测试一次 Excel 导出
11. 测试一次 Word 导出
12. 测试一次 AI 建议生成

只要这 12 步都走通，答辩现场就会稳很多。

## 12. 快速命令清单

### Windows 一次性部署

```powershell
cd D:\obe-paper-analysis
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

第二个终端：

```powershell
cd D:\obe-paper-analysis\frontend
npm run dev
```

### 访问地址

- 前端：`http://localhost:5173`
- 后端 Swagger：`http://localhost:8000/docs`

## 13. 本项目部署结论

本项目本质上是一个标准的“前后端分离 + 本地 SQLite + `.env` 配置”系统，所以只要满足下面四个条件，就能在另一台电脑正常运行：

1. 项目完整解压
2. 目标电脑安装了 Python 和 Node.js
3. 在项目根目录创建并激活 `.venv`
4. 在项目根目录配置好 `.env`

如果你只是把项目拿到另一台自己的电脑上继续开发或演示，推荐直接采用本文档的方法，不需要 Git，也不需要额外部署服务器。
