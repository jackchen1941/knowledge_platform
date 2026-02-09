# 🔧 Git 常见问题解决方案

## 📋 目录

1. [多账号管理问题](#多账号管理问题)
2. [SSH密钥冲突](#ssh密钥冲突)
3. [推送被拒绝问题](#推送被拒绝问题)
4. [Commit信息过长导致卡顿](#commit信息过长导致卡顿)
5. [最佳实践](#最佳实践)

---

## 🔐 多账号管理问题

### 问题描述
当你有多个GitHub账号（如工作账号和个人账号）时，可能会遇到推送到错误账号的问题。

**错误示例**:
```bash
ERROR: Permission to jackchen1941/knowledge_platform.git denied to jackchen19411.
fatal: Could not read from remote repository.
```

### 解决方案

#### 方法1: 使用HTTPS + 项目级配置（推荐）

**优点**: 简单、不影响其他项目、每个项目独立配置

```bash
# 1. 仅在当前项目设置账号信息（不影响全局）
git config --local user.name "your-personal-username"
git config --local user.email "your-personal-email@example.com"

# 2. 使用HTTPS URL
git remote set-url origin https://github.com/username/repository.git

# 3. 推送时输入对应账号的凭据
git push -u origin main
```

**获取Personal Access Token**:
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制token
5. 推送时使用token作为密码

#### 方法2: 使用SSH + 多密钥配置

**步骤1: 为不同账号生成不同的SSH密钥**

```bash
# 工作账号密钥（如果已有，跳过）
ssh-keygen -t ed25519 -C "work-email@company.com" -f ~/.ssh/id_ed25519_work

# 个人账号密钥
ssh-keygen -t ed25519 -C "personal-email@example.com" -f ~/.ssh/id_ed25519_personal
```

**步骤2: 添加密钥到ssh-agent**

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_work
ssh-add ~/.ssh/id_ed25519_personal
```

**步骤3: 配置SSH config文件**

编辑 `~/.ssh/config`:

```bash
# 工作账号（默认）
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes

# 个人账号（使用别名）
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
```

**步骤4: 在项目中使用对应的配置**

```bash
# 个人项目
git config --local user.name "personal-username"
git config --local user.email "personal-email@example.com"
git remote set-url origin git@github.com-personal:username/repository.git

# 工作项目（使用默认配置）
git config --local user.name "work-username"
git config --local user.email "work-email@company.com"
git remote set-url origin git@github.com:company/repository.git
```

**步骤5: 添加公钥到对应的GitHub账号**

```bash
# 复制工作账号公钥
cat ~/.ssh/id_ed25519_work.pub

# 复制个人账号公钥
cat ~/.ssh/id_ed25519_personal.pub
```

分别添加到对应的GitHub账号: Settings > SSH and GPG keys > New SSH key

#### 方法3: 使用环境变量（临时切换）

```bash
# 临时使用特定SSH密钥
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_personal" git push origin main
```

### 验证配置

```bash
# 查看当前项目配置
git config --local --list

# 查看全局配置
git config --global --list

# 测试SSH连接
ssh -T git@github.com
ssh -T git@github.com-personal
```

---

## 🚫 推送被拒绝问题

### 问题1: 本地落后于远程

**错误信息**:
```bash
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/username/repository.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart.
```

**原因**: 远程仓库有本地没有的提交（如GitHub自动创建的README）

**解决方案**:

```bash
# 方案1: 拉取并合并（推荐）
git pull origin main --allow-unrelated-histories

# 如果有冲突，解决后提交
git add .
git commit -m "Merge remote changes"
git push -u origin main

# 方案2: 强制推送（会覆盖远程内容，谨慎使用）
git push -u origin main --force
```

### 问题2: 分支保护规则

**错误信息**:
```bash
remote: error: GH006: Protected branch update failed
```

**解决方案**:
1. 检查分支保护规则: Settings > Branches
2. 临时禁用保护规则，或
3. 通过Pull Request方式合并

---

## 💬 Commit信息过长导致卡顿

### 问题描述
在某些IDE或终端中，使用过长的commit信息可能导致命令卡住。

**问题示例**:
```bash
git commit -m "很长很长的commit信息..."
# 终端卡住，无响应
```

### 解决方案

#### 方案1: 使用简短的commit信息

```bash
# 简短版本
git commit -m "Initial release v1.0.0"

# 或使用编辑器编写详细信息
git commit
# 会打开默认编辑器，可以写多行
```

#### 方案2: 使用commit模板

创建 `.gitmessage` 文件:
```
# 标题（不超过50字符）


# 详细描述（可选）


# 相关Issue（可选）

```

配置使用模板:
```bash
git config --global commit.template ~/.gitmessage
```

#### 方案3: 使用约定式提交

```bash
# 格式: <type>(<scope>): <subject>
git commit -m "feat(auth): add user authentication"
git commit -m "fix(api): resolve search pagination bug"
git commit -m "docs(readme): update installation guide"
```

**常用类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

---

## 🔑 SSH密钥冲突

### 问题描述
多个SSH密钥导致认证失败或使用错误的账号。

### 解决方案

#### 检查当前使用的密钥

```bash
# 查看已加载的密钥
ssh-add -l

# 测试连接并查看使用的账号
ssh -T git@github.com
```

#### 清理并重新配置

```bash
# 清除所有已加载的密钥
ssh-add -D

# 只添加需要的密钥
ssh-add ~/.ssh/id_ed25519_personal

# 测试连接
ssh -T git@github.com
```

#### 使用SSH配置文件管理

参考上面的"多账号管理"部分配置 `~/.ssh/config`

---

## 📚 最佳实践

### 1. 项目级配置优先

```bash
# 每个项目单独配置，不依赖全局配置
git config --local user.name "username"
git config --local user.email "email@example.com"
```

### 2. 使用有意义的commit信息

```bash
# 好的commit信息
git commit -m "Add user authentication with JWT"
git commit -m "Fix search pagination bug in knowledge list"

# 不好的commit信息
git commit -m "update"
git commit -m "fix bug"
```

### 3. 定期同步远程仓库

```bash
# 推送前先拉取
git pull origin main
git push origin main
```

### 4. 使用分支进行开发

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 开发完成后合并
git checkout main
git merge feature/new-feature
```

### 5. 保护敏感信息

```bash
# 使用.gitignore忽略敏感文件
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets/" >> .gitignore

# 检查是否意外提交了敏感信息
git log --all --full-history -- "*password*"
```

### 6. 定期备份重要分支

```bash
# 创建备份分支
git branch backup-main main

# 推送到远程
git push origin backup-main
```

---

## 🆘 快速参考

### 常用命令

```bash
# 查看配置
git config --list
git config --local --list
git config --global --list

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline -10

# 查看当前状态
git status

# 撤销未提交的更改
git checkout -- <file>
git reset --hard HEAD

# 修改最后一次commit
git commit --amend

# 查看差异
git diff
git diff --staged
```

### 紧急情况处理

```bash
# 撤销最后一次commit（保留更改）
git reset --soft HEAD~1

# 撤销最后一次commit（丢弃更改）
git reset --hard HEAD~1

# 恢复已删除的文件
git checkout HEAD -- <file>

# 清理未跟踪的文件
git clean -fd

# 暂存当前更改
git stash
git stash pop  # 恢复暂存
```

---

## 📞 获取帮助

### 官方资源
- Git官方文档: https://git-scm.com/doc
- GitHub文档: https://docs.github.com
- Pro Git书籍: https://git-scm.com/book/zh/v2

### 社区支持
- Stack Overflow: https://stackoverflow.com/questions/tagged/git
- GitHub Community: https://github.community

### 检查Git版本

```bash
git --version

# 更新Git（macOS）
brew upgrade git

# 更新Git（Ubuntu）
sudo apt update && sudo apt upgrade git
```

---

## 📝 总结

本文档涵盖了在使用Git和GitHub时最常见的问题和解决方案：

1. ✅ 多账号管理 - 使用项目级配置和SSH别名
2. ✅ 推送被拒绝 - 先拉取再推送，或使用force（谨慎）
3. ✅ Commit卡顿 - 使用简短的commit信息
4. ✅ SSH密钥冲突 - 配置SSH config文件
5. ✅ 最佳实践 - 项目级配置、有意义的commit、定期同步

记住：**遇到问题时，先查看错误信息，通常Git会给出有用的提示！**

---

**文档版本**: 1.0.0  
**最后更新**: 2024-02-09  
**维护者**: Knowledge Platform Team