# GitHub工作流与协作规范

## 1. 仓库初始化

### 1.1 本地仓库初始化
```bash
# 进入项目根目录
cd D:\repo

# 初始化Git仓库
git init

# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "chore: init project scaffold

- 创建项目目录结构
- 添加后端FastAPI基础框架
- 添加前端Vue 3基础框架
- 创建数据模型和API接口
- 添加示例数据和文档
- 配置部署环境

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

### 1.2 创建GitHub远程仓库
1. 登录GitHub账户
2. 点击"+"按钮，选择"New repository"
3. 填写仓库信息：
   - **Repository name**: obe-paper-analysis-system
   - **Description**: 基于OBE的期末试卷分析与成绩可视化系统
   - **Visibility**: Public (或Private根据需求)
   - **Initialize this repository with**: 不勾选任何选项

### 1.3 关联远程仓库
```bash
# 添加远程仓库地址
git remote add origin https://github.com/your-username/obe-paper-analysis-system.git

# 验证远程仓库
git remote -v

# 推送代码到远程仓库
git branch -M main
git push -u origin main
```

## 2. 分支策略

### 2.1 分支结构
```
main (主分支，稳定可演示版本)
├── dev (开发分支，日常开发)
│   ├── feature/obe-metrics (功能分支)
│   ├── feature/ai-integration (功能分支)
│   └── feature/export-report (功能分支)
└── release/v0.1.0 (发布分支)
```

### 2.2 分支创建与切换
```bash
# 从main创建dev分支
git checkout main
git checkout -b dev
git push -u origin dev

# 从dev创建功能分支
git checkout dev
git checkout -b feature/obe-metrics
git push -u origin feature/obe-metrics
```

## 3. 提交规范

### 3.1 提交消息格式
采用Conventional Commits规范：
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 3.2 提交类型
- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更新
- **test**: 测试相关
- **refactor**: 重构代码
- **chore**: 工程杂项
- **style**: 代码格式
- **perf**: 性能优化

### 3.3 提交示例
```bash
# 新功能提交
git commit -m "feat: add student management API

- 添加学生CRUD接口
- 添加学生查询接口
- 添加学生数据验证

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# Bug修复提交
git commit -m "fix: fix database connection issue

- 修复SQLite连接线程问题
- 添加连接池配置
- 优化错误处理

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# 文档更新提交
git commit -m "docs: update API documentation

- 更新学生管理API文档
- 添加请求参数说明
- 补充响应示例

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

## 4. 工作流程

### 4.1 功能开发流程
```bash
# 1. 切换到dev分支
git checkout dev
git pull origin dev

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发功能
# ... 编写代码 ...

# 4. 添加修改到暂存区
git add .

# 5. 提交修改
git commit -m "feat: implement your feature"

# 6. 推送到远程
git push -u origin feature/your-feature-name

# 7. 创建Pull Request
# 在GitHub网页上创建PR，从feature分支合并到dev分支
```

### 4.2 Bug修复流程
```bash
# 1. 从main创建hotfix分支
git checkout main
git checkout -b hotfix/fix-issue-name

# 2. 修复bug
# ... 修改代码 ...

# 3. 提交修复
git commit -m "fix: fix issue description"

# 4. 推送到远程
git push -u origin hotfix/fix-issue-name

# 5. 创建Pull Request
# 合并到main和dev分支
```

## 5. Pull Request规范

### 5.1 PR模板
创建`.github/PULL_REQUEST_TEMPLATE.md`：
```markdown
## 功能描述

[简要描述本次PR的功能]

## 变更内容

- [ ] 新增功能
- [ ] 修复bug
- [ ] 文档更新
- [ ] 代码重构

## 测试说明

[说明如何测试本次变更]

## 关联Issue

[关联的Issue编号]

## 截图

[如果有界面变更，请添加截图]

## 其他说明

[其他需要说明的信息]
```

### 5.2 PR创建要求
- **标题**: 清晰描述PR内容，采用Conventional Commits格式
- **描述**: 详细说明变更内容和原因
- **测试**: 确保所有测试通过
- **代码风格**: 符合项目代码规范
- **文档**: 更新相关文档

### 5.3 PR审查流程
1. **自动检查**: CI流水线自动运行测试和代码检查
2. **代码审查**: 至少1人审查通过
3. **讨论**: 解决审查中发现的问题
4. **合并**: 使用Squash Merge保持提交历史整洁

