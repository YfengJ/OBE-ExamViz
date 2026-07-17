# 09 GitHub 工作流

这份文档用于维护公开仓库，不用于记录真实课程、真实学生或本地部署私密信息。

## 1. 初始化与首次提交
```bash
git init
git add .
git commit -m "chore: init project scaffold"
```

## 2. 关联远程仓库并推送
```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

## 3. 分支策略
- `main`：稳定可演示版本
- `dev`：日常集成
- `feature/*`：功能分支（示例：`feature/obe-metrics`）

推荐合并流：`feature/* -> dev -> main`

## 4. 提交规范（Conventional Commits）
- `feat:` 新功能
- `fix:` 缺陷修复
- `docs:` 文档
- `test:` 测试
- `refactor:` 重构
- `chore:` 工程杂项
- `ci:` GitHub Actions 或自动化维护
- `security:` 隐私、安全或依赖审计相关修复

## 5. 版本发布（Tag / Release）
```bash
git tag -a v0.1.0 -m "M1 minimal runnable"
git push origin v0.1.0
```
在 GitHub Releases 填写里程碑变更说明。

## 6. CI（GitHub Actions）
当前仓库维护两类 workflow：

- `CI`：安装依赖，运行 `./scripts/verify_delivery.sh`，并生成安全交付包 artifact。
- `Security Audit`：审计后端依赖、前端生产依赖，并重新执行交付包隐私审计。

本地提交前建议至少运行：

```bash
./scripts/verify_delivery.sh
./scripts/package_release.sh
```

## 7. 安全检查（必须）
严禁提交 `.env`、密钥、私有数据。提交前执行：
```bash
git status
git diff --name-only --cached
rg -n "DEEPSEEK_API_KEY|SECRET_KEY|BEGIN PRIVATE KEY|password" .
```

## 8. 大文件建议
- `sample_data/` 仅存放公开模拟数据
- 超大文件建议 Git LFS（默认不启用）

## 9. Issue 与 PR 维护节奏
- 小缺陷、文档缺口和后续优化先开 issue，标题保持具体，例如 `[Docs] 补充 Windows Python 3.12 部署说明`。
- 涉及源码、依赖、CI 或公开文档的改动通过 pull request 合并，不直接在 `main` 堆叠不可审查变更。
- UI 截图只能使用演示数据库或占位数据，不能出现真实学生、真实成绩、真实大纲或 API Key。
- 每周查看 Dependabot PR 和 Security Audit 结果，优先处理安全、隐私、安装失败和核心工作流回归。

## 10. 公开活跃度建议
- 用 issue 跟踪路线图中的 Near Term 项目，而不是只在本地记录。
- 每次修复后更新 `CHANGELOG.md`，让 GitHub 首页能看到连续维护痕迹。
- 发布可演示版本时创建 tag 和 GitHub Release，说明功能、验证命令和隐私边界。
