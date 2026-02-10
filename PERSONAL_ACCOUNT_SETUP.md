# 🔄 使用个人账号推送（不影响工作账号）

## 方案1: 使用HTTPS（最简单，推荐）

这个方法最简单，每次推送时选择使用哪个账号：

```bash
# 1. 仅在当前项目设置个人账号信息
git config --local user.name "jackchen1941"
git config --local user.email "your-personal-email@example.com"

# 2. 使用HTTPS URL
git remote set-url origin https://github.com/jackchen1941/knowledge_platform.git

# 3. 推送（会提示输入用户名和token）
git push -u origin main
# 用户名: jackchen1941
# 密码: 使用Personal Access Token
```

**获取Personal Access Token:**
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制token
5. 推送时用token作为密码

## 方案2: 使用SSH（配置后更方便）

### 步骤1: 生成个人账号专用SSH密钥

```bash
# 生成新密钥（不覆盖工作密钥）
ssh-keygen -t ed25519 -C "your-personal-email@example.com" -f ~/.ssh/id_ed25519_personal

# 添加到ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_personal

# 复制公钥
cat ~/.ssh/id_ed25519_personal.pub
```

### 步骤2: 添加公钥到GitHub个人账号

1. 复制上面的公钥内容
2. 访问: https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥，保存

### 步骤3: 配置SSH使用不同密钥

编辑或创建 `~/.ssh/config`:

```bash
# 工作账号（默认）
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519  # 或你的工作密钥

# 个人账号（使用别名）
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
```

### 步骤4: 配置当前项目

```bash
# 1. 仅在当前项目设置个人账号
git config --local user.name "jackchen1941"
git config --local user.email "your-personal-email@example.com"

# 2. 使用个人账号的SSH别名
git remote set-url origin git@github.com-personal:jackchen1941/knowledge_platform.git

# 3. 测试连接
ssh -T git@github.com-personal

# 4. 推送
git push -u origin main
```

## 方案3: 使用环境变量（临时切换）

```bash
# 1. 设置当前项目配置
git config --local user.name "jackchen1941"
git config --local user.email "your-personal-email@example.com"

# 2. 临时指定SSH密钥
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_personal" git push -u origin main
```

## 验证配置

### 检查当前项目配置（不影响全局）
```bash
# 查看当前项目的Git配置
git config --local --list

# 查看全局配置（应该还是工作账号）
git config --global --list
```

### 检查SSH密钥
```bash
# 列出所有SSH密钥
ls -la ~/.ssh/

# 测试工作账号连接
ssh -T git@github.com

# 测试个人账号连接（如果配置了别名）
ssh -T git@github.com-personal
```

## 推荐方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| HTTPS | 最简单，无需配置SSH | 每次需要输入token | ⭐⭐⭐⭐⭐ |
| SSH配置 | 配置后很方便 | 初次配置稍复杂 | ⭐⭐⭐⭐ |
| 环境变量 | 灵活 | 每次都要设置 | ⭐⭐⭐ |

## 我的推荐

**对于这个项目，使用HTTPS方式最简单：**

```bash
# 一次性配置
git config --local user.name "jackchen1941"
git config --local user.email "your-personal-email@example.com"
git remote set-url origin https://github.com/jackchen1941/knowledge_platform.git

# 推送
git push -u origin main
```

这样：
- ✅ 不影响其他项目的工作账号
- ✅ 配置简单，立即可用
- ✅ 安全可靠
- ✅ 以后在这个项目中的所有操作都自动使用个人账号

## 常见问题

### Q: 这会影响我的工作项目吗？
A: 不会！使用 `--local` 参数的配置只对当前项目有效。

### Q: 如何切换回工作账号？
A: 在其他项目中，Git会自动使用全局配置（工作账号）。

### Q: 如何查看当前使用的是哪个账号？
```bash
git config user.name
git config user.email
```

### Q: Personal Access Token在哪里获取？
A: https://github.com/settings/tokens → Generate new token (classic) → 勾选repo权限

---

**总结**: 使用 `git config --local` 可以让你在不同项目中使用不同的GitHub账号，互不影响！