## 6. 代码审查规范

### 6.1 审查要点
- **功能正确性**: 代码实现是否符合需求
- **代码质量**: 代码结构、命名、注释
- **性能**: 是否存在性能问题
- **安全性**: 是否存在安全漏洞
- **测试**: 是否有足够的测试覆盖
- **可维护性**: 代码是否易于维护

### 6.2 审查评论规范
- **正面反馈**: 肯定好的实现
- **建设性建议**: 提出改进建议
- **明确指出问题**: 明确说明问题所在
- **提供解决方案**: 建议如何修复

## 7. 版本发布

### 7.1 版本号规范
采用Semantic Versioning：
- **MAJOR.MINOR.PATCH**
- **MAJOR**: 不兼容的API变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

### 7.2 发布流程
```bash
# 1. 切换到main分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 创建发布分支
git checkout -b release/v0.1.0

# 4. 更新版本号
# 修改backend/app/core/config.py中的VERSION
# 修改frontend/package.json中的version

# 5. 提交版本更新
git commit -m "chore: bump version to v0.1.0"

# 6. 推送到远程
git push -u origin release/v0.1.0

# 7. 创建标签
git tag -a v0.1.0 -m "M1 minimal runnable version"

# 8. 推送标签
git push origin v0.1.0

# 9. 创建Pull Request
# 合并release分支到main分支

# 10. 创建GitHub Release
# 在GitHub网页上创建Release，填写变更日志
```

### 7.3 发布说明模板
```markdown
## v0.1.0 (2026-02-24)

### 新增功能
- 学生管理功能
- 课程管理功能
- 考试管理功能
- 成绩分析功能
- 数据导入导出功能

### 改进
- 优化数据库查询性能
- 改进前端界面交互
- 增强错误处理

### 修复
- 修复数据库连接问题
- 修复文件上传漏洞
- 修复API认证问题

### 已知问题
- OBE达成度计算待完善
- AI分析功能待集成
- 性能优化待进行

### 升级说明
从v0.0.1升级到此版本需要执行数据库迁移：
```bash
alembic upgrade head
```

### 下载链接
- [源码下载](https://github.com/your-username/obe-paper-analysis-system/archive/v0.1.0.tar.gz)
- [Docker镜像](https://hub.docker.com/r/your-dockerhub-username/obe-backend/tags)
```

## 8. CI/CD配置

### 8.1 GitHub Actions配置
创建`.github/workflows/ci.yml`：
```yaml
name: CI

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.10]
        node-version: [18]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install backend dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black

    - name: Run backend lint
      run: |
        cd backend
        flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check app/

    - name: Run backend tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci

    - name: Run frontend lint
      run: |
        cd frontend
        npm run lint

    - name: Run frontend tests
      run: |
        cd frontend
        npm test

    - name: Build frontend
      run: |
        cd frontend
        npm run build

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### 8.2 自动部署配置
创建`.github/workflows/deploy.yml`：
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/obe-analysis
          git pull origin main
          docker-compose build
          docker-compose up -d
          docker image prune -f

    - name: Notify Deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
      if: always()
```

## 9. 敏感信息管理

### 9.1 敏感文件检查
```bash
# 检查是否意外提交了敏感文件
git grep -l "password\|secret\|key" --include="*.py" --include="*.env"

# 检查大文件
git rev-list --objects --all | grep $(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -5 | awk '{print$1}')

# 检查是否包含.env文件
git log --all -- .env
```

### 9.2 清理敏感文件
如果意外提交了敏感文件：
```bash
# 使用BFG Repo-Cleaner或git filter-branch
# 1. 安装BFG
# 2. 清理历史记录
bfg --delete-files .env

# 3. 强制推送
git push --force
```

### 9.3 GitHub Secrets配置
在GitHub仓库设置中添加以下Secrets：
- `SERVER_HOST`: 服务器地址
- `SERVER_USER`: 服务器用户名
- `SSH_KEY`: SSH私钥
- `SLACK_WEBHOOK`: Slack Webhook URL
- `CODECOV_TOKEN`: Codecov Token

## 10. Git Hooks配置

