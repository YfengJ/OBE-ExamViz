# 09 GitHub 工作流

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

## 5. 版本发布（Tag / Release）
```bash
git tag -a v0.1.0 -m "M1 minimal runnable"
git push origin v0.1.0
```
在 GitHub Releases 填写里程碑变更说明。

## 6. 可选 CI（GitHub Actions）
建议流程：
- 后端：`pytest`
- 前端：`npm ci && npm run build`

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