### 10.1 预提交钩子
创建`.git/hooks/pre-commit`：
```bash
#!/bin/sh

# 运行代码检查
echo "Running pre-commit checks..."

# 检查Python代码格式
cd backend
python -m flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
if [ $? -ne 0 ]; then
    echo "Python code style check failed"
    exit 1
fi

# 检查前端代码格式
cd ../frontend
npm run lint
if [ $? -ne 0 ]; then
    echo "Frontend code style check failed"
    exit 1
fi

echo "All checks passed!"
```

### 10.2 提交消息钩子
创建`.git/hooks/commit-msg`：
```bash
#!/bin/sh

# 验证提交消息格式
commit_regex='^(feat|fix|docs|test|refactor|chore|style|perf)(\([a-z]+\))?: .{10,}'
error_msg="提交消息格式不正确！请使用以下格式：
<type>[optional scope]: <description>

例如：
feat: add new feature
fix: fix bug
docs: update documentation"

if ! grep -qE "$commit_regex" "$1"; then
    echo "$error_msg"
    exit 1
fi
```

## 11. 协作工具

### 11.1 Issue管理
使用GitHub Issues进行任务跟踪：
- **任务类型**: Feature, Bug, Enhancement, Task
- **优先级**: High, Medium, Low
- **状态**: To Do, In Progress, Done
- **标签**: 按模块、功能、优先级标记

### 11.2 Project看板
创建GitHub Project看板：
- **Backlog**: 待处理任务
- **In Progress**: 进行中任务
- **Review**: 待审查任务
- **Done**: 已完成任务

### 11.3 代码审查工具
- **Reviewable**: 代码审查工具
- **PullRequest**: PR管理工具
- **Codecov**: 代码覆盖率检查

## 12. 文档维护

### 12.1 文档更新流程
```bash
# 1. 创建文档分支
git checkout -b docs/update-readme

# 2. 更新文档
# ... 编辑文档 ...

# 3. 提交更新
git commit -m "docs: update README with new features"

# 4. 推送并创建PR
git push -u origin docs/update-readme
# 创建PR合并到main分支
```

### 12.2 文档版本控制
- 文档与代码同步更新
- 重要变更及时更新文档
- 保留历史版本记录

## 13. 问题排查

### 13.1 常见问题
```bash
# 1. 远程仓库连接问题
ssh -T git@github.com  # 测试SSH连接
https://github.com     # 测试HTTPS连接

# 2. 权限问题
git remote set-url origin git@github.com:user/repo.git  # 改用SSH
git remote set-url origin https://github.com/user/repo.git  # 改用HTTPS

# 3. 大文件问题
git filter-branch --tree-filter 'rm -f large-file' HEAD

# 4. 合并冲突
git status  # 查看冲突文件
# 手动解决冲突
git add .
git commit
```

### 13.2 最佳实践
- 频繁拉取最新代码，避免大规模冲突
- 小颗粒度提交，便于问题定位
- 清晰的提交消息，便于历史追溯
- 定期同步主分支，保持分支最新

## 14. 命令速查表

### 14.1 日常命令
```bash
# 拉取最新代码
git pull origin main

# 查看状态
git status

# 添加修改
git add .

# 提交修改
git commit -m "message"

# 推送到远程
git push origin branch-name

# 查看日志
git log --oneline --graph

# 查看分支
git branch -a

# 切换分支
git checkout branch-name

# 创建分支
git checkout -b branch-name

# 删除分支
git branch -d branch-name
git push origin --delete branch-name

# 暂存修改
git stash

# 恢复暂存
git stash pop
```

### 14.2 高级命令
```bash
# 撤销提交
git reset --soft HEAD~1

# 修改提交消息
git commit --amend

# 合并多个提交
git rebase -i HEAD~5

# 查看文件修改
git diff

# 查看某人提交的代码
git blame file-name

# 查看某行代码历史
git log -L start,end:file-name

# 恢复删除的文件
git checkout commit-hash -- file-name

# 查找包含某字符串的提交
git log -S "search-string"
```

## 15. 协作规范总结

### 15.1 基本原则
- 代码风格统一
- 提交信息规范
- 测试覆盖率达标
- 文档及时更新
- 审查流程严格执行

### 15.2 质量要求
- 新功能必须有测试
- Bug修复必须有复现步骤
- 性能变更必须有基准测试
- 安全变更必须有安全评估

### 15.3 沟通协作
- 及时响应PR审查
- 主动报告进度
- 遇到问题及时求助
- 分享技术经验

---

*本规范最后更新：2026年2月24日*